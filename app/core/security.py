from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

load_dotenv()

ALGORITHM  = os.getenv("ALGORITHM")
EXPIRY = os.getenv("ACCESS_TOKEN_EXPIRE_DAYS")
SECRETKEY = os.getenv("SECRET_KEY")

pwd_context = CryptContext(schemes=["bcrypt"])

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain,hashed)


# JWT
def create_token(user_id: int):
    payload= {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(days=int(EXPIRY))
        }

    return jwt.encode(payload,SECRETKEY,algorithm=ALGORITHM)

async def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRETKEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError:
        raise credentials_exception
