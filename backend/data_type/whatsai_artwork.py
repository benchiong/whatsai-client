import json
from contextlib import closing
from datetime import datetime
from pathlib import Path
from typing import Optional
from pydantic import BaseModel

from data_type.base_data_model import PyDBModel
from data_type.whatsai_card import Prompt
from misc.constants import MediaType
from misc.helpers import thumbnail, get_file_created_timestamp_and_datetime
from misc.logger import logger
from misc.whatsai_dirs import get_dir_of_media_type

class ThumbImage(BaseModel):
    file_path: Optional[str] = None
    thumb_width: Optional[int] = None
    thumb_height: Optional[int] = None

class Artwork(PyDBModel):

    file_path: str
    media_type: MediaType
    meta_info: Optional[dict] = None

    liked: bool = False
    shared: bool = False

    card_name: str
    prompt: Prompt

    thumb: Optional[ThumbImage] = None
    created_time_stamp: Optional[int] = None
    created_datetime_str: Optional[str] = None

    @classmethod
    def init(cls):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                """CREATE TABLE IF NOT EXISTS artwork
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_path TEXT UNIQUE,
                        media_type TEXT, 
                        meta_info TEXT,
                        liked INTEGER, 
                        shared INTEGER, 
                        card_name TEXT,
                        prompt TEXT,
                        thumb TEXT,
                        created_time_stamp INTEGER,
                        created_datetime_str TEXT
                        )
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS artwork_idx_path ON artwork(file_path)")
            cur.execute("CREATE INDEX IF NOT EXISTS artwork_idx_card_name ON artwork(card_name)")
            cur.execute("CREATE INDEX IF NOT EXISTS artwork_idx_prompt ON artwork(prompt)")

            conn.commit()

    def save(self):
        conn = self.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                """
                INSERT OR REPLACE INTO artwork 
                (
                    id, file_path, media_type, meta_info, liked, 
                    shared, card_name, prompt, thumb, created_time_stamp,
                    created_datetime_str
                )
                VALUES (
                    ?, ?, ?, ?, ?,  
                    ?, ?, ?, ?, ?,
                    ?
                )
                """,
                self.to_tuple(with_id=True),
            )
            if not self.id:
                self.id = cur.lastrowid
            conn.commit()

    @classmethod
    def get(cls, id_or_file_path):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                " SELECT * FROM artwork where id = ? or file_path = ? ",
                (
                    id_or_file_path,
                    id_or_file_path,
                )
            )
            row = cur.fetchone()
            if row is None:
                return None
            else:
                return cls.from_row(row)

    @classmethod
    def remove(cls, id_or_file_path):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute("DELETE FROM artwork WHERE id = ? or file_path = ?", (id_or_file_path, id_or_file_path))
            conn.commit()

    @classmethod
    def get_all(cls, limit=2, skip=12):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                " SELECT * FROM artwork ORDER BY created_time_stamp DESC LIMIT ? OFFSET ?",
                (limit, skip)
            )
            rows = cur.fetchall()
            return [cls.from_row(row) for row in rows]

    @classmethod
    def get_artworks(cls, media_type: MediaType | None, limit=50, skip=0):
        if not media_type:
            return cls.get_all(limit, skip)
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                " SELECT * FROM artwork WHERE media_type = ? ORDER BY created_time_stamp DESC LIMIT ? OFFSET ?",
                (media_type, limit, skip)
            )
            rows = cur.fetchall()
            return [cls.from_row(row) for row in rows]

    @classmethod
    def add_art_work(cls,
                     file_path: str,
                     card_name: str,
                     media_type: MediaType,
                     auto_thumb=True,
                     meta_info=None,
                     prompt=None,
                     ):
        if not Path(file_path).exists():
            logger.debug('Add artwork failed: {} file not exists.'.format(file_path))
            return None

        thumb_file_path, thumb_size, thumb_width, thumb_height = None, None, None, None
        if auto_thumb:
            thumb_file_path, thumb_size = thumbnail(file_path)
        if thumb_size:
            thumb_width, thumb_height = thumb_size

        thumb = ThumbImage(
            file_path=thumb_file_path,
            thumb_width=thumb_width,
            thumb_height=thumb_height
        )

        time_stamp, datetime_str = get_file_created_timestamp_and_datetime(file_path)

        artwork = cls(
            file_path=file_path,
            media_type=media_type,
            meta_info=meta_info,
            card_name=card_name,
            prompt=prompt,
            thumb=thumb,
            created_time_stamp=time_stamp,
            created_datetime_str=datetime_str
        )
        artwork.save()
        return artwork

    @classmethod
    def search_by_substr(cls, substr):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                " SELECT * FROM artwork WHERE card_name LIKE ? OR prompt LIKE ? ORDER BY created_time_stamp DESC",
                (substr, substr)
            )
            rows = cur.fetchall()
            return [cls.from_row(row) for row in rows]

    @classmethod
    def create_file_path(cls, media_type: MediaType):
        filename = datetime.now().strftime('%Y%m%d-%H%M%S') + '.png'
        path = get_dir_of_media_type(media_type)
        return str(path / filename)

    def to_tuple(self, with_id=False):
        model_dict = self.model_dump()
        model_dict['meta_info'] = json.dumps(model_dict.get('meta_info'))
        model_dict['prompt'] = json.dumps(model_dict.get('prompt'))
        model_dict['thumb'] = json.dumps(model_dict.get('thumb'))

        if with_id:
            return tuple(model_dict.values())
        else:
            model_dict.pop('id')
            return tuple(model_dict.values())

    @classmethod
    def from_row(cls, row: tuple):
        model_info = cls(
            id=row[0],
            file_path=row[1],
            media_type=row[2],
            meta_info=json.loads(row[3]),
            liked=row[4],
            shared=row[5],
            card_name=row[6],
            prompt=json.loads(row[7]),
            thumb=json.loads(row[8]),
            created_time_stamp=row[9],
            created_datetime_str=row[10]
        )
        return model_info
