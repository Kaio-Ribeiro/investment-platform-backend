from sqlalchemy import Column, Integer, ForeignKey, Numeric, Date, String, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base
import enum

class MovementType(enum.Enum):
    deposit = "deposit"
    withdrawal = "withdrawal"

class Movement(Base):
    __tablename__ = "movements"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    type = Column(Enum(MovementType), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    date = Column(Date, nullable=False)
    note = Column(String, nullable=True)

    # Relationships
    client = relationship("Client", backref="movements")