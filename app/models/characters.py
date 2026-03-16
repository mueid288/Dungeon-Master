from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from datetime import datetime, timezone
from ..database import Base
from sqlalchemy.orm import relationship, declarative_base


class Character(Base):
    __tablename__ = "characters"

    id= Column(Integer, primary_key=True)
    user_id= Column(Integer, ForeignKey("users.id"))
    name= Column(String)
    char_class= Column(String)
    health= Column(Float,default= 100)
    max_health= Column(Float, default= 100)
    xp= Column(Float, default=0)
    level= Column(Integer, default=1)
    created_at= Column(DateTime, default= lambda: datetime.now(timezone.utc))
    user = relationship("User", back_populates="character", uselist= False)
