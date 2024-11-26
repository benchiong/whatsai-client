from aiotinydb import AIOTinyDB

from data_type.whatsai_model_type import ModelType, initial_model_types, ModelTypeLiteral
from misc.whatsai_dirs import db_path_dir
from tiny_db.base_table import BaseTable
from tiny_db.initialized_record import DBInitializedRecordTable


class ModelTypeTable(BaseTable):
    table_name = db_path_dir / 'model_type.json'
    DataModel = ModelType

    @classmethod
    async def init(cls):
        inited = await DBInitializedRecordTable.is_table_initialized(cls.table_name.__str__())
        if not inited:
            for model_type in initial_model_types:
                await cls.register_model_type(model_type, 'system')
            await DBInitializedRecordTable.insert_or_update(cls.table_name.__str__(), True)

    @classmethod
    async def all_model_types(cls):
        async with AIOTinyDB(cls.table_name) as db:
            return [r.get('type_name').lower() for r in db.all() if r.get('type_name')]

    @classmethod
    async def register_model_type(cls, type_name: str, source: ModelTypeLiteral):
        if not await cls.is_model_type_registered(type_name):
            async with AIOTinyDB(cls.table_name) as db:
                db.insert({
                    'type_name': type_name.upper(),
                    'source': source
                })

    @classmethod
    async def is_model_type_registered(cls, type_name: str):
        return type_name.lower() in await cls.all_model_types()
