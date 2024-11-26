from aiotinydb import AIOTinyDB
from data_type.base import PydanticModel
from misc.whatsai_dirs import db_path_dir
from tiny_db.base_table import BaseTable


class DBInitializedRecordTable(BaseTable):
    table_name = db_path_dir / 'initialized_record.json'

    cached_results = None

    class DataModel(PydanticModel):
        table_path: str
        initialized: bool

    @classmethod
    async def is_table_initialized(cls, table_path: str, use_cache=True):
        if use_cache:
            if cls.cached_results is None:
                results = await cls.get_all_records()
                results_to_cache = {}
                for r in results:
                    results_to_cache[r.get('table_path')] = r.get('initialized')
                cls.cached_results = results_to_cache

            return cls.cached_results.get(table_path, False)
        else:
            return await cls.get_table_initialized(table_path)

    @classmethod
    async def get_all_records(cls):
        async with AIOTinyDB(cls.table_name) as db:
            return db.all()

    @classmethod
    async def get_table_initialized(cls, table_path: str):
        async with AIOTinyDB(cls.table_name) as db:
            results = db.search(cls.Q.table_path == table_path)
            return results[0] if results else None

    @classmethod
    async def insert_or_update(cls, table_path: str, initialized, use_cache=True):
        record = await cls.get_table_initialized(table_path)
        if record:
            async with AIOTinyDB(cls.table_name) as db:
                db.update({'initialized': initialized}, doc_ids=[record.doc_id])
        else:
            async with AIOTinyDB(cls.table_name) as db:
                db.insert({
                    'table_path': table_path,
                    'initialized': initialized
                })
        if use_cache:
            cls.cached_results = {
                **cls.cached_results,
                table_path: initialized
            }

    @classmethod
    async def reset(cls):
        async with AIOTinyDB(cls.table_name) as db:
            db.truncate()
