from data_type.base import PydanticModel

class FileSHA256(PydanticModel):
    file_path: str
    sha_256: str

