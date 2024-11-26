import traceback
from pathlib import Path

from tinydb import TinyDB, Query

from data_type.base import PydanticModel
from misc.whatsai_dirs import db_path_dir, media_files_dir
from misc.helpers import sync_download_image, file_type_guess
from misc.logger import logger
from tiny_db.base_table import BaseTable


class MediaFile(BaseTable):
    table_name = db_path_dir / 'media_file.json'

    class DataModel(PydanticModel):
        url: str
        local_path: str
        meta_data: dict = {}

    @classmethod
    def get_by_url(cls, url: str):
        db = TinyDB(cls.table_name)
        Q = Query()
        results = db.search(Q.url == url)
        return results[0] if results else None

    @classmethod
    def add_record(cls, url: str):
        # todo: support other type of files
        record = cls.get_by_url(url)
        if record:
            return record

        try:
            file_name = Path(url).name
            local_image_path = media_files_dir / file_name
            sync_download_image(url=url, file_name=local_image_path)

            db = TinyDB(cls.table_name)
            mime = file_type_guess(local_image_path)
            record = {
                "url": url,
                "local_path": local_image_path.__str__(),
                "meta_data": {
                    'mime': mime
                }
            }

            doc_id = db.insert(record)
            record['doc_id'] = doc_id
            return record

        except Exception as e:
            traceback.print_exc()
            logger.debug("download_image url error:", e)
            return None
