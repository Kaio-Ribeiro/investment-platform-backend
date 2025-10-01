from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List, Optional, Union

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.db_helpers import DBHelper
from app.models.allocation import Allocation
from app.models.client import Client
from app.models.asset import Asset
from app.models.user import User
from app.schemas.allocation import Allocation as AllocationSchema, AllocationCreate, AllocationUpdate, AllocationWithDetails

router = APIRouter()

@router.get("/", response_model=List[AllocationWithDetails])
async def read_allocations(
    client_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Union[AsyncSession, Session] = Depends(get_db)
):
    # Criar query base
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
    
    # Executar query usando DBHelper
    result = await DBHelper.execute_query(db, query)
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

@router.get("/total-allocation")
async def get_total_allocation(
    current_user: User = Depends(get_current_active_user),
    db: Union[AsyncSession, Session] = Depends(get_db)
):
    result = await DBHelper.execute_query(
        db,
        select(func.sum(Allocation.quantity * Allocation.buy_price))
    )
    total = result.scalar() or 0
    return {"total_allocation": float(total)}

@router.get("/{allocation_id}", response_model=AllocationSchema)
async def read_allocation(
    allocation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Union[AsyncSession, Session] = Depends(get_db)
):
    allocation = await DBHelper.get_by_id(db, Allocation, allocation_id)
    if allocation is None:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return allocation

@router.post("/", response_model=AllocationSchema)
async def create_allocation(
    allocation: AllocationCreate, 
    current_user: User = Depends(get_current_active_user),
    db: Union[AsyncSession, Session] = Depends(get_db)
):
    # Verificar se cliente existe e está ativo
    client_result = await DBHelper.execute_query(db, select(Client).where(Client.id == allocation.client_id))
    client = client_result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    if not client.is_active:
        raise HTTPException(status_code=400, detail="Cannot create allocation for inactive client")
    
    # Verificar se asset existe
    asset_result = await DBHelper.execute_query(db, select(Asset).where(Asset.id == allocation.asset_id))
    asset = asset_result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Validações de negócio
    if allocation.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than zero")
    if allocation.buy_price <= 0:
        raise HTTPException(status_code=400, detail="Buy price must be greater than zero")
    
    db_allocation = Allocation(**allocation.dict())
    return await DBHelper.add_and_commit(db, db_allocation)

@router.put("/{allocation_id}", response_model=AllocationSchema)
async def update_allocation(
    allocation_id: int,
    allocation: AllocationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Union[AsyncSession, Session] = Depends(get_db)
):
    # Buscar allocation existente
    db_allocation = await DBHelper.get_by_id(db, Allocation, allocation_id)
    if db_allocation is None:
        raise HTTPException(status_code=404, detail="Allocation not found")
    
    # Atualizar campos se fornecidos
    update_data = allocation.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_allocation, key, value)
    
    await DBHelper.commit(db)
    await DBHelper.refresh(db, db_allocation)
    return db_allocation

@router.delete("/{allocation_id}")
async def delete_allocation(
    allocation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Union[AsyncSession, Session] = Depends(get_db)
):
    allocation = await DBHelper.get_by_id(db, Allocation, allocation_id)
    if allocation is None:
        raise HTTPException(status_code=404, detail="Allocation not found")
    
    await DBHelper.delete_obj(db, allocation)
    return {"detail": "Allocation deleted successfully"}

@router.get("/client/{client_id}/allocation")
async def get_client_allocation(
    client_id: int, 
    current_user: User = Depends(get_current_active_user),
    db: Union[AsyncSession, Session] = Depends(get_db)
):
    result = await DBHelper.execute_query(
        db,
        select(func.sum(Allocation.quantity * Allocation.buy_price))
        .where(Allocation.client_id == client_id)
    )
    total = result.scalar() or 0
    return {"client_id": client_id, "total_allocation": float(total)}

@router.get("/client/{client_id}", response_model=List[AllocationWithDetails])
async def get_allocations_by_client(
    client_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Union[AsyncSession, Session] = Depends(get_db)
):
    # Verificar se cliente existe
    client = await DBHelper.get_by_id(db, Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Buscar allocations do cliente
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
        .where(Allocation.client_id == client_id)
    )
    
    result = await DBHelper.execute_query(db, query)
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