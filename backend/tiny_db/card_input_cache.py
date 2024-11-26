from tinydb import TinyDB, Query

from data_type.base import PydanticModel
from misc.whatsai_dirs import db_path_dir
from tiny_db.base_table import BaseTable


class CardCache(BaseTable):
    table_name = db_path_dir / 'card_cache.json'
    db = TinyDB(table_name)

    class DataModel(PydanticModel):
        card_name: str
        card_info: dict

    @classmethod
    def update_or_insert(cls, card_name: str, card_info: dict):
        record = cls.get(card_name)
        if record:
            cls.db.update({'card_info': card_info}, doc_ids=[record.doc_id])
        else:
            cls.insert(card_name, card_info)

    @classmethod
    def insert(cls, card_name: str, card_info: dict):
        cls.db.insert({'card_name': card_name, 'card_info': card_info})

    @classmethod
    def get(cls, card_name: str):
        Q = Query()
        records = cls.db.search(Q.card_name == card_name)
        return records[0] if records else None

    @classmethod
    def delete(cls, card_name: str):
        record = cls.get(card_name)
        if record:
            cls.db.remove(doc_ids=[record.doc_id])
