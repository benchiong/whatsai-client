import threading

from tinydb import TinyDB, Query

from data_type.whatsai_model_downloading_info import ModelDownloadingInfo
from misc.whatsai_dirs import db_path_dir
from tiny_db.base_table import BaseTable


class ModelDownloadInfoTable(BaseTable):
    table_name = db_path_dir / 'model_download_info.json'
    mutex = threading.RLock()
    db = TinyDB(table_name)
    DataModel = ModelDownloadingInfo

    @classmethod
    def get_all_downloading_records(cls):
        with cls.mutex:
            Q = Query()
            return cls.db.search(Q.finished != True)

    @classmethod
    def get_record(cls, url: str):
        with cls.mutex:
            Q = Query()
            results = cls.db.search(Q.url == url)
            return results[0] if results else None

    @classmethod
    def add_record(cls, model_download_info: ModelDownloadingInfo):
        with cls.mutex:
            url = model_download_info.url
            record = cls.get_record(url)
            if record:
                return record
            cls.db.insert(model_download_info.model_dump())

    @classmethod
    def update_record(cls, model_download_info: ModelDownloadingInfo):
        with cls.mutex:
            url = model_download_info.url
            record = cls.get_record(url)
            if not record:
                return False, "No record found with url: {}".format(url)

            cls.db.update(model_download_info.model_dump(), doc_ids=[record.doc_id])
            return True, None

