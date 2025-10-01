from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.db_helpers import DBHelper
from app.models.client import Client
from app.models.user import User
from app.schemas.client import Client as ClientSchema, ClientCreate, ClientUpdate

router = APIRouter()

@router.get("/", response_model=list[ClientSchema])
async def read_clients(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db = Depends(get_db)
):
    query = select(Client)
    
    if search:
        query = query.where(Client.name.ilike(f"%{search}%") | Client.email.ilike(f"%{search}%"))
    
    if is_active is not None:
        query = query.where(Client.is_active == is_active)
    
    query = query.offset(skip).limit(limit)
    
    if isinstance(db, AsyncSession):
        result = await db.execute(query)
        clients = result.scalars().all()
    else:
        result = db.execute(query)
        clients = result.scalars().all()
    return clients

@router.post("/", response_model=ClientSchema)
async def create_client(
    client: ClientCreate, 
    current_user: User = Depends(get_current_active_user),
    db = Depends(get_db)
):
    db_client = Client(**client.model_dump())
    return await DBHelper.add_and_commit(db, db_client)

@router.get("/{client_id}", response_model=ClientSchema)
async def read_client(
    client_id: int, 
    current_user: User = Depends(get_current_active_user),
    db = Depends(get_db)
):
    client = await DBHelper.get_by_id(db, Client, client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.put("/{client_id}", response_model=ClientSchema)
async def update_client(
    client_id: int, 
    client_update: ClientUpdate, 
    current_user: User = Depends(get_current_active_user),
    db = Depends(get_db)
):
    client = await DBHelper.get_by_id(db, Client, client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    update_data = client_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
    
    await DBHelper.commit(db)
    await DBHelper.refresh(db, client)
    return client

@router.delete("/{client_id}")
async def delete_client(
    client_id: int, 
    current_user: User = Depends(get_current_active_user),
    db = Depends(get_db)
):
    client = await DBHelper.get_by_id(db, Client, client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    await DBHelper.delete_obj(db, client)
    return {"message": "Client deleted successfully"}