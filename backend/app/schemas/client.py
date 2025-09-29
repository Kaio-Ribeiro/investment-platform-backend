from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ClientBase(BaseModel):
    name: str
    email: str
    is_active: bool = True

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None

class Client(ClientBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True