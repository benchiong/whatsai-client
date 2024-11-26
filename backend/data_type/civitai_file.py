from typing import Optional

from data_type.base import PydanticModel

# civitai urls:
# https://civitai.com/api/v1/model-versions/by-hash/A5E5A941A3217247DBCECEEE5B67F8D6B1EF2514260E08A5757436BEC7035F93
# https://civitai.com/api/v1/models/7240
# https://civitai.com/api/v1/model-versions/948574

class CivitaiFileHashes(PydanticModel):
    AutoV1: Optional[str] = None
    AutoV2: Optional[str] = None
    SHA256: Optional[str] = None  # whatsai used
    CRC32: Optional[str] = None
    BLAKE3: Optional[str] = None
    AutoV3: Optional[str] = None

class CivitaiFile(PydanticModel):
    id: int
    sizeKB: float
    name: str
    type: str

    hashes: CivitaiFileHashes
    primary: Optional[bool] = False
    downloadUrl: str

