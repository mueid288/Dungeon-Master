from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from datetime import datetime, timezone
from ..database import Base
from sqlalchemy.orm import relationship
class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer,primary_key=True)
    character_id = Column(Integer,ForeignKey("characters.id"))
    item_name = Column(String)
    quantity = Column(Integer, default=1)

    character = relationship("Character", back_populates="inventory")