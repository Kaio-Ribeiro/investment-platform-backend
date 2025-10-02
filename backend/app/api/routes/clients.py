from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import json

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.db_helpers import DBHelper
from app.models.client import Client
from app.models.user import User
from app.schemas.client import Client as ClientSchema, ClientCreate, ClientUpdate

router = APIRouter()

def serialize_json_fields(client_data: dict) -> dict:
    """Convert list fields to JSON strings for database storage"""
    if 'investment_goals' in client_data and isinstance(client_data['investment_goals'], list):
        client_data['investment_goals'] = json.dumps(client_data['investment_goals'])
    if 'tags' in client_data and isinstance(client_data['tags'], list):
        client_data['tags'] = json.dumps(client_data['tags'])
    return client_data

def deserialize_json_fields(client) -> dict:
    """Convert JSON strings back to lists for API response"""
    client_dict = {column.name: getattr(client, column.name) for column in client.__table__.columns}
    
    # Parse JSON fields
    if client_dict.get('investment_goals'):
        try:
            client_dict['investment_goals'] = json.loads(client_dict['investment_goals'])
        except (json.JSONDecodeError, TypeError):
            client_dict['investment_goals'] = []
    else:
        client_dict['investment_goals'] = []
        
    if client_dict.get('tags'):
        try:
            client_dict['tags'] = json.loads(client_dict['tags'])
        except (json.JSONDecodeError, TypeError):
            client_dict['tags'] = []
    else:
        client_dict['tags'] = []
    
    # Handle None values for required string fields
    if client_dict.get('created_by') is None:
        client_dict['created_by'] = 'system'
    
    # Ensure other fields have proper defaults
    client_dict.setdefault('status', 'active')
    client_dict.setdefault('investment_profile', 'not_defined')
    client_dict.setdefault('investment_experience', 'beginner')
    client_dict.setdefault('country', 'Brasil')
    
    return client_dict

@router.get("/", response_model=list[ClientSchema])
async def read_clients(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    status: Optional[str] = Query(None),
    investment_profile: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db = Depends(get_db)
):
    import time
    start_time = time.time()
    
    query = select(Client)
    
    # Search in name, email, or CPF - optimized with indexes
    if search and search.strip():  # Only search if not empty
        search_term = f"%{search.strip()}%"
        query = query.where(
            Client.name.ilike(search_term) | 
            Client.email.ilike(search_term) |
            Client.cpf.ilike(search_term)
        )
    
    if is_active is not None:
        query = query.where(Client.is_active == is_active)
        
    if status:
        query = query.where(Client.status == status)
        
    if investment_profile:
        query = query.where(Client.investment_profile == investment_profile)
    
    # Add ordering for consistent results
    query = query.order_by(Client.name.asc()).offset(skip).limit(limit)
    
    if isinstance(db, AsyncSession):
        result = await db.execute(query)
        clients = result.scalars().all()
    else:
        result = db.execute(query)
        clients = result.scalars().all()
    
    # Convert to dictionaries with proper JSON field parsing
    clients_data = []
    for client in clients:
        client_dict = deserialize_json_fields(client)
        clients_data.append(ClientSchema(**client_dict))
    
    return clients_data

@router.post("/", response_model=ClientSchema)
async def create_client(
    client: ClientCreate, 
    current_user: User = Depends(get_current_active_user),
    db = Depends(get_db)
):
    # Convert client data to dict and serialize JSON fields
    client_data = client.model_dump()
    client_data = serialize_json_fields(client_data)
    client_data['created_by'] = current_user.email
    
    db_client = Client(**client_data)
    created_client = await DBHelper.add_and_commit(db, db_client)
    
    # Return with properly parsed JSON fields
    client_dict = deserialize_json_fields(created_client)
    return ClientSchema(**client_dict)

@router.get("/{client_id}", response_model=ClientSchema)
async def read_client(
    client_id: int, 
    current_user: User = Depends(get_current_active_user),
    db = Depends(get_db)
):
    client = await DBHelper.get_by_id(db, Client, client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Return with properly parsed JSON fields
    client_dict = deserialize_json_fields(client)
    return ClientSchema(**client_dict)

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
    
    # Serialize JSON fields in update data
    update_data = client_update.model_dump(exclude_unset=True)
    update_data = serialize_json_fields(update_data)
    
    for field, value in update_data.items():
        setattr(client, field, value)
    
    await DBHelper.commit(db)
    await DBHelper.refresh(db, client)
    
    # Return with properly parsed JSON fields
    client_dict = deserialize_json_fields(client)
    return ClientSchema(**client_dict)

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