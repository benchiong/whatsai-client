import json
from contextlib import closing
from pathlib import Path
from typing import Optional

from data_type.base_data_model import PyDBModel
from data_type.whatsai_model_info import ModelInfo


class ModelDownloadingInfo(PyDBModel):
    url: str
    model_info: ModelInfo
    total_size: float

    downloaded_size: float = 0.0
    downloaded_time: float = 0.0

    progress: float = 0.0
    eta:  Optional[float] = None

    finished: bool = False

    @classmethod
    def init(cls):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                """CREATE TABLE IF NOT EXISTS model_downloading_info
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT,
                        model_info TEXT,
                        total_size REAL,
                        downloaded_size REAL,
                        downloaded_time REAL,
                        progress REAL,
                        eta REAL,
                        finished INTEGER
                        )"""
            )
            cur.execute("CREATE INDEX IF NOT EXISTS model_downloading_info_url ON model_downloading_info(url)")

            conn.commit()

    def save(self):
        conn = self.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                """ INSERT OR REPLACE INTO model_downloading_info 
                    (
                        id, url, model_info, total_size, downloaded_size,
                        downloaded_time, progress, eta, finished
                    
                    ) VALUES (
                        ?, ?, ?, ?, ?,
                        ?, ?, ?, ?
                    )
                     
                """,
                self.to_tuple(with_id=True),
            )
            if not self.id:
                self.id = cur.lastrowid
            conn.commit()

    def to_tuple(self, with_id=False):
        model_dict = self.model_dump()
        model_dict['model_info'] = json.dumps(model_dict.get('model_info', ''))
        # model_dict['finished'] =

        if with_id:
            return tuple(model_dict.values())
        else:
            model_dict.pop('id')
            return tuple(model_dict.values())

    def is_file_exists(self):
        return Path(self.model_info.local_path).exists()

    def downloading_file(self):
        return self.model_info.local_path + '.downloading'

    def is_downloading_file_exists(self):
        return Path(self.downloading_file()).exists()

    @classmethod
    def from_row(cls, row: tuple):
        model_downloading_info = cls(
            id=row[0],
            url=row[1],
            model_info=json.loads(row[2]),
            total_size=row[3],
            downloaded_size=row[4],
            downloaded_time=row[5],
            progress=row[6],
            eta=row[7],
            finished=bool(row[8])
        )
        return model_downloading_info

    @classmethod
    def get(cls, id_or_url):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                "SELECT * FROM model_downloading_info where id = ? or url = ?", (id_or_url, id_or_url)
            )
            row = cur.fetchone()
            if row is None:
                return None
            else:
                return cls.from_row(row)

    @classmethod
    def get_all(cls):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute("SELECT * FROM model_downloading_info")
            rows = cur.fetchall()
            return [cls.from_row(row) for row in rows]

    @classmethod
    def get_unfinished(cls):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute("SELECT * FROM model_downloading_info WHERE finished = 0")
            rows = cur.fetchall()
            return [cls.from_row(row) for row in rows]

    @classmethod
    def get_with_ids(cls, ids):

        query = """
                        SELECT * FROM model_downloading_info
                        WHERE id IN ({})
                    """.format(
            ",".join("?" * len(ids))
        )

        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(query, ids)
            rows = cur.fetchall()

        return [cls.from_row(row) for row in rows]

