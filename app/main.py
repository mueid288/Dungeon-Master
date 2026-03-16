from fastapi import FastAPI
from .routers import auth,character
from .database import Base, engine
# Ensure all ORM models are imported so relationship targets resolve.
from .models import users, characters
     
app = FastAPI(title="Dungeon Master")

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(character.router)