from pydantic import BaseModel
from datetime import date
from typing import Optional

class AllocationBase(BaseModel):
    client_id: int
    asset_id: int
    quantity: float
    buy_price: float
    buy_date: date

class AllocationCreate(AllocationBase):
    pass

class AllocationUpdate(BaseModel):
    quantity: Optional[float] = None
    buy_price: Optional[float] = None
    buy_date: Optional[date] = None

class Allocation(AllocationBase):
    id: int

    class Config:
        from_attributes = True

class AllocationWithDetails(Allocation):
    client_name: str
    asset_ticker: str
    asset_name: str
    total_invested: float