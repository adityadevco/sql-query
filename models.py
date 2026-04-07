from pydantic import BaseModel
from typing import List, Optional


class Observation(BaseModel):
    query: str
    stage: str
    history: List[str]


class Action(BaseModel):
    intent: Optional[str] = None
    action: Optional[str] = None
    response: Optional[str] = None