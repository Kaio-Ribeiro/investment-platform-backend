from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import date, datetime, timedelta
from typing import List, Optional

from app.core.database import get_db
from app.models.movement import Movement, MovementType
from app.models.client import Client
from app.schemas.movement import Movement as MovementSchema, MovementCreate, MovementWithDetails, CaptationSummary

router = APIRouter()

@router.get("/", response_model=List[MovementWithDetails])
async def read_movements(
    client_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Movement, Client.name.label("client_name"))
        .join(Client, Movement.client_id == Client.id)
    )
    
    if client_id:
        query = query.where(Movement.client_id == client_id)
    
    if start_date:
        query = query.where(Movement.date >= start_date)
    
    if end_date:
        query = query.where(Movement.date <= end_date)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    movements = result.all()
    
    return [
        MovementWithDetails(
            id=mov.Movement.id,
            client_id=mov.Movement.client_id,
            type=mov.Movement.type,
            amount=float(mov.Movement.amount),
            date=mov.Movement.date,
            note=mov.Movement.note,
            client_name=mov.client_name
        )
        for mov in movements
    ]

@router.post("/", response_model=MovementSchema)
async def create_movement(movement: MovementCreate, db: AsyncSession = Depends(get_db)):
    # Verificar se cliente existe
    client_result = await db.execute(select(Client).where(Client.id == movement.client_id))
    client = client_result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db_movement = Movement(**movement.dict())
    db.add(db_movement)
    await db.commit()
    await db.refresh(db_movement)
    return db_movement

@router.get("/captation-total", response_model=CaptationSummary)
async def get_total_captation(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    # Se não fornecer datas, usa último mês
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Total deposits
    deposits_result = await db.execute(
        select(func.sum(Movement.amount))
        .where(
            Movement.type == MovementType.deposit,
            Movement.date >= start_date,
            Movement.date <= end_date
        )
    )
    total_deposits = deposits_result.scalar() or 0
    
    # Total withdrawals
    withdrawals_result = await db.execute(
        select(func.sum(Movement.amount))
        .where(
            Movement.type == MovementType.withdrawal,
            Movement.date >= start_date,
            Movement.date <= end_date
        )
    )
    total_withdrawals = withdrawals_result.scalar() or 0
    
    return CaptationSummary(
        total_deposits=float(total_deposits),
        total_withdrawals=float(total_withdrawals),
        net_captation=float(total_deposits - total_withdrawals),
        period_start=start_date,
        period_end=end_date
    )

@router.get("/captation-by-client")
async def get_captation_by_client(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Captação por cliente
    query = (
        select(
            Client.id,
            Client.name,
            func.sum(
                func.case(
                    (Movement.type == MovementType.deposit, Movement.amount),
                    else_=0
                )
            ).label("total_deposits"),
            func.sum(
                func.case(
                    (Movement.type == MovementType.withdrawal, Movement.amount),
                    else_=0
                )
            ).label("total_withdrawals")
        )
        .select_from(Movement)
        .join(Client, Movement.client_id == Client.id)
        .where(Movement.date >= start_date, Movement.date <= end_date)
        .group_by(Client.id, Client.name)
    )
    
    result = await db.execute(query)
    captation_data = result.all()
    
    return [
        {
            "client_id": row.id,
            "client_name": row.name,
            "total_deposits": float(row.total_deposits or 0),
            "total_withdrawals": float(row.total_withdrawals or 0),
            "net_captation": float((row.total_deposits or 0) - (row.total_withdrawals or 0))
        }
        for row in captation_data
    ]