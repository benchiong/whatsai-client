from typing import Optional

from data_type.base import PydanticModel
from data_type.whatsai_model_info import ModelInfo


class ModelDownloadingInfo(PydanticModel):
    url: str
    model_info: ModelInfo
    total_size: float

    downloaded_size: float = 0.0
    downloaded_time: float = 0.0

    progress: float = 0.0
    eta:  Optional[float] = None

    finished: bool = False


