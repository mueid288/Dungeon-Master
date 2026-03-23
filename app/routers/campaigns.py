from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..core.security import verify_token
from ..models.campaign import Campaign
from ..models.campaign_players import CampaignPlayer
from ..schemas.campaign import CampaignCreate, CampaignJoin, CampaignResponse, CampaignSummary, PlayerInCampaign
from ..models.campaign_players import CampaignPlayer
from ..models.memory import Memory
from ..models.characters import Character

router = APIRouter(prefix="/campaign",tags=["Campaign"])

@router.post("/create",response_model=CampaignResponse)
def create_campaign(payload: CampaignCreate, user_Id:int=Depends(verify_token),db:Session=Depends(get_db)):
    set_campaign = Campaign(
        name = payload.name,
        theme = payload.theme,
        created_by = user_Id
    )
    db.add(set_campaign)
    db.flush()

    set_player = CampaignPlayer(
        user_id = user_Id,
        campaign_id = set_campaign.id,
        role = "admin"
    )

    db.add(set_player)
    db.commit()
    db.refresh(set_campaign)

    return set_campaign

@router.post("/join",response_model=PlayerInCampaign)
def join_campaign(payload: CampaignJoin, user_Id:int=Depends(verify_token),db:Session=Depends(get_db)):
    current_campaign = db.query(Campaign).filter(Campaign.id == payload.campaign_id).first()
    if current_campaign:
        check_player = db.query(CampaignPlayer).filter(CampaignPlayer.campaign_id == payload.campaign_id,CampaignPlayer.user_id == user_Id).first()
        if check_player:
            raise HTTPException(status_code=409,detail="Player already in the Campaign")
        else:
            player_count = db.query(CampaignPlayer).filter(CampaignPlayer.campaign_id == payload.campaign_id).count()
            if player_count >= 4:
              raise HTTPException(status_code=400, detail="Campaign is full")
            else:
                set_player = CampaignPlayer(
                    user_id = user_Id,
                    campaign_id = payload.campaign_id,
                    role = "player"
                )
                db.add(set_player)
                db.commit()
                db.refresh(set_player)

                return set_player
    else:
        raise HTTPException(status_code=404, detail="Campaign Not Found")
    
@router.get("/my",response_model=list[CampaignSummary])
def get_my_campaigns(user_Id:int=Depends(verify_token),db:Session=Depends(get_db)):
    list_campaigns = db.query(Campaign).join(CampaignPlayer).filter(CampaignPlayer.user_id == user_Id).all()
    return list_campaigns

@router.get("/{campaign_id}",response_model=CampaignResponse)
def get_campaign(campaign_id:int,user_Id:int=Depends(verify_token),db:Session=Depends(get_db)):
    list_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not list_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return list_campaign

@router.get("/{campaign_id}/export")
def export_story(campaign_id:int,user_Id:int= Depends(verify_token),db:Session=Depends(get_db)):
     current_character = db.query(Character).filter(Character.user_id == user_Id).first()
     current_campaign = db.query(Campaign).join(CampaignPlayer).filter(CampaignPlayer.campaign_id == campaign_id , CampaignPlayer.user_id == user_Id).first()

    #  if current_campaign.status != "Active":
    #       raise HTTPException(status_code=400,detail=f"Game already ended — status: {current_campaign.status}")
     
     memories = db.query(Memory).filter(Memory.campaign_id == current_campaign.id).all()

    #  return current_character
     #return current_campaign
     return memories