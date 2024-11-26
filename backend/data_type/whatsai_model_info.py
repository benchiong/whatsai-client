from typing import Optional

from data_type.base import PydanticModel
from data_type.civitai_model_version import CivitaiModelVersion


class ModelInfo(PydanticModel):
    local_path: str
    file_name: str

    # some data get from civitai is empty,
    # case: https://civitai.com/api/v1/models/618692   files[0]
    sha_256: Optional[str] = ""
    model_type: str

    image_path: Optional[str] = None

    civit_model: Optional[CivitaiModelVersion] = None

    size_kb: Optional[float] = 0
    created_time_stamp: Optional[int] = 0
    created_datetime_str: Optional[str] = ""

    order_num: Optional[int] = 0  # use to set order manually, not used yet.


