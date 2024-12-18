import threading
import traceback

import torch

import comfy.model_management
from core.abstracts import Addon, Comp
from core.abstracts.cache import OutputsCache
from core.abstracts.func import Func, FuncInput
from core.abstracts.card import Card
from data_type.whatsai_card import CardDataModel, Prompt
from misc.helpers import get_now_timestamp_and_str
from data_type.whatsai_task import Task
from data_type.whatsai_task import TaskStatus
from misc.logger import logger


# frontend uses loop instead of socket, so it's not import here, maybe socket is a better way though.
class EventTypes:
    TASK_START = 1
    TASK_PROCESSING = 2
    TASK_CANCELED = 3

    TASK_FAILED = 8
    TASK_FINISHED = 9

    PREVIEW_IMAGE = 11
    UNENCODED_PREVIEW_IMAGE = 12


class TaskQueue:
    """ Used to put prompt by frontend, get by prompt worker to generate.
        Mostly from ComfyUI, thanks.
    """

    mutex = threading.RLock()
    not_empty = threading.Condition(mutex)
    queue = []

    @classmethod
    def put(cls, card_name: str, prompt: Prompt, client_id: str):
        with cls.mutex:
            created_time_stamp, created_datetime_str = get_now_timestamp_and_str()
            task = Task(
                client_id=client_id,
                status=TaskStatus.queued.value,
                card_name=card_name,
                prompt=prompt,
                created_time_stamp=created_time_stamp,
                created_datetime_str=created_datetime_str
            )
            task.save()
            task_dict = task.model_dump()
            cls.queue.append(task_dict)
            cls.not_empty.notify()

    @classmethod
    def put_task(cls, task: Task):
        with cls.mutex:
            task_dict = task.model_dump()
            cls.queue.append(task_dict)
            cls.not_empty.notify()

    @classmethod
    def get(cls, timeout=1):
        with cls.not_empty:
            while len(cls.queue) == 0:
                cls.not_empty.wait(timeout=timeout)
                if len(cls.queue) == 0:
                    return None
            task_dict = cls.queue.pop(0)
            task = Task(**task_dict)
            return task


