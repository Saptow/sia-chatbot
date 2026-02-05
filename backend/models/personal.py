from pydantic import BaseModel
from enum import StrEnum
from typing import Optional, Any

from backend.models.exercise import ExerciseCollection
from backend.models.roster import Roster
from backend.models.sleep import SleepCollection

## Enums TODO: Expandable for other roles in future ##
class Role(StrEnum):
    ATC='Air Traffic Controller'


class Personnel(BaseModel):
    user_id: int
    position: Role
    age: int
    gender: str # 'M' or 'F'
    roster_info: Optional[Roster] = None
    personal_info: Optional[dict[str, Any]] = {}
    exercise_info: Optional[ExerciseCollection] = None
    sleep_info: Optional[SleepCollection] = None