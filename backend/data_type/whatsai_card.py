import json
from contextlib import closing
from pathlib import Path
from typing import Optional, Literal
from pydantic import BaseModel

from data_type.base_data_model import PyDBModel
from data_type.whatsai_model_info import ModelInfo
from misc.arg_parser import is_prod
from misc.custom_cards import load_custom_card
from misc.helpers import get_now_timestamp_and_str, download_image, get_items_in_dir
from misc.whatsai_dirs import media_files_dir

CardType = Literal['builtin', 'custom']


class Prompt(BaseModel):
    """ Prompt are just inputs of the card, set by user, use to generate. """
    card_name: str
    base_inputs: dict
    addon_inputs: Optional[dict] = None


class CardInfo(BaseModel):
    """ CardInfo are about widgets card and card's addon include, use to tell frontend to render. """
    card_name: str
    card_display_name: Optional[str] = None
    widgets: list[dict] = []
    addons: list[dict] = []

    def to_prompt(self, filter_none=True):
        card_name = self.card_name
        widgets = self.widgets
        addons = self.addons

        def is_none_in_dict_values(d: dict):
            for k, v in d.items():
                if v is None or v == 'None':
                    return True
            return False

        base_inputs = {}
        for widget in widgets:
            widget_type = widget.get('widget_type')
            if widget_type == 'GroupedWidgets':
                _widgets = widget.get('value')
                for _widget in _widgets:
                    parma_name = _widget.get('param_name')
                    value = _widget.get('value')
                    base_inputs[parma_name] = value
            elif widget_type == 'SwitchableWidgets':
                comps_with_selection = widget.get('value')
                for comp_name, widgets_and_selection in comps_with_selection.items():
                    selected = widgets_and_selection.get('selected', False)
                    if selected:
                        base_inputs[widget.get('name')] = comp_name
                        _widgets = widgets_and_selection.get('widgets', [])
                        for _widget in _widgets:
                            parma_name = _widget.get('param_name')
                            value = _widget.get('value')
                            base_inputs[parma_name] = value
                        break
            else:
                parma_name = widget.get('param_name')
                value = widget.get('value')
                base_inputs[parma_name] = value

        addon_inputs = {}
        for addon in addons:
            addon_name = addon.get('addon_name')
            addon_widgets_list = addon.get('widgets')
            can_turn_off = addon.get('can_turn_off')
            is_off = addon.get('is_off')
            is_switchable = addon.get('is_switchable')

            if can_turn_off and is_off:
                continue

            if is_switchable:
                switchable_widget_info = addon_widgets_list[0][0] if addon_widgets_list else None
                if not switchable_widget_info:
                    continue

                switchable_comps = switchable_widget_info.get('value')

                addon_inputs_list = []
                addon_widgets_input = {}

                for comp_name, widgets_and_selection in switchable_comps.items():
                    selected = widgets_and_selection.get('selected', False)

                    if selected:
                        addon_widgets_input['selected_comp_name'] = comp_name
                        _widgets = widgets_and_selection.get('widgets', [])
                        for _widget in _widgets:
                            parma_name = _widget.get('param_name')
                            value = _widget.get('value')
                            addon_widgets_input[parma_name] = value
                        addon_inputs_list.append(addon_widgets_input)
                        break

                addon_inputs[addon_name] = addon_inputs_list
                continue

            addon_inputs_list = []
            for addon_widgets in addon_widgets_list:
                addon_widgets_input = {}
                for addon_widget in addon_widgets:
                    parma_name = addon_widget.get('param_name')
                    value = addon_widget.get('value')
                    addon_widgets_input[parma_name] = value

                if filter_none and is_none_in_dict_values(addon_widgets_input):
                    continue
                addon_inputs_list.append(addon_widgets_input)

            if addon_inputs_list:
                addon_inputs[addon_name] = addon_inputs_list

        prompt = Prompt(
            card_name=card_name,
            base_inputs=base_inputs,
            addon_inputs=addon_inputs
        )
        return prompt


