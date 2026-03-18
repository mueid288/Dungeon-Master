from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from ..database import Base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

class CampaignPlayer(Base):
    __tablename__ = "campaign_players"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    role = Column(String, nullable=False)
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="campaigns")
    campaign = relationship("Campaign", back_populates="players")