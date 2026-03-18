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
    """
    Create a JSON Web Token embedding the given user ID as the token subject and an expiration based on configured settings.
    
    Parameters:
        user_id (int): Identifier to include in the token's `sub` claim.
    
    Returns:
        token (str): Encoded JWT string.
    """
    payload= {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(days=int(EXPIRY))
        }

    return jwt.encode(payload,SECRETKEY,algorithm=ALGORITHM)

def verify_token(token: str = Depends(oauth2_scheme)):
    """
    Validate a Bearer JWT and extract the authenticated user's identifier.
    
    Attempts to decode the provided JWT, verifies the presence of the `sub` claim, and returns its value as the user ID.
    
    Returns:
        user_id (int): The `sub` (subject) claim from the token representing the user identifier.
    
    Raises:
        HTTPException: 401 Unauthorized when the token is missing, invalid, expired, or does not contain a `sub` claim.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRETKEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError:
        raise credentials_exception
    