from fastapi import FastAPI
from app.api.routes import auth

app = FastAPI(title="Investment API", version="1.0.0")

app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "Investment API is running!"}