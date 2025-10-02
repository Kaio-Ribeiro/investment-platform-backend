from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text, Float
from sqlalchemy.sql import func
from app.models.base import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    cpf = Column(String(14), unique=True, nullable=True)  # Format: 000.000.000-00
    rg = Column(String(20), nullable=True)
    birth_date = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)  # 'male', 'female', 'other'
    
    # Contact information
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)
    whatsapp = Column(String(20), nullable=True)
    
    # Address information
    street = Column(String(255), nullable=True)
    number = Column(String(20), nullable=True)
    complement = Column(String(100), nullable=True)
    neighborhood = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)  # UF
    zip_code = Column(String(10), nullable=True)  # Format: 00000-000
    country = Column(String(100), default="Brasil", nullable=False)
    
    # Investment profile
    investment_profile = Column(String(20), default="not_defined", nullable=False)  # 'conservative', 'moderate', 'aggressive', 'not_defined'
    risk_tolerance = Column(Integer, default=5)  # 1-10 scale
    investment_experience = Column(String(20), default="beginner", nullable=False)  # 'beginner', 'intermediate', 'advanced'
    monthly_income = Column(Float, default=0.0)
    net_worth = Column(Float, default=0.0)
    investment_goals = Column(Text, nullable=True)  # JSON string array
    
    # Status and tracking
    is_active = Column(Boolean, default=True)
    status = Column(String(20), default="active", nullable=False)  # 'active', 'inactive', 'prospect', 'suspended'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100), default="system", nullable=False)
    last_contact_date = Column(DateTime(timezone=True), nullable=True)
    
    # Additional information
    notes = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # JSON string array
    referral_source = Column(String(255), nullable=True)