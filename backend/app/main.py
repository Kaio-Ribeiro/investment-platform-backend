from fastapi import FastAPI
from app.core.database import engine
from app.models.base import Base

app = FastAPI(title="Investment API", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Investment API is running!"}