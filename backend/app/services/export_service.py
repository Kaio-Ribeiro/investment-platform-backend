import csv
import io
from datetime import date
from typing import List, Dict, Any, Union
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.models.client import Client
from app.models.allocation import Allocation
from app.models.movement import Movement, MovementType
from app.models.asset import Asset
from app.core.db_helpers import DBHelper

class ExportService:
    @staticmethod
    async def export_clients_to_csv(db: Union[AsyncSession, Session]) -> StreamingResponse:
        clients = await DBHelper.get_all(db, Client)
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(["ID", "Name", "Email", "Status", "Created At"])
        
        # Data
        for client in clients:
            writer.writerow([
                client.id,
                client.name,
                client.email,
                "Active" if client.is_active else "Inactive",
                client.created_at.isoformat()
            ])
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=clients.csv"}
        )
    
    @staticmethod
    async def export_assets_to_csv(db: Union[AsyncSession, Session]) -> StreamingResponse:
        assets = await DBHelper.get_all(db, Asset)
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(["ID", "Ticker", "Name", "Exchange", "Currency"])
        
        # Data
        for asset in assets:
            writer.writerow([
                asset.id,
                asset.ticker,
                asset.name,
                asset.exchange or "",
                asset.currency
            ])
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=assets.csv"}
        )
    
    @staticmethod
    async def export_allocations_to_csv(db: Union[AsyncSession, Session]) -> StreamingResponse:
        query = (
            select(
                Allocation,
                Client.name.label("client_name"),
                Asset.ticker.label("asset_ticker"),
                Asset.name.label("asset_name")
            )
            .join(Client, Allocation.client_id == Client.id)
            .join(Asset, Allocation.asset_id == Asset.id)
        )
        
        result = await DBHelper.execute_query(db, query)
        allocations = result.all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "ID", "Client", "Asset Ticker", "Asset Name", 
            "Quantity", "Buy Price", "Total Invested", "Buy Date"
        ])
        
        # Data
        for alloc in allocations:
            total_invested = float(alloc.Allocation.quantity * alloc.Allocation.buy_price)
            writer.writerow([
                alloc.Allocation.id,
                alloc.client_name,
                alloc.asset_ticker,
                alloc.asset_name,
                float(alloc.Allocation.quantity),
                float(alloc.Allocation.buy_price),
                total_invested,
                alloc.Allocation.buy_date.isoformat()
            ])
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=allocations.csv"}
        )
    
    @staticmethod
    async def export_movements_to_csv(
        db: Union[AsyncSession, Session], 
        start_date: date = None, 
        end_date: date = None
    ) -> StreamingResponse:
        query = (
            select(Movement, Client.name.label("client_name"))
            .join(Client, Movement.client_id == Client.id)
        )
        
        if start_date:
            query = query.where(Movement.date >= start_date)
        if end_date:
            query = query.where(Movement.date <= end_date)
        
        result = await DBHelper.execute_query(db, query)
        movements = result.all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(["ID", "Client", "Type", "Amount", "Date", "Note"])
        
        # Data
        for mov in movements:
            writer.writerow([
                mov.Movement.id,
                mov.client_name,
                mov.Movement.type.value,
                float(mov.Movement.amount),
                mov.Movement.date.isoformat(),
                mov.Movement.note or ""
            ])
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=movements.csv"}
        )

export_service = ExportService()