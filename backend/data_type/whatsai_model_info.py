import json
from contextlib import closing
from typing import Optional
from pathlib import Path

from data_type.base_data_model import PyDBModel
from data_type.civitai_model_version import CivitaiModelVersion
from misc.helpers import get_file_size_in_kb, get_now_timestamp_and_str, get_file_created_timestamp_and_datetime


class ModelInfo(PyDBModel):
    local_path: str
    file_name: str

    # some data get from civitai is empty,
    # case: https://civitai.com/api/v1/models/618692   files[0]
    sha_256: Optional[str] = None
    model_type: str

    image_path: Optional[str] = None

    civit_model_version_id: Optional[int] = None
    civit_model: Optional[CivitaiModelVersion] = None

    size_kb: Optional[float] = 0
    created_time_stamp: Optional[int] = 0
    created_datetime_str: Optional[str] = ""

    order_num: Optional[int] = 0  # use to set order manually, not used yet.
    civit_info_synced: bool = False
    dir: Optional[str] = None
    base_model: Optional[str] = None
    download_url: Optional[str] = None

    @classmethod
    def create_table(cls):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                """CREATE TABLE IF NOT EXISTS model_info
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        local_path TEXT UNIQUE,
                        file_name TEXT,
                        sha_256 TEXT, 
                        model_type TEXT,
                        image_path TEXT,
                        civit_model_version_id INTEGER,
                        size_kb REAL,
                        created_time_stamp INTEGER,
                        created_datetime_str TEXT,
                        order_num INTEGER,
                        civit_info_synced INTEGER DEFAULT 0,
                        dir TEXT,
                        base_model TEXT,
                        download_url TEXT,
                        FOREIGN KEY (civit_model_version_id) REFERENCES civit_model_version(id)
                        )
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS model_info_idx_sha_256 ON model_info(sha_256)")
            cur.execute("CREATE INDEX IF NOT EXISTS model_info_idx_file_name ON model_info(file_name)")
            cur.execute("CREATE INDEX IF NOT EXISTS model_info_idx_local_path ON model_info(local_path)")
            cur.execute("CREATE INDEX IF NOT EXISTS model_info_idx_download_url ON model_info(download_url)")

            conn.commit()

    @classmethod
    def init(cls):
        cls.create_table()

    def save(self):
        conn = self.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                """
                INSERT OR REPLACE INTO model_info 
                (
                    id, local_path, file_name, sha_256, model_type, 
                    image_path, civit_model_version_id, size_kb, created_time_stamp, 
                    created_datetime_str, order_num, civit_info_synced, dir, base_model, download_url
                )
                VALUES (
                    ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?
                )
                """,
                self.to_tuple(with_id=True),
            )
            if not self.id:
                self.id = cur.lastrowid
            conn.commit()
    @classmethod
    def get(cls, id_or_file_name_or_hash_or_file_path, with_civitai_model_info=False):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                """SELECT * FROM model_info where 
                    id = ? 
                    or file_name = ? 
                    or sha_256 = ? 
                    or local_path = ?
                    or download_url = ?
                """,
                (
                    id_or_file_name_or_hash_or_file_path,
                    id_or_file_name_or_hash_or_file_path,
                    id_or_file_name_or_hash_or_file_path,
                    id_or_file_name_or_hash_or_file_path,
                    id_or_file_name_or_hash_or_file_path
                 )
            )
            row = cur.fetchone()
            if row is None:
                return None
            else:
                if with_civitai_model_info:
                    civit_model_info = CivitaiModelVersion.get(row[6])
                else:
                    civit_model_info = None
                return cls.from_row(row, civit_model_info)

    @classmethod
    def add_with_local_path(cls, local_path, model_type):
        success, error_info, obj = cls.from_local_path_and_model_type(local_path, model_type)
        if obj:
            obj.save()
        return True, None, obj

    @classmethod
    def add_with_many_local_paths(cls, local_paths, model_type):
        tuples_to_add = []

        for local_path in local_paths:
            _, _, obj = cls.from_local_path_and_model_type(local_path, model_type)
            if obj:
                tuples_to_add.append(obj.to_tuple(with_id=True))

        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.executemany(
                """
                    INSERT OR IGNORE INTO model_info 
                    (
                        id, local_path, file_name, sha_256, model_type, 
                        image_path, civit_model_version_id, size_kb, created_time_stamp, 
                        created_datetime_str, order_num, civit_info_synced, dir, base_model, download_url
                    )
                    VALUES (
                        ?, ?, ?, ?, ?, 
                        ?, ?, ?, ?, 
                        ?, ?, ?, ?, ?, ?
                    )
                """, tuples_to_add)
            conn.commit()

    @classmethod
    def remove_models_in_dir(cls, model_dir):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute("DELETE FROM model_info WHERE dir = ?", (model_dir,))
            conn.commit()

    @classmethod
    def get_all(cls):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute("SELECT * FROM model_info ORDER BY created_time_stamp desc ")
            rows = cur.fetchall()
            return [cls.from_row(row, civit_model_info=None) for row in rows]

    @classmethod
    def get_model_infos(cls, model_type, base_model=None):
        query = "SELECT * FROM model_info WHERE model_type = ? ORDER BY created_time_stamp desc ", (model_type,)
        if base_model:
            query = """ 
                SELECT * FROM model_info 
                WHERE model_type = ? AND REPLACE(LOWER({base_model}), ' ', '') = REPLACE(LOWER(?), ' ', '') 
                ORDER BY created_time_stamp desc 
                """, (model_type, base_model)

        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(*query)
            rows = cur.fetchall()

        model_infos = []
        for row in rows:
            model_infos.append(cls.from_row(row, civit_model_info=None))
        return model_infos

    @classmethod
    def get_with_local_paths(cls, local_paths):

        query = """
                    SELECT * FROM model_info
                    WHERE local_path IN ({})
                """.format(
            ",".join("?" * len(local_paths))
        )

        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(query, local_paths)
            rows = cur.fetchall()

        model_infos = []
        for row in rows:
            model_infos.append(cls.from_row(row, civit_model_info=None))
        return model_infos

    @classmethod
    def get_taesd_model_infos(cls):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                "SELECT * FROM model_info WHERE model_type = ? AND file_name LIKE ? ORDER BY created_time_stamp desc ", ('vae-approx', "tae%")
            )
            rows = cur.fetchall()

        model_infos = []
        for row in rows:
            model_infos.append(cls.from_row(row, civit_model_info=None))
        return model_infos

    @classmethod
    def from_local_path_and_model_type(cls, local_path, model_type):
        path = Path(local_path)
        if not path.exists():
            return False, f"{local_path} not exits.", None
        obj = cls.get(local_path)
        if obj:
            return True, "Already in db", obj

        size_kb = get_file_size_in_kb(local_path)
        file_name = path.name

        created_time_stamp, created_datetime_str = get_file_created_timestamp_and_datetime(local_path)
        obj = cls(
            file_name=file_name,
            local_path=local_path,
            model_type=model_type,
            size_kb=size_kb,
            created_time_stamp=created_time_stamp,
            created_datetime_str=created_datetime_str,
            dir=str(path.parent)
        )
        return True, None, obj

    def to_tuple(self, with_id=False):
        model_dict = self.model_dump()
        model_dict.pop('civit_model')

        if with_id:
            return tuple(model_dict.values())
        else:
            model_dict.pop('id')
            return tuple(model_dict.values())

    @classmethod
    def from_row(cls, row: tuple, civit_model_info):
        model_info = cls(
            id=row[0],
            local_path=row[1],
            file_name=row[2],
            sha_256=row[3],
            model_type=row[4],
            image_path=row[5],
            civit_model_version_id=row[6],
            size_kb=row[7],
            created_time_stamp=row[8],
            created_datetime_str=row[9],
            order_num=row[10],
            civit_info_synced=bool(row[11]),
            dir=row[12],
            base_model=row[13],
            download_url=row[14],
            civit_model=civit_model_info
        )
        return model_info





