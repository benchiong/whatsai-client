from pydantic import BaseModel, ConfigDict

class PydanticModel(BaseModel):
    # fix annoying warning:  Field "model_type" in DataModel has conflict with protected namespace "model_".
    model_config = ConfigDict(protected_namespaces=())
