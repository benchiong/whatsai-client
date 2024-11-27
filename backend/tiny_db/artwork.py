import json
import re
from datetime import datetime
from pathlib import Path

from aiotinydb import AIOTinyDB
from tinydb import Query, TinyDB

from data_type.whatsai_artwork import MediaType, Artwork
from misc.whatsai_dirs import db_path_dir, get_dir_of_media_type, cache_dir
from misc.helpers import thumbnail, get_file_created_timestamp_and_datetime
from misc.logger import logger
from tiny_db.helpers import fill_id


class ArtworkTable:
    # todo: add basemodel query support.

    table_name = db_path_dir / 'art.json'
    DataModel = Artwork

    @classmethod
    async def get_artworks(cls, media_type: MediaType | None):
        async with AIOTinyDB(cls.table_name) as db:
            if media_type is None:
                results = db.all()
            else:
                Q = Query()
                results = db.search(Q.media_type == media_type.value)
            results = fill_id('artwork_id', results)
            return sorted(results, key=lambda r: r.get('created_time_stamp'), reverse=True)

    @classmethod
    def add_art(cls,
                file_path: str,
                card_name: str,
                media_type: MediaType,
                auto_thumb=True,
                meta_info=None,
                inputs_info=None,
                addon_inputs_info=None
                ):
        """ This method will be used by func module, so blocked actions should be ok. """

        if not Path(file_path).exists():
            logger.debug('Add art: {} file not exists.'.format(file_path))
            return None

        thumb_file, thumb_size = None, None
        thumb_width, thumb_height = None, None
        if auto_thumb:
            thumb_file, thumb_size = thumbnail(file_path, cache_dir)
        if thumb_size:
            thumb_width, thumb_height = thumb_size

        time_stamp, datetime_str = get_file_created_timestamp_and_datetime(file_path)

        info_dict = {
            # **card_info,
            **inputs_info,
            **addon_inputs_info
        }

        info_str = json.dumps(info_dict)

        artwork = cls.DataModel(
            card_name=card_name,
            path=file_path,
            media_type=media_type,
            meta_info=meta_info,
            # card_info=card_info,
            inputs_info=inputs_info,
            addon_inputs_info=addon_inputs_info,
            info=info_str,
            thumb=thumb_file,
            thumb_width=thumb_width,
            thumb_height=thumb_height,
            created_time_stamp=time_stamp,
            created_datetime_str=datetime_str
        )
        artwork_record = artwork.model_dump()

        db = TinyDB(cls.table_name)
        doc_id = db.insert(artwork_record)
        artwork_record['artwork_id'] = doc_id
        return artwork_record

    @classmethod
    async def search_by_substr(cls, substr):
        async with AIOTinyDB(cls.table_name) as db:
            Q = Query()
            results = db.search(Q.info.matches('.*{}.*'.format(substr), flags=re.IGNORECASE))
            results = fill_id('artwork_id', results)
            return sorted(results, key=lambda r: r.get('created_time_stamp'), reverse=True)

    @classmethod
    async def get_artwork(cls, artwork_id: int):
        async with AIOTinyDB(cls.table_name) as db:
            art = db.get(doc_id=artwork_id)
            if art:
                art = fill_id('artwork_id', [art])[0]
            return art

    @classmethod
    async def get_art_by_path(cls, path: str):
        async with AIOTinyDB(cls.table_name) as db:
            Q = Query()
            results = db.search(Q.path == path)
            results = fill_id('artwork_id', results)
            return results[0] if results else None

    @classmethod
    async def delete_art(cls, art_id):
        async with AIOTinyDB(cls.table_name) as db:
            db.remove(doc_ids=[art_id])

    @classmethod
    def get_file_name(cls, media_type: MediaType):
        filename = datetime.now().strftime('%Y%m%d-%H%M%S') + '.png'
        path = get_dir_of_media_type(media_type)
        return (path / filename).__str__()


