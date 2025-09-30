from pydantic import BaseModel
from datetime import date
from typing import Optional
from enum import Enum

class MovementType(str, Enum):
    deposit = "deposit"
    withdrawal = "withdrawal"

class MovementBase(BaseModel):
    client_id: int
    type: MovementType
    amount: float
    date: date
    note: Optional[str] = None

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