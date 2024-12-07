from contextlib import closing
from typing import Literal

from data_type.base_data_model import PyDBModel

ModelTypeLiteral = Literal['system', 'custom']

class ModelType(PyDBModel):
    type_name: str
    source: ModelTypeLiteral

    @classmethod
    def create_table(cls):
        conn = cls.conn()
        with closing(cls.conn().cursor()) as cur:
            cur.execute(
                """CREATE TABLE IF NOT EXISTS model_type 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     type_name Text UNIQUE,
                     source Text)
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS model_type_idx_type_name ON model_type(type_name)")

            conn.commit()

    @classmethod
    def insert_many(cls, model_types):
        conn = cls.conn()
        model_tuples = []
        for model_type in model_types:
            model_tuples.append(model_type.to_tuple())
        with closing(conn.cursor()) as cur:
            cur.executemany("""
                 INSERT OR IGNORE INTO model_type (type_name, source) VALUES (?, ?)
                """, model_tuples)
            conn.commit()

    @classmethod
    def get(cls, id_or_type_name):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                "SELECT * FROM model_type where id = ? or type_name = ?", (id_or_type_name, id_or_type_name)
            )
            row = cur.fetchone()
            if row is None:
                return None
            else:
                return cls.from_row(row)

    @classmethod
    def is_model_type_registered(cls, type_name):
        record = cls.get(type_name.lower())
        if record:
            return True
        else:
            return False

    @classmethod
    def register_model_type(cls, type_name):
        model_type = cls(type_name=type_name, source='custom')
        model_type.save()
        return model_type

    def save(self):
        conn = self.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                "INSERT OR REPLACE INTO model_type (id, type_name, source) VALUES (?, ?, ?)",
                (self.id, self.type_name, self.source),
            )
            self.id = cur.lastrowid
            conn.commit()

    @classmethod
    def get_all(cls):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute("SELECT * FROM model_type")
            rows = cur.fetchall()
            return [cls.from_row(row) for row in rows]

    @classmethod
    def get_all_model_types(cls):
        model_types = cls.get_all()
        return [model_type.type_name for model_type in model_types]

    @classmethod
    def from_row(cls, row: tuple):
        model_type = cls(id=row[0], type_name=row[1], source=row[2])
        return model_type

    @classmethod
    def init(cls):
        cls.create_table()

        model_types_to_save = []
        for model_type in initial_model_types:
            model_type = cls(type_name=model_type, source='system')
            model_types_to_save.append(model_type)

        cls.insert_many(model_types_to_save)


initial_model_types = [
    'checkpoint',
    'clip',
    'clip_vision',
    'controlnet',
    'embedding',
    'upscaler',
    'gligen',
    'hypernet',
    'inpainting',
    'lora',
    'vae',
    'vae-approx',
    'others'
]
