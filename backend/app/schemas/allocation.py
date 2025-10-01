from pydantic import BaseModel, Field, validator
from datetime import date
from typing import Optional

class AllocationBase(BaseModel):
    client_id: int = Field(..., gt=0, description="Client ID must be greater than 0")
    asset_id: int = Field(..., gt=0, description="Asset ID must be greater than 0")
    quantity: float = Field(..., gt=0, description="Quantity must be greater than 0")
    buy_price: float = Field(..., gt=0, description="Buy price must be greater than 0")
    buy_date: date
    
    @validator('buy_date')
    def validate_buy_date(cls, v):
        if v > date.today():
            raise ValueError('Buy date cannot be in the future')
        return v

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