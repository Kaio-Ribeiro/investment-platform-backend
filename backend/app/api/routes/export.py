from fastapi import APIRouter, Depends, Query
from datetime import date
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.services.export_service import export_service

router = APIRouter()

@router.get("/clients/csv")
async def export_clients_csv(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await export_service.export_clients_to_csv(db)

@router.get("/allocations/csv")
async def export_allocations_csv(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await export_service.export_allocations_to_csv(db)

@router.get("/movements/csv")
async def export_movements_csv(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await export_service.export_movements_to_csv(db, start_date, end_date)