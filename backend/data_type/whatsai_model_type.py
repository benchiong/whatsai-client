from typing import Literal

from data_type.base import PydanticModel


ModelTypeLiteral = Literal['system', 'custom']

class ModelType(PydanticModel):
    type_name: str
    source: ModelTypeLiteral


initial_model_types = [
    'checkpoint',
    'clip',
    'clip_vision',
    'controlnet',
    'embedding',
    'upscaler',
    'gligen',
    'hypernet',
    'inpainting',
    'lora',
    'vae',
    'vae-approx',
    'others'
]
