import json
from contextlib import closing
from typing import Optional

from data_type.civitai_file import CivitaiFile
from data_type.civitai_image import CivitaiImage
from data_type.base_data_model import PyDBModel


# civitai urls:
# https://civitai.com/api/v1/model-versions/by-hash/A5E5A941A3217247DBCECEEE5B67F8D6B1EF2514260E08A5757436BEC7035F93
# https://civitai.com/api/v1/models/7240
# https://civitai.com/api/v1/model-versions/948574


# Version info lack of info of model, so CivitAI add this field to make it complete.
class CivitaiModelIfoOfVersion(PyDBModel):
    name: str
    type: str
    nsfw: Optional[bool] = None
    poi: Optional[bool] = None

class CivitaiFileToDownload(PyDBModel):
    civitaiFile: CivitaiFile
    modelType: str  # where the user put the file according the modelType.

class CivitaiModelVersion(PyDBModel):
    modelId: Optional[int] = None
    name: Optional[str] = None
    baseModel: Optional[str] = None
    baseModelType: Optional[str] = None
    description: Optional[str] = None

    model: Optional[CivitaiModelIfoOfVersion] = None
    files: list[CivitaiFile]
    images: list[CivitaiImage]

    downloadUrl: str

    @classmethod
    def create_table(cls):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                """CREATE TABLE IF NOT EXISTS civit_model_version
                        (id INTEGER UNIQUE PRIMARY KEY,
                        modelId INTEGER,
                        name TEXT,
                        baseModel TEXT, 
                        baseModelType TEXT,
                        description TEXT,
                        model TEXT,
                        files TEXT,
                        images TEXT,
                        downloadUrl TEXT)"""
            )
            cur.execute("CREATE INDEX IF NOT EXISTS civit_model_version_idx_name ON civit_model_version(name)")
            conn.commit()
    @classmethod
    def init(cls):
        cls.create_table()
    def save(self):
        conn = self.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                """
                INSERT OR REPLACE INTO civit_model_version 
                (id, modelId, name, baseModel, baseModelType, description, model, files, images, downloadUrl) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                self.to_tuple(with_id=True),
            )
            conn.commit()

    def to_tuple(self, with_id=False):
        model_dict = self.model_dump()
        model_dict['model'] = json.dumps(model_dict.get('model', ''))
        model_dict['files'] = json.dumps(model_dict.get('files', ''))
        model_dict['images'] = json.dumps(model_dict.get('images', ''))

        if with_id:
            return tuple(model_dict.values())
        else:
            model_dict.pop('id')
            return tuple(model_dict.values())

    @classmethod
    def from_row(cls, row: tuple):
        model_data = json.loads(row[6])
        model = CivitaiModelIfoOfVersion(**model_data)

        files_dict = json.loads(row[7])
        files = [CivitaiFile(**data) for data in files_dict]

        images_data = json.loads(row[8])
        images = [CivitaiImage(**data) for data in images_data]

        model_dir = cls(
            id=row[0],
            modelId=row[1],
            name=row[2],
            baseModel=row[3],
            baseModelType=row[4],
            description=row[5],

            model=model,
            files=files,
            images=images,

            downloadUrl=row[9]
        )
        return model_dir
    @classmethod
    def get(cls, id_or_name):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                "SELECT * FROM civit_model_version where id = ? or name = ?", (id_or_name, id_or_name)
            )
            row = cur.fetchone()
            if row is None:
                return None
            else:
                return cls.from_row(row)






