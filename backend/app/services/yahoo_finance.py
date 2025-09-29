import httpx
import asyncio
from typing import Optional, Dict, Any

class YahooFinanceService:
    def __init__(self):
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart"
    
    async def search_asset(self, symbol: str) -> Optional[Dict[str, Any]]:
        try:
            url = f"{self.base_url}/{symbol}"
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                data = response.json()
                
            result = data.get("chart", {}).get("result", [{}])[0]
            meta = result.get("meta", {})
            
            if not meta:
                return None
            
            return {
                "ticker": symbol.upper(),
                "name": meta.get("longName", ""),
                "exchange": meta.get("exchangeName", ""),
                "currency": meta.get("currency", "USD")
            }
        except Exception:
            return None

yahoo_finance = YahooFinanceService()