from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CampaignCreate(BaseModel):
    name: str
    theme: str

class CampaignJoin(BaseModel):
    campaign_id: int

class PlayerInCampaign(BaseModel):
    user_id: int
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True

class CampaignResponse(BaseModel):
    id: int
    name: str
    theme: str
    summary: Optional[str] = None   # starts as None
    main_quest: Optional[str] = None
    villain: Optional[str] = None
    status: Optional[str] = None
    action_count: Optional[int] = 0
    created_by: int                  # it's a user id, not a name
    created_at: datetime
    players: List[PlayerInCampaign]

    class Config:
        from_attributes= True


class CampaignSummary(BaseModel):
    id: int
    name: str
    theme: str
    created_at: datetime

    class Config:
        from_attributes = True