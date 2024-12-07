import json
from contextlib import closing
from enum import Enum
from typing import Literal, Optional

from data_type.whatsai_card import Prompt
from data_type.base_data_model import PyDBModel
from misc.helpers import get_now_timestamp_and_str

ModelTypeLiteral = Literal['system', 'custom']
class TaskStatus(Enum):
    queued = 'queued'
    processing = 'processing'
    canceled = 'canceled'
    failed = 'failed'
    done = 'done'

class Task(PyDBModel):

    client_id: str
    status: str
    card_name: str
    prompt: Prompt
    outputs: Optional[dict] = None
    preview_info: Optional[dict] = None
    created_time_stamp: Optional[int] = None
    created_datetime_str: Optional[str] = None
    info: Optional[str] = None
    updated_time_stamp: Optional[int] = None
    updated_datetime_str: Optional[str] = None

    # redundant fields
    field0: Optional[str] = None
    field1: Optional[str] = None
    field2: Optional[str] = None
    field3: Optional[str] = None
    field4: Optional[str] = None

    @classmethod
    def init(cls):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                """CREATE TABLE IF NOT EXISTS prompt_task
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        client_id TEXT,
                        status TEXT,
                        card_name TEXT NOT NULL,
                        prompt TEXT,
                        outputs TEXT,
                        preview_info TEXT,
                        created_time_stamp TEXT,
                        created_datetime_str TEXT,
                        info TEXT,
                        updated_time_stamp TEXT,
                        updated_datetime_str TEXT,
                        field0 TEXT,
                        field1 TEXT,
                        field2 TEXT,
                        field3 TEXT,
                        field4 TEXT
                        )"""
            )
            cur.execute("CREATE INDEX IF NOT EXISTS prompt_task_idx_card_name ON prompt_task(card_name)")

            conn.commit()

    def save(self):
        if not self.updated_time_stamp:
            self.updated_time_stamp, self.updated_datetime_str = get_now_timestamp_and_str()

        conn = self.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                """ 
                    INSERT OR REPLACE INTO prompt_task 
                        (
                            id, client_id, status, card_name, prompt,
                            outputs, preview_info, created_time_stamp, created_datetime_str, info,
                            updated_time_stamp, updated_datetime_str,
                            field0, field1, field2, field3, field4
                        ) 
                    VALUES 
                        (
                            ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?,
                            ?, ?,
                            ?, ?, ?, ?, ?
                        )
                """,
                self.to_tuple(with_id=True),
            )
            if not self.id:
                self.id = cur.lastrowid
            conn.commit()

    def to_tuple(self, with_id=False):
        model_dict = self.model_dump()
        model_dict['prompt'] = json.dumps(model_dict.get('prompt', {}))
        model_dict['outputs'] = json.dumps(model_dict.get('outputs', {}))
        model_dict['preview_info'] = json.dumps(model_dict.get('preview_info', {}))

        if with_id:
            return tuple(model_dict.values())
        else:
            model_dict.pop('id')
            return tuple(model_dict.values())

    @classmethod
    def from_row(cls, row: tuple):
        prompt = json.loads(row[4])
        outputs = json.loads(row[5])
        preview_info = json.loads(row[6])

        model_info = cls(
            id=row[0],
            client_id=row[1],
            status=row[2],
            card_name=row[3],
            prompt=prompt,
            outputs=outputs,
            preview_info=preview_info,
            created_time_stamp=row[7],
            created_datetime_str=row[8],
            info=row[9],
            updated_time_stamp=row[10],
            updated_datetime_str=row[11],
            field0=row[12],
            field1=row[13],
            field2=row[14],
            field3=row[15],
            field4=row[16],

        )
        return model_info

    @classmethod
    def get(cls, id):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                " SELECT * FROM prompt_task where id = ? ", (id,)
            )
            row = cur.fetchone()
            if row is None:
                return None
            else:
                return cls.from_row(row)

    @classmethod
    def get_all(cls, limit=20):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                " SELECT * FROM prompt_task ORDER BY updated_time_stamp desc LIMIT ?", (limit,)
            )
            rows = cur.fetchall()
            return [cls.from_row(row) for row in rows]

    @classmethod
    def get_undone_tasks(cls):
        unfinished_status = ['queued', 'processing']

        query = """
                    SELECT * FROM prompt_task
                        WHERE status IN ({})
                """.format(
            ",".join("?" * len(unfinished_status))
        )

        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(query, unfinished_status)
            rows = cur.fetchall()

        return [cls.from_row(row) for row in rows]

    @classmethod
    def remove(cls, id):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                "DELETE FROM prompt_task WHERE id = ? ", (id)
            )
            conn.commit()
