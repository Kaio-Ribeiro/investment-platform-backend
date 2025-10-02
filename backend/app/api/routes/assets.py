from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.db_helpers import DBHelper
from app.models.asset import Asset
from app.models.user import User
from app.schemas.asset import Asset as AssetSchema, AssetCreate, AssetUpdate, YahooFinanceAsset
from app.services.yahoo_finance import yahoo_finance

router = APIRouter()

@router.get("/", response_model=list[AssetSchema])
async def read_assets(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db = Depends(get_db)
):
    assets = await DBHelper.get_all(db, Asset)
    return assets[skip:skip+limit]

@router.post("/", response_model=AssetSchema)
async def create_asset(
    asset: AssetCreate,
    current_user: User = Depends(get_current_active_user),
    db = Depends(get_db)
):
    db_asset = Asset(**asset.model_dump())
    return await DBHelper.add_and_commit(db, db_asset)

@router.get("/search-yahoo/{symbol}", response_model=Optional[YahooFinanceAsset])
async def search_yahoo_asset(
    symbol: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Busca informações de um ativo no Yahoo Finance
    """
    asset_data = await yahoo_finance.search_asset(symbol)
    return asset_data

@router.get("/history-yahoo/{symbol}")
async def get_yahoo_history(
    symbol: str,
    period: str = "1mo",
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém histórico de preços do Yahoo Finance
    """
    history_data = await yahoo_finance.get_stock_history(symbol, period)
    if not history_data:
        raise HTTPException(status_code=404, detail="Histórico não encontrado")
    return history_data

@router.post("/from-yahoo/{symbol}", response_model=AssetSchema)
async def create_asset_from_yahoo(
    symbol: str, 
    current_user: User = Depends(get_current_active_user),
    db = Depends(get_db)
):
    # Verificar se asset já existe
    existing_assets = await DBHelper.get_by_filter(db, Asset, ticker=symbol.upper())
    
    if existing_assets:
        return existing_assets[0]
    
    # Buscar dados do Yahoo Finance
    asset_data = await yahoo_finance.search_asset(symbol)
    if not asset_data:
        raise HTTPException(status_code=404, detail="Asset not found on Yahoo Finance")
    
    # Criar asset no banco
    db_asset = Asset(**asset_data)
    return await DBHelper.add_and_commit(db, db_asset)

@router.get("/{asset_id}", response_model=AssetSchema)
async def read_asset(
    asset_id: int, 
    current_user: User = Depends(get_current_active_user),
    db = Depends(get_db)
):
    asset = await DBHelper.get_by_id(db, Asset, asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.put("/{asset_id}", response_model=AssetSchema)
async def update_asset(
    asset_id: int,
    asset: AssetUpdate,
    current_user: User = Depends(get_current_active_user),
    db = Depends(get_db)
):
    db_asset = await DBHelper.get_by_id(db, Asset, asset_id)
    if db_asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    for key, value in asset.model_dump(exclude_unset=True).items():
        setattr(db_asset, key, value)
    
    await DBHelper.commit(db)
    await DBHelper.refresh(db, db_asset)
    return db_asset

@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: int,
    current_user: User = Depends(get_current_active_user),
    db = Depends(get_db)
):
    db_asset = await DBHelper.get_by_id(db, Asset, asset_id)
    if db_asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    await DBHelper.delete_obj(db, db_asset)
    return {"ok": True}

@router.get("/{asset_id}/price")
async def get_asset_price(
    asset_id: int,
    current_user: User = Depends(get_current_active_user),
    db = Depends(get_db)
):
    asset = await DBHelper.get_by_id(db, Asset, asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Get current price from Yahoo Finance
    try:
        price_data = await yahoo_finance.get_current_price(asset.ticker)
        return {"asset_id": asset_id, "ticker": asset.ticker, "current_price": price_data}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Unable to fetch current price")