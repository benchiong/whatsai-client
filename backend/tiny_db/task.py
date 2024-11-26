from datetime import datetime
from enum import Enum
from typing import Optional

from aiotinydb import AIOTinyDB
from tinydb import TinyDB, Query

from data_type.base import PydanticModel
from misc.whatsai_dirs import db_path_dir
from tiny_db.prompt import Prompt
from tiny_db.base_table import BaseTable


class TaskStatus(Enum):
    queued = 1
    processing = 2
    canceled = 3
    failed = 4
    finished = 5


class Task(BaseTable):
    table_name = db_path_dir / 'task.json'

    class DataModel(PydanticModel):
        task_id: Optional[int] = None  # take doc_id in tinydb as task_id, filled after saved into tinydb.

        client_id: str
        status: int
        prompt: Prompt
        outputs: Optional[dict] = None
        preview_info: Optional[dict] = None
        created_time_stamp: Optional[int] = None
        created_datetime_str: Optional[str] = None

    @classmethod
    def add_task(cls,
                 client_id: str,
                 prompt: Prompt,
                 status: int = TaskStatus.queued.value,
                 created_time_stamp=None,
                 created_datetime_str=None
                 ):
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
        async with AIOTinyDB(cls.table_name) as db:
            db.remove(doc_ids=[task_id])

    @classmethod
    async def get_tasks(cls, status: TaskStatus | None):
        async with AIOTinyDB(cls.table_name) as db:
            if status is None:
                results = db.all()
            else:
                Q = Query()
                results = db.search(Q.status == status.value)

            return sorted(results, key=lambda r: r.get('created_time_stamp'), reverse=True)
