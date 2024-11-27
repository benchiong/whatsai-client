from enum import Enum
from typing import Literal, Optional

from data_type.base import PydanticModel
from data_type.whatsai_prompt import Prompt

ModelTypeLiteral = Literal['system', 'custom']

class Task(PydanticModel):
    task_id: Optional[int] = None  # take doc_id in tinydb as task_id, filled after saved into tinydb.

    client_id: str
    status: int
    prompt: Prompt
    outputs: Optional[dict] = None
    preview_info: Optional[dict] = None
    created_time_stamp: Optional[int] = None
    created_datetime_str: Optional[str] = None


class TaskStatus(Enum):
    queued = 1
    processing = 2
    canceled = 3
    failed = 4
    finished = 5
