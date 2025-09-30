from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List, Optional

from app.core.database import get_db
from app.models.allocation import Allocation
from app.models.client import Client
from app.models.asset import Asset
from app.schemas.allocation import Allocation as AllocationSchema, AllocationCreate, AllocationWithDetails

router = APIRouter()

@router.get("/", response_model=List[AllocationWithDetails])
async def read_allocations(
    client_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(
            Allocation,
            Client.name.label("client_name"),
            Asset.ticker.label("asset_ticker"),
            Asset.name.label("asset_name"),
            (Allocation.quantity * Allocation.buy_price).label("total_invested")
        )
        .join(Client, Allocation.client_id == Client.id)
        .join(Asset, Allocation.asset_id == Asset.id)
    )
    
    if client_id:
        query = query.where(Allocation.client_id == client_id)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    allocations = result.all()
    
    return [
        AllocationWithDetails(
            id=alloc.Allocation.id,
            client_id=alloc.Allocation.client_id,
            asset_id=alloc.Allocation.asset_id,
            quantity=float(alloc.Allocation.quantity),
            buy_price=float(alloc.Allocation.buy_price),
            buy_date=alloc.Allocation.buy_date,
            client_name=alloc.client_name,
            asset_ticker=alloc.asset_ticker,
            asset_name=alloc.asset_name,
            total_invested=float(alloc.total_invested)
        )
        for alloc in allocations
    ]

@router.post("/", response_model=AllocationSchema)
async def create_allocation(allocation: AllocationCreate, db: AsyncSession = Depends(get_db)):
    # Verificar se cliente existe
    client_result = await db.execute(select(Client).where(Client.id == allocation.client_id))
    client = client_result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Verificar se asset existe
    asset_result = await db.execute(select(Asset).where(Asset.id == allocation.asset_id))
    asset = asset_result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    db_allocation = Allocation(**allocation.dict())
    db.add(db_allocation)
    await db.commit()
    await db.refresh(db_allocation)
    return db_allocation

@router.get("/total-allocation")
async def get_total_allocation(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(func.sum(Allocation.quantity * Allocation.buy_price))
    )
    total = result.scalar() or 0
    return {"total_allocation": float(total)}

@router.get("/client/{client_id}/allocation")
async def get_client_allocation(client_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(func.sum(Allocation.quantity * Allocation.buy_price))
        .where(Allocation.client_id == client_id)
    )
    total = result.scalar() or 0
    return {"client_id": client_id, "total_allocation": float(total)}