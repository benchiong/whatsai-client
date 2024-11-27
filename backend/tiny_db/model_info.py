import threading
from pathlib import Path

from aiotinydb import AIOTinyDB
from tinydb import TinyDB

from data_type.civitai_model_version import CivitaiModelVersion
from data_type.whatsai_model_info import ModelInfo
from misc.whatsai_dirs import db_path_dir
from tiny_db.base_table import BaseTable

class ModelInfoTable(BaseTable):
    table_name = db_path_dir / 'model_info.json'
    DataModel = ModelInfo
    mutex = threading.RLock()

    @classmethod
    async def get_all_models(cls):
        with cls.mutex:
            async with AIOTinyDB(cls.table_name) as db:
                return db.all()

    @classmethod
    async def get_model_info_by_file_path(cls, file_path: str):
        with cls.mutex:
            async with AIOTinyDB(cls.table_name) as db:
                results = db.search(cls.Q.local_path == file_path)
                return results[0] if results else None

    @classmethod
    async def get_model_info_by_hash(cls, hash_str: str):
        with cls.mutex:
            async with AIOTinyDB(cls.table_name) as db:
                results = db.search(cls.Q.sha_256 == hash_str)
                return results[0] if results else None

    @classmethod
    async def get_model_info_by_model_type(cls, model_type: str | None):
        with cls.mutex:
            async with AIOTinyDB(cls.table_name) as db:
                if model_type is None or model_type.lower() == 'none':
                    results = db.all()
                else:
                    results = db.search(cls.Q.model_type == model_type.upper())
                return results

    @classmethod
    async def get_model_info_by_file_name(cls, file_name: str):
        with cls.mutex:
            async with AIOTinyDB(cls.table_name) as db:
                results = db.search(cls.Q.file_name == file_name)
                return results[0] if results else None

    @classmethod
    async def remove_record(cls, doc_id: int):
        with cls.mutex:
            async with AIOTinyDB(cls.table_name) as db:
                db.remove(doc_ids=[doc_id])

    @classmethod
    def sync_get_taesd_file_records(cls):
        with cls.mutex:
            db = TinyDB(cls.table_name)
            tae_files = db.search(cls.Q.model_type == 'vae-approx'.upper())
            tae_files = [tae_file for tae_file in tae_files if tae_file.get('file_name').startswith('tae')]
            return tae_files

    @classmethod
    def sync_get_model_info_by_file_name(cls, file_name: str):
        with cls.mutex:
            db = TinyDB(cls.table_name)
            results = db.search(cls.Q.file_name == file_name)
            return results[0] if results else None

    @classmethod
    def sync_get_model_info_by_hash(cls, hash_str: str):
        with cls.mutex:
            db = TinyDB(cls.table_name)
            results = db.search(cls.Q.sha_256 == hash_str)
            return results[0] if results else None

    @classmethod
    def sync_get_model_info_by_model_type(cls, model_type: str | None, base_model: str | None = None):
        with cls.mutex:
            db = TinyDB(cls.table_name)
            if model_type is None or model_type.lower() == 'none':
                return db.all()
            else:
                if base_model:
                    return db.search((cls.Q.model_type == model_type.upper()) & (cls.Q.base_model == base_model))
                else:
                    return db.search(cls.Q.model_type == model_type.upper())

    @classmethod
    def sync_add_model_info(cls, model_info: ModelInfo):
        with cls.mutex:
            hash_str = model_info.sha_256
            record = cls.sync_get_model_info_by_hash(hash_str)
            if record:
                return
            db = TinyDB(cls.table_name)
            db.insert(model_info.model_dump())

    @classmethod
    async def add_model_info(cls,
                             hash_str: str,
                             file_path: str,
                             model_type: str,
                             image_path: str,
                             civitai_model: CivitaiModelVersion,
                             size_kb: float = None,
                             created_time_stamp: int = None,
                             created_datetime_str: str = None,
                             force_renew: bool = False,
                             ):
        with cls.mutex:
            record = await cls.get_model_info_by_file_path(file_path)

            if not record:
                model_info = cls.DataModel(
                    local_path=file_path,
                    file_name=Path(file_path).name,
                    sha_256=hash_str,
                    model_type=model_type.upper(),
                    image_path=image_path,
                    civit_model=civitai_model,
                    size_kb=size_kb,
                    created_time_stamp=created_time_stamp,
                    created_datetime_str=created_datetime_str
                )

                async with AIOTinyDB(cls.table_name) as db:
                    doc_id = db.insert(model_info.model_dump())

                return {
                    **model_info.model_dump(),
                    'doc_id': doc_id
                }

            elif force_renew:
                await cls.remove_record(doc_id=record.doc_id)
                async with AIOTinyDB(cls.table_name) as db:
                    model_info = cls.DataModel(
                        local_path=file_path,
                        file_name=Path(file_path).name,
                        sha_256=hash_str,
                        model_type=model_type.upper(),
                        image_path=image_path,
                        civit_model=civitai_model,
                        size_kb=size_kb,
                        created_time_stamp=created_time_stamp,
                        created_datetime_str=created_datetime_str
                    )
                    doc_id = db.insert(model_info.model_dump())
                    return {
                        **model_info.model_dump(),
                        'doc_id': doc_id
                    }
            else:
                return record
