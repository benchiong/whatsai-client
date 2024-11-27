import threading
from datetime import datetime

from aiotinydb import AIOTinyDB
from tinydb import TinyDB, Query

from data_type.whatsai_task import Task, TaskStatus
from misc.whatsai_dirs import db_path_dir
from data_type.whatsai_prompt import Prompt
from tiny_db.base_table import BaseTable


class TaskTable(BaseTable):
    table_name = db_path_dir / 'task.json'
    DataModel = Task
    mutex = threading.RLock()

    @classmethod
    def add_task(cls,
                 client_id: str,
                 prompt: Prompt,
                 status: int = TaskStatus.queued.value,
                 created_time_stamp=None,
                 created_datetime_str=None
                 ):
        with cls.mutex:
            now = datetime.now()
            task = cls.DataModel(
                client_id=client_id,
                status=status,
                prompt=prompt,
                created_time_stamp=created_time_stamp if created_time_stamp else int(now.timestamp()),
                created_datetime_str=created_datetime_str if created_datetime_str else now.strftime("%Y/%m/%d %H:%M:%S")
            )
            task_record = task.model_dump()

            db = TinyDB(cls.table_name)
            doc_id = db.insert(task_record)
            db.update({'task_id': doc_id}, doc_ids=[doc_id])

            task_record['task_id'] = doc_id
            return task_record

    @classmethod
    def update_task_status(cls, task_id, status: TaskStatus, outputs: dict = {}, preview_info: dict = {}):
        with cls.mutex:
            db = TinyDB(cls.table_name)

            if not outputs:
                to_update = {'status': status.value}
            else:
                to_update = {
                    'status': status.value,
                    'outputs': outputs
                }

            if preview_info:
                to_update = {
                    **to_update,
                    'preview_info': preview_info
                }

            if status == TaskStatus.finished:
                to_update = {
                    **to_update,
                    'preview_info': None
                }

            db.update(to_update, doc_ids=[task_id])

    @classmethod
    async def remove_task(cls, task_id):
        with cls.mutex:
            async with AIOTinyDB(cls.table_name) as db:
                db.remove(doc_ids=[task_id])

    @classmethod
    async def get_tasks(cls, status: TaskStatus | None):
        with cls.mutex:
            async with AIOTinyDB(cls.table_name) as db:
                if status is None:
                    results = db.all()
                else:
                    Q = Query()
                    results = db.search(Q.status == status.value)

                return sorted(results, key=lambda r: r.get('created_time_stamp'), reverse=True)
