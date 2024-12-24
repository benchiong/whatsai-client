import json
import threading
import traceback

from data_type.civitai_model_version import CivitaiModelVersion
from data_type.whatsai_model_download_task import ModelDownloadTask, TaskStatus, TaskType
from data_type.whatsai_model_downloading_info import ModelDownloadingInfo
from data_type.whatsai_model_info import ModelInfo
from misc.helpers import sync_gen_file_sha256, gen_file_sha256
from misc.helpers_civitai import sync_get_civitai_model_info_by_hash, \
    sync_download_civitai_image_to_whatsai_file_dir, sync_get_real_image_info, file_to_download_2_model_download_info, \
    download_civitai_model_worker, get_civitai_model_info_by_hash, download_civitai_image_to_whatsai_file_dir, \
    get_real_image_info
from misc.logger import logger


class ModelDownloadQueue:
    """ Use to download civitai model info or sync model info etc..
    """

    mutex = threading.RLock()
    not_empty = threading.Condition(mutex)
    queue = []

    @classmethod
    def put(cls, task: ModelDownloadTask):
        with cls.mutex:
            cls.queue.append(task.model_dump())
            cls.not_empty.notify()

    @classmethod
    def get(cls, timeout=1):
        with cls.not_empty:
            while len(cls.queue) == 0:
                cls.not_empty.wait(timeout=timeout)
                if len(cls.queue) == 0:
                    return None
            task_dict = cls.get_model_downloading_first()
            task = ModelDownloadTask(**task_dict)
            task.task_status = TaskStatus.processing.value
            task.save()
            return task

    @classmethod
    def get_model_downloading_first(cls):
        for task_dict in cls.queue:
            if task_dict.get('task_type') == 'download_civitai_model':
                cls.queue.remove(task_dict)
                return task_dict
        return cls.queue.pop(0)


