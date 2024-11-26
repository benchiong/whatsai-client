from datetime import datetime
from pathlib import Path
from typing import Optional

from tinydb import TinyDB, Query

from data_type.base import PydanticModel
from misc.whatsai_dirs import base_dir, db_path_dir
from misc.helpers import file_type_guess
from tiny_db.base_table import BaseTable


class InputFile(BaseTable):
    table_name = db_path_dir / 'input_file.json'
    input_dir = base_dir / 'inputs'

    class DataModel(PydanticModel):
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
    def add_input_file(cls, file_path, mime=None, sub_key=""):
        if not Path(file_path).exists():
            raise Exception("File: {} not exists.".format(file_path))

        record = cls.get_input_file(file_path)
        if record:
            cls.update_last_use_time(record.doc_id)
            return record

        if not mime:
            mime = file_type_guess(file_path)

        media_type = mime.split("/")[0]
        file_name = Path(file_path).name
        now = datetime.now()
        created_time_stamp = int(now.timestamp())
        created_datetime_str = now.strftime("%Y/%m/%d %H:%M:%S")

        last_used_time_stamp = created_time_stamp
        last_used_datetime_str = created_datetime_str

        data = cls.DataModel(
            file_name=file_name,
            file_path=file_path,
            sub_key=sub_key,
            media_type=media_type,
            mime=mime,
            created_datetime_str=created_datetime_str,
            created_time_stamp=created_time_stamp,
            last_used_time_stamp=last_used_time_stamp,
            last_used_datetime_str=last_used_datetime_str
        )
        db = TinyDB(cls.table_name)
        record = data.model_dump()
        doc_id = db.insert(record)
        record['doc_id'] = doc_id
        return record

    @classmethod
    def get_input_file(cls, file_path: str):
        db = TinyDB(cls.table_name)
        Q = Query()
        results = db.search(Q.file_path == file_path)
        return results[0] if results else None

    @classmethod
    def get_input_files(cls, media_type: str, sub_key=""):
        db = TinyDB(cls.table_name)
        Q = Query()
        if sub_key:
            results = db.search((Q.media_type == media_type) & (Q.sub_key == sub_key))
        else:
            results = db.search(Q.media_type == media_type)
        return sorted(results, key=lambda r: r.get('last_used_time_stamp'), reverse=True)

    @classmethod
    def update_last_use_time(cls, doc_id):
        if not doc_id:
            return

        now = datetime.now()
        last_used_time_stamp = int(now.timestamp())
        last_used_datetime_str = now.strftime("%Y/%m/%d %H:%M:%S")

        db = TinyDB(cls.table_name)
        db.update({
            'last_used_time_stamp': last_used_time_stamp,
            'last_used_datetime_str': last_used_datetime_str
        }, doc_ids=[doc_id])

    @classmethod
    def get_inputs(cls, file_type: str):
        db = TinyDB(cls.table_name)
        Q = Query()
        results = db.search(Q.mime.startswith(file_type))
        return sorted(results, key=lambda r: r.get('last_used_time_stamp'), reverse=True)
