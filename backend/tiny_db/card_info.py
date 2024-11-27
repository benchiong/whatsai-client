from typing import Optional, Literal

from aiotinydb import AIOTinyDB
from tinydb import Query, TinyDB

from data_type.base import PydanticModel
from misc.whatsai_dirs import base_dir, db_path_dir
from misc.custom_cards import load_custom_card
from misc.helpers import get_items_in_dir
from tiny_db.base_table import BaseTable

CardType = Literal['builtin', 'custom', 'remote']

class Dependence:
    """ Custom card dependence, not used yet. """
    pip_name: str
    version: str

# class CustomCard(Base):
#     table_name = db_path_dir / 'custom_card.json'
#
#     class DataModel(PydanticModel):
#         remote_path: str
#         local_path: str
#         is_dir: bool
#         dependence: list[Dependence]
#         created_time_stamp: Optional[int] = None
#         created_datetime_str: Optional[str] = None


class CardModelTable(BaseTable):
    table_name = db_path_dir / 'card.json'
    custom_card_dir = base_dir / 'custom_cards'

    class DataModel(PydanticModel):
        card_name: str
        describe: Optional[str] = None

        card_type: CardType
        location: Optional[str] = None

        remote_url: Optional[str] = None

        pre_models: list[str] = []  # model hashes the card needed to run
        cover_image: Optional[str] = None

        # dependencies: list[Dependence] = []

    @classmethod
    async def init(cls, force_renew=False):

        cls.custom_card_dir.mkdir(exist_ok=True)

        from core.cards import builtin_cards_map
        async with AIOTinyDB(cls.table_name) as db:
            if force_renew:
                db.truncate()

            for card_name in builtin_cards_map.keys():
                Q = Query()
                card_info_in_db = db.search(Q.card_name == card_name)
                if not card_info_in_db:
                    card_class = builtin_cards_map.get(card_name)
                    meta_data = card_class.meta_data
                    card_data_model = cls.DataModel(
                        card_name=card_name,
                        card_type='builtin',
                        location='',
                        describe=meta_data.get('describe', None),
                        pre_models=meta_data.get('pre_models', None),
                        cover_image=meta_data.get('cover_image', None)
                    )
                    db.insert(card_data_model.model_dump())

    @classmethod
    def is_ready(cls, card_name: str):
        card = cls.get_card(card_name)
        if not card:
            raise Exception("Card: {} not found.".format(card_name))
        return False

    @classmethod
    def download_models(cls, card_name: str):
        card = cls.get_card(card_name)
        if not card:
            raise Exception("Card: {} not found.".format(card_name))

    @classmethod
    def download_cover(cls, card_name: str):
        card = cls.get_card(card_name)
        if not card:
            raise Exception("Card: {} not found.".format(card_name))

    @classmethod
    def get_card(cls, card_name: str):
        db = TinyDB(cls.table_name)
        Q = Query()
        card_records = db.search((Q.card_name == card_name))
        return card_records[0] if card_records else None

    @classmethod
    def get_card_class(cls, card_name):
        card_record = cls.get_card(card_name)
        if not card_record:
            return None

        if card_record.get('card_type') == 'builtin':
            from core.cards import builtin_cards_map
            return builtin_cards_map.get(card_name)
        else:
            from misc.custom_cards import custom_card_map
            return custom_card_map.get(card_name)

    @classmethod
    async def get_all_cards(cls, force_renew=False):
        if force_renew:
            await cls.init(force_renew=True)
        db = TinyDB(cls.table_name)
        return db.all()

    @classmethod
    def add_custom_card(cls, card_info: dict):
        card_in_db = cls.get_card(card_info.get('card_name'))
        if card_in_db:
            return None

        db = TinyDB(cls.table_name)
        doc_id = db.insert(card_info)
        card_info['doc_id'] = doc_id
        return card_info

    @classmethod
    def sync_custom_cards(cls):
        items = get_items_in_dir(cls.custom_card_dir)

        added_card_infos = []
        for item in items:
            loaded_card_names = load_custom_card(item)
            for card_name in loaded_card_names:
                card_info = cls.DataModel(
                    card_name=card_name,
                    card_type='custom',
                    location=item.__str__()
                )
                added_card_info = cls.add_custom_card(card_info.model_dump())
                if added_card_info:
                    added_card_infos.append(added_card_info)
        return added_card_infos