class ModelDownloadWorker:
    loop = None

    @classmethod
    def run(cls, loop):
        cls.loop = loop
        logger.info("ModelDownloadWorker start to run.")

        try:
            unfinished_tasks = ModelDownloadTask.get_undone_tasks()
            for t in unfinished_tasks:
                ModelDownloadQueue.put(t)
            logger.info(f"Recover task {len(unfinished_tasks)}")
        except Exception as e:
            traceback.print_exc()

        while True:
            task = ModelDownloadQueue.get()
            if not task:
                continue
            loop.run_until_complete(cls.process_task(task))

    @classmethod
    async def process_task(cls, task: ModelDownloadTask):
        logger.info(f"Start to {task.task_type} task: {task.id} ")
        if task.task_type == TaskType.sync_civitai_model_info.value:
            await cls.process_sync_civitai_model_info_task(task)
        elif task.task_type == TaskType.download_civitai_model.value:
            await cls.process_download_civitai_model_task(task)
        else:
            task.task_status = TaskStatus.failed.value
            task.save()
            logger.info(f"Failed to process task because unknown task type: {task.id} {task.task_type}")
        logger.info(f"Finish to {task.task_type} task: {task.id} ")

    @classmethod
    async def process_sync_civitai_model_info_task(cls, task: ModelDownloadTask):
        try:
            model_info = task.workload
            if model_info.civit_info_synced:
                logger.info(f"model_info synced: {model_info.id}")
                task.task_status = TaskStatus.done.value
                task.save()
                return

            local_path = model_info.local_path

            # generate sha_256 of model file
            hash_str = await gen_file_sha256(local_path)

            # get civitai model version info with sha_256
            success, civitai_model_info_dict, error = await get_civitai_model_info_by_hash(hash_str)

            # info not found on civitai, task done.
            if success and not civitai_model_info_dict:
                model_info.sha_256 = hash_str
                model_info.civit_info_synced = True
                model_info.save()
                task.task_status = TaskStatus.done.value
                task.save()
                return

            # task failed.
            if not civitai_model_info_dict:
                if hash_str:
                    model_info.sha_256 = hash_str
                    model_info.save()
                cls.fail_sync_civitai_model_info_task(task, error)
                return

            civitai_model_info = CivitaiModelVersion(**civitai_model_info_dict)
            civitai_model_info.save()

            # download image from civitai
            images = civitai_model_info.images
            local_image_path = None
            if images:
                image_infos = [image.model_dump() for image in images]
                first_img_info = await get_real_image_info(image_infos)
                image_url = first_img_info.get('url')
                if image_url:
                    local_image_path = await download_civitai_image_to_whatsai_file_dir(image_url)

            # save model info in db
            model_info.sha_256 = hash_str
            model_info.image_path = local_image_path
            model_info.civit_model_version_id = civitai_model_info.id
            model_info.civit_info_synced = True
            model_info.base_model = civitai_model_info.baseModel
            model_info.download_url = civitai_model_info.downloadUrl
            model_info.save()
            task.task_status = TaskStatus.done.value
            task.save()

        except Exception as e:
            traceback.print_exc()
            cls.fail_sync_civitai_model_info_task(task, str(e))

    @classmethod
    def fail_sync_civitai_model_info_task(cls, task: ModelDownloadTask, reason: str):
        logger.error(f"Fail to process sync_civitai_model_info task: {task.id}, reason: {reason}")
        task.task_status = TaskStatus.failed.value
        task.save()

    # use to remember which model is download to avoid duplicate downloads
    downloading_models = []

    @classmethod
    async def process_download_civitai_model_task(cls, task: ModelDownloadTask):
        try:
            model_downloading_info = task.workload

            # file already downloaded
            if model_downloading_info.is_file_exists():
                task.task_status = TaskStatus.done.value
                task.save()
                return

            # Model is downloading, fail the new one
            if model_downloading_info.downloading_file() in cls.downloading_models:
                cls.fail_sync_civitai_model_info_task(
                    task,
                    f"model{model_downloading_info.downloading_file()} is downloading already."
                )
                return

            cls.downloading_models.append(model_downloading_info.downloading_file())
            t = threading.Thread(target=cls.download_civitai_model_task, args=(model_downloading_info, task),
                                 daemon=True)
            t.start()

        except Exception as e:
            traceback.print_exc()
            cls.fail_sync_civitai_model_info_task(task, str(e))

    @classmethod
    def download_civitai_model_task(cls, download_model_info: ModelDownloadingInfo, task: ModelDownloadTask):
        retry = 5
        while retry > 0:
            try:
                finished, local_model_path = download_civitai_model_worker(download_model_info, task)
                if finished:
                    logger.debug(f"model downloaded: {local_model_path}")

                    task.task_status = TaskStatus.done.value
                    task.save()

                    cls.downloading_models.remove(download_model_info.downloading_file())
                    return

                else:  # task canceled
                    cls.downloading_models.remove(download_model_info.downloading_file())
                    return

            except Exception as e:
                traceback.print_exc()
                logger.debug(f"download civitai model error: {e} retry: {6 - retry} ")
                retry -= 1

        cls.fail_sync_civitai_model_info_task(task, "Fail to download.")
        cls.downloading_models.remove(download_model_info.downloading_file())


def submit_model_info_sync_task(model_info: ModelInfo):
    if not model_info:
        return

    workload = json.dumps(model_info.model_dump())
    task_in_db = ModelDownloadTask.get(workload)
    if task_in_db and task_in_db.task_status == TaskStatus.queued.value:
        return

    task = ModelDownloadTask(
        task_type=TaskType.sync_civitai_model_info.value,
        task_status=TaskStatus.queued.value,
        workload=model_info
    )
    task.save()
    ModelDownloadQueue.put(task)


def submit_model_download_task(civitai_model_version, files_to_download, image_downloaded):
    # one civitai version may include multiple models to download, map every model to one task
    for file_to_download in files_to_download:
        downloading_model_info, error_info = file_to_download_2_model_download_info(
            file_to_download,
            civitai_model_version,
            image_downloaded
        )
        if downloading_model_info:
            task = ModelDownloadTask(
                task_type=TaskType.download_civitai_model.value,
                task_status=TaskStatus.queued.value,
                workload=downloading_model_info
            )
            task.save()
            ModelDownloadQueue.put(task)
        else:
            # todo: make file_to_download_2_model_download_info can not fail?
            pass
