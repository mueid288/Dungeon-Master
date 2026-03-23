from fastapi import APIRouter,Depends,HTTPException
from fastapi.security import OAuth2PasswordBearer
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..core.security import verify_token
from ..models.characters import Character
from ..schemas.character import CharacterCreate, CharacterResponse, CharacterUpdate
from ..models.campaign import Campaign
from ..models.campaign_players import CampaignPlayer
from ..models.memory import Memory


oauth2_scheme = OAuth2PasswordBearer("/me")

router = APIRouter(prefix="/character", tags=["Character"])

@router.post("/create", response_model=CharacterResponse)
def create_character(payload: CharacterCreate,user_id: int= Depends(verify_token) ,db:Session= Depends(get_db)):
    try:
        new_character = Character(
            name= payload.name,
            char_class= payload.char_class,
            user_id= user_id
        )
        db.add(new_character)
        db.commit()
        db.refresh(new_character)

        return{
                "id":new_character.id,
                "name":payload.name,
                "char_class": payload.char_class,
                "health": new_character.health,
                "max_health": new_character.max_health,
                "xp": new_character.xp,
                "level": new_character.level,
                "created_at": new_character.created_at
        }
    except:
         raise HTTPException(status_code=409, detail="Character already Created")

@router.get("/all", response_model=list[CharacterResponse])
def get_characters(user_id: int= Depends(verify_token),db:Session = Depends(get_db)):

    char = db.query(Character).filter(Character.user_id == user_id).all()
    return char

@router.get("/{character_id}")
def get_character(character_id: int,user_id: int= Depends(verify_token),db:Session = Depends(get_db)):

        query = select(Character).where(
            Character.id == character_id,
            Character.user_id == user_id
        )
        char = db.execute(query).scalar_one_or_none()
        if not char:
                raise HTTPException(status_code=404,detail="Character Not Found")
        return char
  

    
@router.patch("/{character_id}")
def update_character(payload:CharacterUpdate,character_id: int, user_id: int= Depends(verify_token), db: Session= Depends(get_db)):
     char = db.execute(
           select(Character).where(
                 Character.id == character_id,
                 Character.user_id == user_id
                   )
                ).scalar_one_or_none()
     if not char:
        raise HTTPException(status_code=404,detail="Character Not Found")
     update_data = payload.model_dump(exclude_unset=True)
     for key, value in update_data.items():
          setattr(char,key,value)
     db.add(char)
     db.commit()
     db.refresh(char)

     return char


@router.get("/{campaign_id}/export")
def export_story(campaign_id:int,user_Id:int= Depends(verify_token),db:Session=Depends(get_db)):
     current_character = db.query(Character).filter(Character.user_id == user_Id).first()
     current_campaign = db.query(Campaign).join(CampaignPlayer).filter(CampaignPlayer.campaign_id == campaign_id , CampaignPlayer.user_id == user_Id).first()

     if current_campaign.status != "Active":
          raise HTTPException(status_code=400,detail=f"Game already ended — status: {current_campaign.status}")
     
     memories = db.query(Memory).filter(Memory.campaign_id == current_campaign.id,Memory.character_id == current_character.id).order_by(Memory.created_at)

     return current_character
     return current_campaign
     return memories
