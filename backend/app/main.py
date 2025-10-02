from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.api.routes import auth, users, clients, assets, allocations, movements, export
from app.core.database import get_db

app = FastAPI(title="Investment API", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint que verifica:
    - Status da aplicação
    - Conectividade com banco de dados
    """
    try:
        # Testar conexão com banco de dados
        await db.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "message": "API is running",
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "message": "API is running but there are issues",
            "database": "disconnected",
            "error": str(e),
            "version": "1.0.0"
        }