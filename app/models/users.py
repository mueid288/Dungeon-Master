from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key= True)
    email = Column(String, unique= True, nullable= False, index= True)
    created_at = Column(DateTime, default= lambda: datetime.now(timezone.utc))
    hashed_pass = Column(String, nullable= False)
    character = relationship("Character", back_populates="user", uselist= False)
    campaigns = relationship("CampaignPlayer", back_populates="user")