from contextlib import closing
from pathlib import Path
from typing import Optional

from data_type.base_data_model import PyDBModel
from misc.helpers import get_now_timestamp_and_str, file_type_guess
from misc.logger import logger


class InputFile(PyDBModel):
    file_name: str
    file_path: str
    mime: str

    media_type: Optional[str] = ""
    sub_key: Optional[str] = ""

    last_used_time_stamp: Optional[int] = None
    last_used_datetime_str: Optional[str] = None

    created_time_stamp: Optional[int] = None
    created_datetime_str: Optional[str] = None

    @classmethod
    def init(cls):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                """CREATE TABLE IF NOT EXISTS input_file
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_name TEXT,
                        file_path TEXT UNIQUE, 
                        mime TEXT, 
                        media_type TEXT,
                        sub_key TEXT,
                        last_used_time_stamp INTEGER,
                        last_used_datetime_str TEXT,
                        created_time_stamp INTEGER,
                        created_datetime_str TEXT
                        )"""
            )
            cur.execute("CREATE INDEX IF NOT EXISTS input_file_idx_file_path ON input_file(file_path)")

            conn.commit()

    @classmethod
    def get(cls, id_or_file_path):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                "SELECT * FROM input_file where id = ? or file_path = ?", (id_or_file_path, id_or_file_path)
            )
            row = cur.fetchone()
            if row is None:
                return None
            else:
                return cls.from_row(row)

    @classmethod
    def get_input_files(cls, media_type: str, sub_key=None):
        query = " SELECT * FROM input_file WHERE media_type = ? ORDER BY last_used_time_stamp desc ", (media_type, )
        if sub_key:
            query = " SELECT * FROM input_file WHERE media_type = ? AND sub_key = ? ORDER BY last_used_time_stamp desc ", (media_type, sub_key)

        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(*query)
            rows = cur.fetchall()
            return [cls.from_row(row) for row in rows]

    @classmethod
    def add_input_file(cls, file_path, mime=None, sub_key=None):
        if not Path(file_path).exists():
            logger.debug(f"Try to add not exists file to input file: {file_path}")
            return None
        record_in_db = cls.get(file_path)
        if record_in_db:
            record_in_db.save()
            return record_in_db

        if not mime:
            mime = file_type_guess(file_path)
        if mime:
            media_type = mime.split("/")[0]
        else:
            media_type = None

        file_name = Path(file_path).name
        created_time_stamp, created_datetime_str = get_now_timestamp_and_str()

        input_file = cls(
            file_name=file_name,
            file_path=file_path,
            mime=mime,
            media_type=media_type,
            sub_key=sub_key,
            created_time_stamp=created_time_stamp,
            created_datetime_str=created_datetime_str,
            last_used_time_stamp=created_time_stamp,
            last_used_datetime_str=created_datetime_str

        )
        input_file.save()
        return input_file

    def save(self):
        last_used_time_stamp, last_used_datetime_str = get_now_timestamp_and_str()
        self.last_used_time_stamp = last_used_time_stamp
        self.last_used_datetime_str = last_used_datetime_str

        conn = self.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                """ 
                    INSERT OR REPLACE INTO input_file 
                        (
                            id, file_name, file_path, mime, media_type, 
                            sub_key, last_used_time_stamp, last_used_datetime_str, 
                            created_time_stamp, created_datetime_str
                        ) 
                    VALUES 
                        (
                            ?, ?, ?, ?, ?,
                            ?, ?, ?,
                            ?, ?
                        )
                """,
                self.to_tuple(with_id=True),
            )
            if not self.id:
                self.id = cur.lastrowid
            conn.commit()

    @classmethod
    def remove(cls, id_or_file_path):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute("DELETE FROM input_file WHERE id = ? or file_path = ?", (id_or_file_path, id_or_file_path))
            conn.commit()

    @classmethod
    def remove_and_return(cls, file_path, media_type: str, sub_key=None):
        cls.remove(file_path)
        return cls.get_input_files(media_type, sub_key)

    @classmethod
    def from_row(cls, row: tuple):
        input_file = cls(
            id=row[0],
            file_name=row[1],
            file_path=row[2],
            mime=row[3],
            media_type=row[4],
            sub_key=row[5],
            last_used_time_stamp=row[6],
            last_used_datetime_str=row[7],
            created_time_stamp=row[8],
            created_datetime_str=row[9]
        )
        return input_file

