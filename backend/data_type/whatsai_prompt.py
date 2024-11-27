from typing import Optional

from pydantic import BaseModel


class Prompt(BaseModel):
    card_name: str
    base_inputs: dict
    addon_inputs: Optional[dict] = None
