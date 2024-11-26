from data_type.base import PydanticModel


class ModelDir(PydanticModel):
    model_type: str
    dirs: list[str] = []
    default_dir: str