class PreModel(BaseModel):
    """ Model info to make sure the user can use the card. """
    hash: Optional[str] = None  # if you use civitai model, put sha_256 here, it should be the first option.
    download_url: Optional[str] = None  # only civitai model download supported yet, leave if here for following work.
    file_name: Optional[str] = None

    def is_ready(self):
        if self.hash:
            model_info = ModelInfo.get(self.hash)
        elif self.file_name:
            model_info = ModelInfo.get(self.file_name)
        elif self.download_url:
            model_info = ModelInfo.get(self.download_url)
        else:
            model_info = None
        if not model_info:
            return False
        return Path(model_info.local_path).exists()


class CardDataModel(PyDBModel):
    card_name: str

    display_name: Optional[str] = None
    describe: Optional[str] = None

    card_type: CardType

    location: Optional[str] = None  # where the card class locates, None if builtin card.
    remote_url: Optional[str] = None  # where to download remote codes, mainly for custom card.

    pre_models: list[PreModel] = []
    cover_image: Optional[str] = None

    created_time_stamp: Optional[int] = None
    created_datetime_str: Optional[str] = None
    order_number: Optional[int] = 0
    favour: Optional[bool] = False

    default_card_info: Optional[CardInfo] = None
    cached_card_info: Optional[CardInfo] = None

    @classmethod
    def create_table(cls):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                """CREATE TABLE IF NOT EXISTS card
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        card_name TEXT UNIQUE,
                        display_name TEXT, 
                        describe TEXT,
                        card_type TEXT, 
                        location TEXT,
                        remote_url TEXT,
                        pre_models TEXT,
                        cover_image TEXT,
                        created_time_stamp INTEGER,
                        created_datetime_str TEXT,
                        order_num INTEGER,
                        favour INTEGER DEFAULT 0,
                        default_card_info TEXT,
                        cached_card_info TEXT
                        )
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS card_idx_card_name ON card(card_name)")
            conn.commit()

    @classmethod
    def clear(cls):  # convenient when debugging cards.
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(" DELETE FROM card ")
            conn.commit()

    @classmethod
    def init(cls):
        from core.cards import BUILTIN_CARDS_MAP
        cls.create_table()
        if not is_prod:
            cls.clear()

        cards_to_insert = []
        for card_name in BUILTIN_CARDS_MAP.keys():
            card_class = BUILTIN_CARDS_MAP.get(card_name)
            meta_data = card_class.meta_data
            created_time_stamp, created_datetime_str = get_now_timestamp_and_str()
            card = cls(
                card_name=card_name,
                display_name=meta_data.get('display_name'),
                describe=meta_data.get('describe'),
                card_type='builtin',
                location=None,
                remote_url=None,
                pre_models=[PreModel(**pre_model_dict) for pre_model_dict in meta_data.get('pre_models', [])],
                cover_image=meta_data.get('cover_image'),
                created_time_stamp=created_time_stamp,
                created_datetime_str=created_datetime_str,
            )
            cards_to_insert.append(card)

        cls.insert_many(cards_to_insert)

    @classmethod
    def fill_default_infos_of_card(cls):
        """ Fill the default card info of a card.

        // Not sure if it's still the case.
        The reason we don't do this at table init stage is at that time addon infos are
        not ready yet, we will fail, so put it later when server try to start
        """
        cards_to_full = cls.get_cards_without_default_card_info()
        for card in cards_to_full:
            card_class = cls.get_card_class(card.card_name)
            if card_class:
                default_card_info_dict = card_class().card_info
                card.default_card_info = CardInfo(**default_card_info_dict)
                card.save()

    def save(self):
        conn = self.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                """
                INSERT OR REPLACE INTO card 
                (
                    id, card_name, display_name, describe, card_type, location, 
                    remote_url, pre_models, cover_image, created_time_stamp, 
                    created_datetime_str, order_num, favour,
                    default_card_info, cached_card_info
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, 
                    ?, ?, ?,
                    ?, ?
                )
                """,
                self.to_tuple(with_id=True),
            )
            if not self.id:
                self.id = cur.lastrowid
            conn.commit()

    def get_card_info(self, use_cache=True):
        if use_cache and self.cached_card_info:
            return self.cached_card_info
        else:
            return self.default_card_info

    @classmethod
    def insert_many(cls, cards):
        conn = cls.conn()
        card_tuples = []
        for card in cards:
            card_tuples.append(card.to_tuple(with_id=True))
        with closing(conn.cursor()) as cur:
            cur.executemany(
                """
                INSERT OR REPLACE INTO card 
                (
                    id, card_name, display_name, describe, card_type, location, 
                    remote_url, pre_models, cover_image, created_time_stamp, 
                    created_datetime_str, order_num, favour,
                    default_card_info, cached_card_info
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, 
                    ?, ?, ?,
                    ?, ?
                )
                """, card_tuples)
            conn.commit()

    @classmethod
    def get(cls, id_or_card_name):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                " SELECT * FROM card where id = ? or card_name = ? ",
                (
                    id_or_card_name,
                    id_or_card_name,
                )
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
            cur.execute(
                " SELECT * FROM card ORDER BY created_time_stamp DESC ",
            )
            rows = cur.fetchall()
            return [cls.from_row(row) for row in rows]

    @classmethod
    def get_cards_without_default_card_info(cls):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            # sqlite set default_card_info a 'null' str in table when is None
            cur.execute(
                " SELECT * FROM card WHERE default_card_info IS NULL or default_card_info = 'null'  ORDER BY created_time_stamp DESC ",
            )
            rows = cur.fetchall()
            return [cls.from_row(row) for row in rows]

    def is_ready(self):
        pre_models_ready = [pre_models.is_ready() for pre_models in self.pre_models]
        return all(pre_models_ready)

    def to_tuple(self, with_id=False):
        model_dict = self.model_dump()
        model_dict['pre_models'] = json.dumps(model_dict.get('pre_models', []))
        model_dict['default_card_info'] = json.dumps(model_dict.get('default_card_info', []))
        model_dict['cached_card_info'] = json.dumps(model_dict.get('cached_card_info', []))

        if with_id:
            return tuple(model_dict.values())
        else:
            model_dict.pop('id')
            return tuple(model_dict.values())

    @classmethod
    def from_row(cls, row: tuple):
        model_info = cls(
            id=row[0],
            card_name=row[1],
            display_name=row[2],
            describe=row[3],
            card_type=row[4],
            location=row[5],
            remote_url=row[6],
            pre_models=json.loads(row[7]),
            cover_image=row[8],
            created_time_stamp=row[9],
            created_datetime_str=row[10],
            order_num=row[11],
            favour=row[12],
            default_card_info=json.loads(row[13]),
            cached_card_info=json.loads(row[14])
        )
        return model_info

    @classmethod
    def get_card_class(cls, card_name):
        card_record = cls.get(card_name)
        if not card_record:
            return None

        if card_record.card_type == 'builtin':
            from core.cards import BUILTIN_CARDS_MAP
            return BUILTIN_CARDS_MAP.get(card_name)
        else:
            # from misc.custom_cards import custom_card_map
            # return custom_card_map.get(card_name)
            pass

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
                    location=str(item)
                )
                added_card_info = cls.add_custom_card(card_info.model_dump())
                if added_card_info:
                    added_card_infos.append(added_card_info)
        return added_card_infos


async def download_cover_image(card_data_model: CardDataModel):
    if card_data_model.cover_image and card_data_model.cover_image.startswith('http'):
        file_name = Path(card_data_model.cover_image).name
        local_image_path = media_files_dir / file_name
        result = await download_image(card_data_model.cover_image, str(local_image_path))
        if result:
            card_data_model.cover_image = str(local_image_path)
            card_data_model.save()
