import heapq
import struct
import threading
import traceback
from io import BytesIO

from PIL import Image, ImageOps

from tiny_db.prompt import Prompt
from tiny_db.task import TaskStatus, Task
from tiny_db.card_info import CardModelTable
from misc.logger import logger
from misc.websocket_manager import WebsocketManager


class TaskQueue:
    """ Used to put prompt by frontend, get by prompt worker to generate.
        Mostly from ComfyUI, thanks.
    """

    mutex = threading.RLock()
    not_empty = threading.Condition(mutex)
    queue = []

    @classmethod
    def put(cls, prompt: Prompt, client_id: str):
        with cls.mutex:
            task_dict = Task.add_task(client_id, prompt)
            # heapq.heappush(cls.queue, task_dict)
            cls.queue.append(task_dict)
            cls.not_empty.notify()

    @classmethod
    def get(cls, timeout=1):
        with cls.not_empty:
            while len(cls.queue) == 0:
                cls.not_empty.wait(timeout=timeout)
                if len(cls.queue) == 0:
                    return None
            # task_dict = heapq.heappop(cls.queue)
            task_dict = cls.queue.pop(0)
            Task.update_task_status(task_dict.get('task_id'), TaskStatus.processing)
            return task_dict

class EventTypes:
    TASK_START = 1
    TASK_PROCESSING = 2
    TASK_CANCELED = 3

    TASK_FAILED = 8
    TASK_FINISHED = 9

    PREVIEW_IMAGE = 11
    UNENCODED_PREVIEW_IMAGE = 12

class PromptWorker:
    """ The prompt worker which do the generation work, sync generation info to frontend by websocket.
        Mostly from ComfyUI, thanks.
    """

    cached_card = None
    """ Very simple card cache here. """

    loop = None

    @classmethod
    def run(cls, loop):
        cls.loop = loop
        logger.debug("PromptWorker start to run.")
        while True:
            task_dict = TaskQueue.get()
            if not task_dict:
                continue
            task = Task.DataModel(**task_dict)
            logger.debug(task)
            cls.process_prompt(task)

    @classmethod
    def process_prompt(cls, task: Task.DataModel):
        cls.start_task(task)

        card_name = task.prompt.card_name
        base_inputs = task.prompt.base_inputs
        addon_inputs = task.prompt.addon_inputs

        if cls.is_card_cached(card_name):
            card = cls.cached_card
        else:
            card_class = cls.get_card_class(card_name)
            if not card_class:
                cls.fail_task(task, 'Card: {} not found'.format(card_name))
                return
            card = card_class()

        #todo: set other type callbacks here.
        def sd_progress_callback(*args):
            step, total_steps, preview_bytes = args
            # logger.debug((step, total_steps))
            cls.preview_task(task, info={
                'step': step,
                'total_steps': total_steps,
                'preview_bytes': preview_bytes
            })

        card.register_progress_callback('sd_progress_callback', sd_progress_callback)
        card.register_progress_callback('sd_hires_fix_callback', sd_progress_callback)

        cls.cached_card = card
        try:
            results = card(base_inputs=base_inputs, addon_inputs=addon_inputs)
            cls.finish_task(task, results)
            logger.debug(results)
        except Exception as e:
            logger.debug(e)
            traceback.print_exc()
            cls.fail_task(task, str(e))

    @classmethod
    def start_task(cls, task: Task.DataModel):
        cls.send_sync(
            event=EventTypes.TASK_START,
            data=task.model_dump(),
            client_id=task.client_id
        )

        with TaskQueue.mutex:
            Task.update_task_status(task_id=task.task_id, status=TaskStatus.processing)
    @classmethod
    def preview_task(cls, task: Task.DataModel, info: dict):
        cls.send_sync(
            event=EventTypes.TASK_PROCESSING,
            data={
                **task.model_dump(),
                **info
            },
            client_id=task.client_id
        )
        with TaskQueue.mutex:
            Task.update_task_status(task_id=task.task_id, status=TaskStatus.processing, preview_info=info)

    @classmethod
    def fail_task(cls, task: Task.DataModel, reason: str):
        data = {
            **task.model_dump(),
            'reason': reason,
            'status': TaskStatus.failed.value
        }
        cls.send_sync(
            event=EventTypes.TASK_FAILED,
            data=data,
            client_id=task.client_id
        )

        with TaskQueue.mutex:
            Task.update_task_status(task_id=task.task_id, status=TaskStatus.failed)

    @classmethod
    def finish_task(cls, task: Task.DataModel, results: dict):
        data = {
            **task.model_dump(),
            'outputs': results,
            'status': TaskStatus.finished.value
        }
        cls.send_sync(
            event=EventTypes.TASK_FINISHED,
            data=data,
            client_id=task.client_id
        )

        with TaskQueue.mutex:
            Task.update_task_status(task_id=task.task_id, status=TaskStatus.finished, outputs=results)

    @classmethod
    def is_card_cached(cls, card_name: str):
        if not cls.cached_card:
            return False

        cached_card_name = cls.cached_card.name
        return cached_card_name and cached_card_name == card_name

    @classmethod
    def get_card_class(cls, card_name: str):
        return CardModelTable.get_card_class(card_name)

    @classmethod
    async def send(cls, event, data, client_id=None):
        if event == EventTypes.UNENCODED_PREVIEW_IMAGE:
            await cls.send_image(data, client_id)
        elif isinstance(data, (bytes, bytearray)):
            await cls.send_bytes(event, data, client_id)
        else:
            await cls.send_json(event, data, client_id)

    @classmethod
    def encode_bytes(cls, event, data):
        if not isinstance(event, int):
            raise RuntimeError(f"Binary event types must be integers, got {event}")

        packed = struct.pack(">I", event)
        message = bytearray(packed)
        message.extend(data)
        return message

    @classmethod
    async def send_image(cls, image_data, client_id=None):
        image_type = image_data[0]
        image = image_data[1]
        max_size = image_data[2]
        if max_size is not None:
            if hasattr(Image, 'Resampling'):
                resampling = Image.Resampling.BILINEAR
            else:
                resampling = Image.ANTIALIAS

            image = ImageOps.contain(image, (max_size, max_size), resampling)

        type_num = 1
        if image_type == "JPEG":
            type_num = 1
        elif image_type == "PNG":
            type_num = 2

        bytesIO = BytesIO()
        header = struct.pack(">I", type_num)
        bytesIO.write(header)
        image.save(bytesIO, format=image_type, quality=95, compress_level=1)
        preview_bytes = bytesIO.getvalue()
        await cls.send_bytes(EventTypes.PREVIEW_IMAGE, preview_bytes, client_id=client_id)

    @classmethod
    async def send_bytes(cls, event, data, client_id=None):
        message = cls.encode_bytes(event, data)
        await WebsocketManager.send_message(
            message=message,
            message_type='bytes',
            websocket=None,
            client_id=client_id
        )

    @classmethod
    async def send_json(cls, event, data, client_id=None):
        message = {"type": event, "data": data}
        await WebsocketManager.send_message(
            message=message,
            message_type='json',
            websocket=None,
            client_id=client_id
        )

    @classmethod
    def send_sync(cls, event, data, client_id=None):
        cls.loop.run_until_complete(cls.send(event, data, client_id))




