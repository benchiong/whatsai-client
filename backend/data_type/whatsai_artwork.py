from typing import Optional, Literal

from data_type.base import PydanticModel

MediaType = Literal['image', 'video', 'audio', 'other']
class Artwork(PydanticModel):

    art_id: Optional[int] = None

    path: str
    media_type: MediaType

    meta_info: Optional[dict] = None
    tags: list[str] = None

    liked: bool = False
    shared: bool = False

    card_name: str
    card_info: Optional[dict] = None
    inputs_info: Optional[dict] = None
    addon_inputs_info: Optional[dict] = None

    info: Optional[str] = None

    thumb: Optional[str] = None
    thumb_width: Optional[int] = None
    thumb_height: Optional[int] = None

    created_time_stamp: Optional[int] = None
    created_datetime_str: Optional[str] = None


