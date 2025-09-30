from sqlalchemy import Column, Integer, ForeignKey, Numeric, Date
from sqlalchemy.orm import relationship
from app.models.base import Base

class Allocation(Base):
    __tablename__ = "allocations"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    quantity = Column(Numeric(15, 6), nullable=False)
    buy_price = Column(Numeric(15, 2), nullable=False)
    buy_date = Column(Date, nullable=False)

    # Relationships
    client = relationship("Client", backref="allocations")
    asset = relationship("Asset", backref="allocations")