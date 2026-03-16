from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CharacterCreate(BaseModel):
    name: str
    char_class: str  # warrior/mage/rogue

class CharacterUpdate(BaseModel):
    health: Optional[float] = None
    xp: Optional[float] = None
    level: Optional[int] = None

class CharacterResponse(BaseModel):
    id: int
    name: str
    char_class: str
    health: float
    max_health: float
    xp: float
    level: int
    created_at: datetime

    class Config:
        from_attributes = True