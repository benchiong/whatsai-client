from typing import Optional

from data_type.base import PydanticModel
from data_type.civitai_file import CivitaiFile
from data_type.civitai_image import CivitaiImage


# civitai urls:
# https://civitai.com/api/v1/model-versions/by-hash/A5E5A941A3217247DBCECEEE5B67F8D6B1EF2514260E08A5757436BEC7035F93
# https://civitai.com/api/v1/models/7240
# https://civitai.com/api/v1/model-versions/948574


# Version info lack of info of model, so CivitAI add this field to make it complete.
class CivitaiModelIfoOfVersion(PydanticModel):
    name: str
    type: str
    nsfw: Optional[bool] = None
    poi: Optional[bool] = None

class CivitaiModelVersion(PydanticModel):
    id: int
    modelId: Optional[int] = None
    name: Optional[str] = None
    baseModel: Optional[str] = None
    baseModelType: Optional[str] = None
    description: Optional[str] = None
    model: Optional[CivitaiModelIfoOfVersion] = None

    files: list[CivitaiFile]
    images: list[CivitaiImage]

    downloadUrl: str

class CivitaiFileToDownload(PydanticModel):
    civitaiFile: CivitaiFile
    modelType: str  # where the user put the file according the modelType.


