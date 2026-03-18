from fastapi import FastAPI
from .routers import auth,character
from .database import Base, engine

from .models import users, characters, inventory, campaign, campaign_players, memory
     
app = FastAPI(title="Dungeon Master")

app.include_router(auth.router)
app.include_router(character.router)