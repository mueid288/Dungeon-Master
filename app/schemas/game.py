from pydantic import BaseModel

class PlayerAction(BaseModel):
    campaign_id:int
    character_id:int
    player_action:str

class GameStart(BaseModel):
    campaign_id:int