from sqlalchemy import Column, Integer, String, DateTime,ForeignKey
from ..database import Base
from sqlalchemy.orm import relationship
from datetime import datetime,timezone

class Memory(Base):
    __tablename__ = "memory"

    id = Column(Integer,primary_key=True)
    campaign_id = Column(Integer,ForeignKey("campaigns.id"))
    character_id = Column(Integer,ForeignKey("characters.id"))
    action = Column(String)
    ai_response = Column(String)
    importance = Column(String)
    created_at = Column(DateTime, default=lambda:datetime.now(timezone.utc))

    campaign = relationship("Campaign", back_populates="memories")
    character = relationship("Character", back_populates="memories")