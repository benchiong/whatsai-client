from data_type.base import PydanticModel
from data_type.civitai_model_version import CivitaiModelVersion


# civitai urls:
# https://civitai.com/api/v1/model-versions/by-hash/A5E5A941A3217247DBCECEEE5B67F8D6B1EF2514260E08A5757436BEC7035F93
# https://civitai.com/api/v1/models/7240
# https://civitai.com/api/v1/model-versions/948574

class CivitaiModel(PydanticModel):
    id: int
    name: str
    description: str
    type: str
    nsfw: bool
    nsfwLevel: int

    modelVersions: list[CivitaiModelVersion]



