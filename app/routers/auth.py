from fastapi import APIRouter,Depends,HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from ..models.users import User
from ..database import get_db
from ..schemas.user import  UserRegister, UserLogin, UserResponse, TokenResponse
from ..core.security import hash_password, verify_password, create_token, verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/me")

router = APIRouter(prefix="/auth",tags=["auth"])

@router.post("/register",response_model=UserResponse)
async def create_user(payload: UserRegister, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == payload.email).first()
    if db_user:
        raise HTTPException(status_code=409, detail= "User Already Registerd")

    hashedpass= hash_password(payload.password)
    new_user = User(
        email=payload.email,
        hashed_pass=hashedpass
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "email": payload.email,
        "created_at": datetime.now(timezone.utc)

    }

@router.post("/login",response_model=TokenResponse)
async def login_user(payload: UserLogin,db: Session= Depends(get_db)):
    current_user= db.query(User).filter(User.email == payload.email).first()

    if current_user:
        if verify_password(payload.password, current_user.hashed_pass):
            token = create_token(current_user.id)
            return {
               "status": "Login successful",
               "token": token
            }
    if not current_user or not verify_password(payload.password, current_user.hashed_pass):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    

@router.get("/me")
def me(user_id:int = Depends(verify_token),db: Session= Depends(get_db)):
    """
    Retrieve the user record for the authenticated user.
    
    Parameters:
        user_id (int): Authenticated user's id supplied by the `verify_token` dependency.
    
    Returns:
        User or None: The User model instance if found, or `None` if no user exists with the given id.
    
    Raises:
        HTTPException: 404 with detail "User not found" if a database error occurs while fetching the user.
    """
    try:
     get_user = db.query(User).filter(User.id == user_id).first()
     return get_user
    except:
        raise HTTPException(status_code=404,detail="User not found")


