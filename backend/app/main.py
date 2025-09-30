from fastapi import FastAPI
from app.api.routes import auth, users, clients, assets, allocations, movements, export

app = FastAPI(title="Investment API", version="1.0.0")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(clients.router, prefix="/clients", tags=["clients"])
app.include_router(assets.router, prefix="/assets", tags=["assets"])
app.include_router(allocations.router, prefix="/allocations", tags=["allocations"])
app.include_router(movements.router, prefix="/movements", tags=["movements"])
app.include_router(export.router, prefix="/export", tags=["export"])

@app.get("/")
async def root():
    return {"message": "Investment API is running!"}