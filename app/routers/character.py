from fastapi import APIRouter,Depends,HTTPException
from fastapi.security import OAuth2PasswordBearer
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..core.security import verify_token
from ..models.characters import Character
from ..models.users import User
from ..schemas.character import CharacterCreate, CharacterResponse, CharacterUpdate

oauth2_scheme = OAuth2PasswordBearer("/me")

router = APIRouter(prefix="/character", tags=["Character"])

@router.post("/create", response_model=CharacterResponse)
def create_character(payload: CharacterCreate,user_id: int= Depends(verify_token) ,db:Session= Depends(get_db)):

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