from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.asset import Asset
from app.models.user import User
from app.schemas.asset import Asset as AssetSchema, AssetCreate, YahooFinanceAsset
from app.services.yahoo_finance import yahoo_finance

router = APIRouter()

@router.get("/", response_model=list[AssetSchema])
async def read_assets(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Asset).offset(skip).limit(limit))
    assets = result.scalars().all()
    return assets

@router.get("/search-yahoo/{symbol}", response_model=Optional[YahooFinanceAsset])
async def search_yahoo_asset(
    symbol: str,
    current_user: User = Depends(get_current_active_user)
):
    asset_data = await yahoo_finance.search_asset(symbol)
    return asset_data

@router.post("/from-yahoo/{symbol}", response_model=AssetSchema)
async def create_asset_from_yahoo(
    symbol: str, 
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # Verificar se asset já existe
    result = await db.execute(select(Asset).where(Asset.ticker == symbol.upper()))
    existing_asset = result.scalar_one_or_none()
    
    if existing_asset:
        return existing_asset
    
    # Buscar dados do Yahoo Finance
    asset_data = await yahoo_finance.search_asset(symbol)
    if not asset_data:
        raise HTTPException(status_code=404, detail="Asset not found on Yahoo Finance")
    
    # Criar asset no banco
    db_asset = Asset(**asset_data)
    db.add(db_asset)
    await db.commit()
    await db.refresh(db_asset)
    return db_asset

@router.post("/", response_model=AssetSchema)
async def create_asset(
    asset: AssetCreate, 
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # Verificar se ticker já existe
    result = await db.execute(select(Asset).where(Asset.ticker == asset.ticker))
    existing_asset = result.scalar_one_or_none()
    
    if existing_asset:
        raise HTTPException(status_code=400, detail="Asset with this ticker already exists")
    
    db_asset = Asset(**asset.dict())
    db.add(db_asset)
    await db.commit()
    await db.refresh(db_asset)
    return db_asset

@router.get("/{asset_id}", response_model=AssetSchema)
async def read_asset(
    asset_id: int, 
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset