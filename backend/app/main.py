from fastapi import FastAPI
from app.api.routes import auth, users, clients

app = FastAPI(title="Investment API", version="1.0.0")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(clients.router, prefix="/clients", tags=["clients"])

@app.get("/")
async def root():
    return {"message": "Investment API is running!"}