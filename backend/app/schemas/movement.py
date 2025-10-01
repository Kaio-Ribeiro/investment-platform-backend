from pydantic import BaseModel, Field, validator
from datetime import date
from typing import Optional
from enum import Enum

class MovementType(str, Enum):
    deposit = "deposit"
    withdrawal = "withdrawal"

class MovementBase(BaseModel):
    client_id: int = Field(..., gt=0, description="Client ID must be greater than 0")
    type: MovementType
    amount: float = Field(..., gt=0, description="Amount must be greater than 0")
    date: date
    note: Optional[str] = Field(None, max_length=500, description="Note cannot exceed 500 characters")
    
    @validator('date')
    def validate_date(cls, v):
        if v > date.today():
            raise ValueError('Movement date cannot be in the future')
        return v

class MovementCreate(MovementBase):
    pass

class Movement(MovementBase):
    id: int

    class Config:
        from_attributes = True

class MovementWithDetails(Movement):
    client_name: str

class CaptationSummary(BaseModel):
    total_deposits: float
    total_withdrawals: float
    net_captation: float
    period_start: date
    period_end: date