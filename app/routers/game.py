from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from ..core.dungeon_master import ask_dungeon_master, start_game
from ..database import get_db
from ..core.security import verify_token
from ..schemas.game import PlayerAction, GameStart
from ..models.campaign import Campaign
from ..models.campaign_players import CampaignPlayer
from ..models.characters import Character
from ..models.memory import Memory
from ..models.inventory import Inventory
from ..models.users import User

router = APIRouter(prefix="/game",tags=["Game"])

@router.post("/action")
def game_action(payload:PlayerAction,user_Id:int=Depends(verify_token),db:Session=Depends(get_db)):
    query = select(Character).where(
            Character.id == payload.character_id,
            Character.user_id == user_Id
        )
    current_character = db.execute(query).scalar_one_or_none()
    if not current_character:
                raise HTTPException(status_code=404,detail="Character Not Found")
    current_campaign = db.query(Campaign).join(CampaignPlayer).filter(CampaignPlayer.campaign_id == payload.campaign_id,CampaignPlayer.user_id == user_Id).first()
    if not current_campaign:
                raise HTTPException(status_code=404,detail="Player not in the Campaign")
    
    recent_memories = db.query(Memory)\
                        .filter(Memory.campaign_id == payload.campaign_id)\
                        .order_by(Memory.created_at.desc())\
                        .limit(5)\
                        .all()
    critical_memories = db.query(Memory)\
                        .filter(
                            Memory.campaign_id == payload.campaign_id,
                            Memory.importance.in_(["critical", "high"])
                        )\
                        .order_by(Memory.created_at.asc())\
                    .all()
    result = ask_dungeon_master(current_character,current_campaign,recent_memories,critical_memories,payload.player_action)

    current_campaign.action_count +=1
    if current_character.health <=0:
           current_character.health = 0
           current_campaign.status = "Failed"

    if result.get("quest_completed"):
           current_campaign.status = "Completed"

    if result.get("game_over"):
           current_campaign.status = "Failed"

    if current_campaign.status != "active":
           raise HTTPException(status_code=400, detail=f"Game already ended — status: {current_campaign.status}") 

    if result["damage_taken"] > 0:
            current_character.health -= int(result["damage_taken"])
    if result["xp_gained"] > 0:
            current_character.xp += int(result["xp_gained"])

    xp_needed = current_character.level * 100
    if current_character.xp >= xp_needed:
            current_character.level += 1
            current_character.max_health += 50
            current_character.health = current_character.max_health

    db.add(current_character)

    if result["item_gained"]:
            existing_item = db.query(Inventory).filter(Inventory.character_id == current_character.id, Inventory.item_name == result["item_gained"]).first()
            if existing_item:
                    existing_item.quantity += 1
            else:
             new_item = Inventory(
                     character_id = current_character.id,
                     item_name = result["item_gained"]
             )
             db.add(new_item)

    if result["item_lost"]:
            existing = db.query(Inventory).filter(Inventory.character_id == current_character.id, Inventory.item_name == result["item_lost"]).first()
            if existing:
                    if existing.quantity > 1:
                            existing.quantity -=1
                    else:
                        db.delete(existing)

    new_memory = Memory(
        campaign_id=payload.campaign_id,
        character_id=current_character.id,
        action=payload.player_action,
        ai_response=result["narrative"],
        importance=result["importance"]
    )

    db.add(new_memory)

    if result["world_update"]:
           current_campaign.summary = f"{current_campaign.summary or ''} \n {result['world_update']}"


    db.commit()
    db.refresh(current_character)

    return result

@router.post("/start")
def start_game_route(payload: GameStart, user_Id: int = Depends(verify_token), db: Session = Depends(get_db)):
    list_campaign = db.query(Campaign).filter(Campaign.id == payload.campaign_id).first()
    if not list_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    already_started = db.query(Memory).filter(
    Memory.campaign_id == payload.campaign_id,
    Memory.action == "[GAME START]"
    ).first() 
    if already_started:
           raise HTTPException(status_code=409,detail="Game Already Started")
    
    characters = db.query(Character)\
    .join(User, User.id == Character.user_id)\
    .join(CampaignPlayer, CampaignPlayer.user_id == User.id)\
    .filter(CampaignPlayer.campaign_id == payload.campaign_id)\
    .all()
    if not characters:
        raise HTTPException(status_code=400, detail="No characters found in campaign")
    
    result = start_game(characters,list_campaign)

    list_campaign.main_quest = result["main_quest"]
    list_campaign.villain = result["villain"]
    db.commit()

    for character in characters:
        new_memory = Memory(
            campaign_id=payload.campaign_id,
            character_id=character.id,
            action="[GAME START]",
            ai_response=result["opening"],
            importance="critical")

        db.add(new_memory)

    db.commit()
    return result