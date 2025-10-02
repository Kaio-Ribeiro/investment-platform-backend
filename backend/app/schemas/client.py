from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List
import json

class ClientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    cpf: Optional[str] = Field(None, max_length=14)
    rg: Optional[str] = Field(None, max_length=20)
    birth_date: Optional[date] = None
    gender: Optional[str] = Field(None, pattern=r'^(male|female|other)$')
    
    # Contact information
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    
    # Address information
    street: Optional[str] = Field(None, max_length=255)
    number: Optional[str] = Field(None, max_length=20)
    complement: Optional[str] = Field(None, max_length=100)
    neighborhood: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)
    country: Optional[str] = Field("Brasil", max_length=100)
    
    # Investment profile
    investment_profile: Optional[str] = Field("not_defined", pattern=r'^(conservative|moderate|aggressive|not_defined)$')
    risk_tolerance: Optional[int] = Field(5, ge=1, le=10)
    investment_experience: Optional[str] = Field("beginner", pattern=r'^(beginner|intermediate|advanced)$')
    monthly_income: Optional[float] = Field(0.0, ge=0)
    net_worth: Optional[float] = Field(0.0)
    investment_goals: Optional[List[str]] = None
    
    # Status and tracking
    is_active: bool = True
    status: Optional[str] = Field("active", pattern=r'^(active|inactive|prospect|suspended)$')
    last_contact_date: Optional[datetime] = None
    
    # Additional information
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    referral_source: Optional[str] = Field(None, max_length=255)

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    cpf: Optional[str] = Field(None, max_length=14)
    rg: Optional[str] = Field(None, max_length=20)
    birth_date: Optional[date] = None
    gender: Optional[str] = Field(None, pattern=r'^(male|female|other)$')
    
    # Contact information
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    
    # Address information
    street: Optional[str] = Field(None, max_length=255)
    number: Optional[str] = Field(None, max_length=20)
    complement: Optional[str] = Field(None, max_length=100)
    neighborhood: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)
    country: Optional[str] = Field(None, max_length=100)
    
    # Investment profile
    investment_profile: Optional[str] = Field(None, pattern=r'^(conservative|moderate|aggressive|not_defined)$')
    risk_tolerance: Optional[int] = Field(None, ge=1, le=10)
    investment_experience: Optional[str] = Field(None, pattern=r'^(beginner|intermediate|advanced)$')
    monthly_income: Optional[float] = Field(None, ge=0)
    net_worth: Optional[float] = None
    investment_goals: Optional[List[str]] = None
    
    # Status and tracking
    is_active: Optional[bool] = None
    status: Optional[str] = Field(None, pattern=r'^(active|inactive|prospect|suspended)$')
    last_contact_date: Optional[datetime] = None
    
    # Additional information
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    referral_source: Optional[str] = Field(None, max_length=255)

class Client(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = "system"  # Allow None with default

    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm_with_json_fields(cls, obj):
        """Convert SQLAlchemy model to Pydantic with JSON field parsing"""
        data = {}
        for field in cls.__fields__:
            value = getattr(obj, field, None)
            if field in ['investment_goals', 'tags'] and isinstance(value, str):
                try:
                    data[field] = json.loads(value) if value else []
                except json.JSONDecodeError:
                    data[field] = []
            else:
                data[field] = value
        return cls(**data)