class PromptWorker:
    """ The prompt worker which do the generation work, sync generation info to frontend by websocket.
        Mostly from ComfyUI, thanks.
    """

    loop = None
    cached_outputs: OutputsCache = OutputsCache()

    old_prompt: Prompt = None
    old_card: Card | None = None

    last_result = None

    @classmethod
    def run(cls, loop):
        cls.loop = loop
        logger.debug("PromptWorker start to run.")

        try:
            unfinished_tasks = Task.get_undone_tasks()
            for t in unfinished_tasks:
                TaskQueue.put_task(t)
            logger.info(f"Recover prompt tasks {len(unfinished_tasks)}")
        except Exception as e:
            traceback.print_exc()

        while True:
            task = TaskQueue.get()
            if not task:
                continue
            cls.process_prompt(task)

    @classmethod
    def process_prompt(cls, task: Task):
        logger.debug(f"start processing prompt task {task.id} {task.card_name}")
        cls.start_task(task)

        card_name = task.card_name

        card_class = cls.get_card_class(card_name)
        if not card_class:
            cls.fail_task(task, 'Card: {} not found'.format(card_name))
            return
        card = card_class()

        cls.execute_card(card, task)

    @classmethod
    def execute_card(cls, card: Card, task: Task):
        prompt = task.prompt
        base_inputs = prompt.base_inputs
        addon_inputs = prompt.addon_inputs

        try:
            logger.debug(f"addon_inputs: {addon_inputs}")
            addon_valid_errors = card.create_addons(addon_inputs)
            logger.debug(f"Func list after created addon: {[func.name for func in card.func_list]}")
            base_inputs_valid_errors = card.make_type_right_and_valid_inputs(base_inputs)

            if addon_valid_errors or base_inputs_valid_errors:
                addon_valid_errors.extend(base_inputs_valid_errors)
                cls.fail_task(task, f"Inputs Error:{addon_valid_errors}")
                return

            with torch.inference_mode():
                logger.debug(f"loaded models: {comfy.model_management.current_loaded_models}")

                card.set_prompt(prompt)
                cls.set_k_samplers_callback_of_card(card, task)

                to_deletes = cls.delete_outputs_if_changed(card, prompt)
                logger.debug(f'to_deletes: {to_deletes}')
                to_executes = cls.calculate_to_executes(card, to_deletes)
                logger.debug(f'to_executes:{[func.name for func in to_executes]}')

                if not to_executes:
                    cls.finish_task(task, cls.last_result)
                    return

                # Notice: card only support single result output now, so any func of the card changed, the result should change.
                for index, func in enumerate(to_executes):
                    is_last = index == len(to_executes) - 1
                    if is_last:
                        cls.last_result = cls.execute_func(func, prompt, card)
                        cls.old_prompt = prompt
                        cls.old_card = card

                        cls.finish_task(task, cls.last_result)
                        logger.debug(f"results: {cls.last_result}")
                    else:
                        _ = cls.execute_func(func, prompt, card)

        except Exception as e:
            logger.debug(e)
            traceback.print_exc()
            cls.fail_task(task, str(e))

    @classmethod
    def execute_func(cls, func: Func, prompt: Prompt, card: Card):
        if isinstance(func, Addon):
            func_outputs = func.execute(prompt.addon_inputs, cls.cached_outputs, card, func.name)
        else:
            func_outputs = func.execute(prompt.base_inputs, cls.cached_outputs, card, func.name)

        cls.cached_outputs.cache_func_outputs(func.name, func.index, func_outputs)
        logger.debug(f"cached funcs: {list(cls.cached_outputs.cache.keys())} ")
        return func_outputs

    @classmethod
    def delete_outputs_if_changed(cls, card: Card, prompt: Prompt):
        to_deletes = []

        for func in card.func_list:
            if isinstance(func, Addon):
                is_widget_inputs_changed = cls.is_addon_inputs_changed(func, prompt.addon_inputs, card)
            elif isinstance(func, Comp):
                is_widget_inputs_changed = cls.is_comp_inputs_changed(func, prompt.base_inputs, card)
            else:
                is_widget_inputs_changed = False

            if is_widget_inputs_changed:
                is_changed = True
            else:
                is_changed = not cls.are_func_inputs_equal(func, card)

            if is_changed:
                to_deletes.append(func.name)
                func_successor_names = card.get_func_successors(func)
                to_deletes.extend(func_successor_names)
                if len(to_deletes) == len(card.func_list):
                    break

        func_names = [func.name for func in card.func_list]
        for cached_func in cls.cached_outputs.cached_keys():
            if cached_func not in func_names:
                to_deletes.append(cached_func)

        to_deletes = set(to_deletes)
        for to_delete in to_deletes:
            cls.cached_outputs.clear_func_outputs(to_delete)

        logger.debug(
            f"Models before clean: {[model.model.model.__class__.__name__ for model in comfy.model_management.current_loaded_models]}")
        comfy.model_management.cleanup_models(keep_clone_weights_loaded=True)
        logger.debug(
            f"Models after clean: {[model.model.model.__class__.__name__ for model in comfy.model_management.current_loaded_models]}")
        return to_deletes

    @classmethod
    def calculate_to_executes(cls, card, to_deletes):
        to_executes = []
        for func in card.func_list:
            if func.name not in cls.cached_outputs.cached_keys():
                to_executes.append(func)
        return to_executes

    @classmethod
    def is_comp_inputs_changed(cls, comp: Comp, inputs, card):
        if not cls.old_prompt:
            return True

        widget_input_names = comp.widgets.keys()
        is_equals = []

        for input_name in widget_input_names:
            old_input = cls.old_prompt.base_inputs.get(input_name)
            input_ = inputs.get(input_name)
            is_equals.append(old_input == input_)

        return not all(is_equals)

    @classmethod
    def is_addon_inputs_changed(cls, addon: Addon, addon_inputs, card):
        if not cls.old_prompt:
            return True

        addon_name = addon.name
        this_addon_inputs = addon_inputs.get(addon_name, [])
        old_addon_inputs = cls.old_prompt.addon_inputs.get(addon_name, [])

        if len(this_addon_inputs) != len(old_addon_inputs):
            return True

        is_equals = []
        for input_dict, old_input_dict in zip(this_addon_inputs, old_addon_inputs):
            if input_dict.keys() == old_input_dict.keys():
                if all(old_input_dict[key] == old_input_dict[key] for key in input_dict):
                    is_equals.append(True)
                else:
                    is_equals.append(False)
            else:
                is_equals.append(False)

        return not all(is_equals)

    @classmethod
    def are_func_inputs_equal(cls, func: Func, card):
        """ Check if inputs from other funcs are equal. """

        if not cls.old_card:
            return False

        old_func = cls.old_card.get_func(func.name)
        if not old_func:
            return False

        def is_func_input_equal(func_input: FuncInput, old_func_input: FuncInput):
            output_pos = func_input.link.frm.pos if func_input.link else None
            old_output_pos = old_func_input.link.frm.pos if old_func_input.link else None
            if not output_pos and not old_output_pos:
                return True

            if (not output_pos and old_output_pos) or (output_pos and not old_output_pos):
                return False

            func_name, func_index, param_name = card.map_pos_to_func_and_io_names(output_pos)
            old_func_name, old_func_index, old_param_name = cls.old_card.map_pos_to_func_and_io_names(old_output_pos)
            is_output_equal = (func_name == old_func_name
                               and func_index == old_func_index
                               and param_name == old_param_name
                               )
            return is_output_equal

        is_equals = []
        for input_ in func.inputs.values():
            old_input = old_func.inputs.get(input_.name)
            if not old_input:
                is_equals.append(False)
            is_equal = is_func_input_equal(input_, old_input)
            is_equals.append(is_equal)

        return all(is_equals)

    @classmethod
    def set_k_samplers_callback_of_card(cls, card, task):
        k_samplers = card.get_ksampler_funcs()

        def callback(step, total_steps, preview_bytes):
            cls.preview_task(task, info={
                'step': step,
                'total_steps': total_steps,
                'preview_bytes': preview_bytes
            })

        for k_sampler in k_samplers:
            k_sampler.set_callback(callback)

    @classmethod
    def start_task(cls, task: Task):
        task.status = TaskStatus.processing.value
        task.save()

    @classmethod
    def preview_task(cls, task: Task, info: dict):
        task.preview_info = info
        task.save()

    @classmethod
    def fail_task(cls, task: Task, reason: str):
        task.info = reason
        task.status = TaskStatus.failed.value
        task.save()

    @classmethod
    def finish_task(cls, task: Task, results: dict):
        task.outputs = results
        task.preview_info = None
        task.status = TaskStatus.done.value
        task.save()

    @classmethod
    def get_card_class(cls, card_name: str):
        return CardDataModel.get_card_class(card_name)
