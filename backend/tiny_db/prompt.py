from typing import Optional

from pydantic import BaseModel


class Prompt(BaseModel):
    class BaseInput(BaseModel):
        checkpoint: dict
        vae_name: Optional[dict] = None
        clip_skip: int
        positive_prompt: str
        negative_prompt: Optional[str] = None
        width: Optional[int] = None
        height: Optional[int] = None
        batch_size: Optional[int] = None
        image_path: Optional[str] = None
        mask_path: Optional[str] = None
        grow_mask_by: Optional[int] = None
        seed: int
        steps: int
        cfg_scale: float
        denoise: float
        sampler_name: str
        scheduler_name: str

    card_name: str
    base_inputs: dict
    addon_inputs: Optional[dict] = None
