from typing import Optional

from data_type.base import PydanticModel


# civitai urls:
# https://civitai.com/api/v1/model-versions/by-hash/A5E5A941A3217247DBCECEEE5B67F8D6B1EF2514260E08A5757436BEC7035F93
# https://civitai.com/api/v1/models/7240
# https://civitai.com/api/v1/model-versions/948574

class CivitaiImageMetaData(PydanticModel):
    hash: Optional[str] = None
    size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None

class CivitaiImage(PydanticModel):
    # only needed fields defined here
    url: str
    nsfwLevel: int
    width: int
    height: int
    hash: str
    type: str

    metadata: Optional[CivitaiImageMetaData] = None

