import json
from contextlib import closing
from enum import Enum

from data_type.base_data_model import PyDBModel
from data_type.whatsai_model_downloading_info import ModelDownloadingInfo
from data_type.whatsai_model_info import ModelInfo
from misc.logger import logger


class TaskType(str, Enum):
    download_civitai_model = 'download_civitai_model'
    sync_civitai_model_info = 'sync_civitai_model_info'


class TaskStatus(str, Enum):
    queued = 'queued'
    processing = 'processing'
    done = 'done'
    failed = 'failed'
    canceled = 'canceled'


class ModelDownloadTask(PyDBModel):
    task_type: str
    task_status: str
    workload: ModelInfo | ModelDownloadingInfo

    @classmethod
    def init(cls):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                """CREATE TABLE IF NOT EXISTS model_download_task
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task_type TEXT,
                        task_status TEXT,
                        workload TEXT
                        )
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS model_download_task_idx_workload ON model_download_task(workload)")
            conn.commit()

    def save(self):
        conn = self.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                """
                INSERT OR REPLACE INTO model_download_task 
                (id, task_type, task_status, workload)
                VALUES 
                (?, ?, ?, ?)
                """,
                self.to_tuple(with_id=True),
            )
            if not self.id:
                self.id = cur.lastrowid
            conn.commit()

    def to_tuple(self, with_id=False):
        model_dict = self.model_dump()
        model_dict['workload'] = json.dumps(model_dict.get('workload', {}))

        if with_id:
            return tuple(model_dict.values())
        else:
            model_dict.pop('id')
            return tuple(model_dict.values())

    @classmethod
    def from_row(cls, row: tuple):
        workload = json.loads(row[3])
        task_type = row[1]
        if task_type == 'download_civitai_model':
            workload = ModelDownloadingInfo(**workload)
        elif task_type == 'sync_civitai_model_info':
            workload = ModelInfo(**workload)
        else:
            logger.error("Unknown workload", workload)
            workload = {}

        model_info = cls(
            id=row[0],
            task_type=row[1],
            task_status=row[2],
            workload=workload,
        )
        return model_info

    @classmethod
    def get(cls, id_or_workload):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                "SELECT * FROM model_download_task where id = ? or workload = ? ",
                (id_or_workload, id_or_workload)
            )
            row = cur.fetchone()
            if row is None:
                return None
            else:
                return cls.from_row(row)

    @classmethod
    def get_undone_tasks(cls):
        unfinished_status = ['queued', 'processing']

        query = """
                            SELECT * FROM model_download_task
                            WHERE task_status IN ({})
                        """.format(
            ",".join("?" * len(unfinished_status))
        )

        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(query, unfinished_status)
            rows = cur.fetchall()

        return [cls.from_row(row) for row in rows]

    @classmethod
    def get_downloading_model_info_in_tasks(cls):
        unfinished_status = ['queued', 'processing']
        query = """
                    SELECT * FROM model_download_task
                    WHERE task_status IN ({}) AND task_type = 'download_civitai_model'
                """.format(
            ",".join("?" * len(unfinished_status))
        )

        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(query, unfinished_status)
            rows = cur.fetchall()

        return [cls.from_row(row).workload for row in rows]
