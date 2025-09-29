from pydantic import BaseModel
from typing import Optional

class AssetBase(BaseModel):
    ticker: str
    name: str
    exchange: Optional[str] = None
    currency: str = "USD"

class AssetCreate(AssetBase):
    pass

class Asset(AssetBase):
    id: int

    class Config:
        from_attributes = True

class YahooFinanceAsset(BaseModel):
    ticker: str
    name: str
    exchange: Optional[str] = None
    currency: str = "USD"