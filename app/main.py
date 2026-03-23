from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from .routers import auth, campaigns, character, game
from .database import Base, engine

from .models import users, characters, inventory, campaign, campaign_players, memory
     
app = FastAPI(title="Dungeon Master")

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(character.router)
app.include_router(campaigns.router)
app.include_router(game.router)