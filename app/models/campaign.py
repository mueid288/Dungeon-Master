from sqlalchemy import Column, Integer, String, DateTime,ForeignKey
from ..database import Base
from sqlalchemy.orm import relationship
from datetime import datetime,timezone

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer,primary_key=True)
    name = Column(String, nullable=False)
    theme = Column(String)        # fantasy/sci-fi/horror
    summary = Column(String)      # starts empty, gets updated
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # FK → users
    created_at = Column(DateTime, default= lambda:datetime.now(timezone.utc))
    players = relationship("CampaignPlayer", back_populates="campaign")
    memories = relationship("Memory", back_populates="campaign")