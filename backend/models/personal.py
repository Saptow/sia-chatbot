from pydantic import BaseModel
from enum import StrEnum

from backend.models.roster import Roster

## Enums TODO: Expandable for other roles in future ##
class Role(StrEnum):
    ATC='Air Traffic Controller'


class Personnel(BaseModel):
    user_id: int
    position: Role
    age: int
    gender: str # 'M' or 'F'
    roster_info: Roster
    personal_info: dict
