from fastapi import APIRouter,Depends,HTTPException
from fastapi.security import OAuth2PasswordBearer
from ..database import get_db
from sqlalchemy.orm import Session

from ..core.security import verify_token
from ..models.characters import Character
from ..models.users import User
from ..schemas.character import CharacterCreate, CharacterResponse, CharacterUpdate

oauth2_scheme = OAuth2PasswordBearer("/me")

router = APIRouter(prefix="/character", tags=["Character"])

@router.post("/create", response_model=CharacterResponse)
async def create_character(payload: CharacterCreate,token:str = Depends(oauth2_scheme) ,db:Session= Depends(get_db)):
 
    current_user = verify_token(token)
    db_user = db.query(User).filter(current_user == User.id).first()
    if db_user is not None :
        new_character = Character(
            name= payload.name,
            char_class= payload.char_class
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