import yfinance as yf
import asyncio
import time
from typing import Optional, Dict, Any
from starlette.concurrency import run_in_threadpool
import random

class YahooFinanceService:
    def __init__(self):
        # Cache para evitar muitas requisições
        self._cache = {}
        self._last_request_time = 0
        
    async def search_asset(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Busca informações de um ativo usando yfinance com rate limiting e fallback
        """
        symbol = symbol.upper()
        
        # Verificar cache primeiro
        if symbol in self._cache:
            cache_time, data = self._cache[symbol]
            # Cache válido por 5 minutos
            if time.time() - cache_time < 300:
                return data
        
        try:
            # Rate limiting - esperar mais tempo entre requisições
            current_time = time.time()
            time_since_last = current_time - self._last_request_time
            if time_since_last < 10:  # Aumentado para 10 segundos
                wait_time = 10 - time_since_last + random.uniform(2, 5)
                await asyncio.sleep(wait_time)
            
            # Executa em thread pool para não bloquear o loop principal
            ticker_data = await run_in_threadpool(self._get_ticker_info, symbol)
            self._last_request_time = time.time()
            
            if not ticker_data:
                # Fallback para dados mock quando Yahoo Finance não está disponível
                return self._get_fallback_data(symbol)
            
            result = {
                "ticker": symbol,
                "name": ticker_data.get("longName", ticker_data.get("shortName", symbol)),
                "exchange": ticker_data.get("exchange", ""),
                "currency": ticker_data.get("currency", "USD")
            }
            
            # Salvar no cache
            self._cache[symbol] = (time.time(), result)
            
            return result
            
        except Exception as e:
            print(f"Error fetching Yahoo Finance data for {symbol}: {e}")
            # Fallback para dados mock em caso de erro
            return self._get_fallback_data(symbol)
    
    def _get_ticker_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Função síncrona para buscar dados do ticker com retry e configurações otimizadas
        """
        max_retries = 2  # Reduzido para evitar muitas tentativas
        for attempt in range(max_retries):
            try:
                # Delay exponencial entre tentativas
                if attempt > 0:
                    time.sleep((2 ** attempt) + random.uniform(1, 3))
                
                # Configurar yfinance com headers customizados
                ticker = yf.Ticker(symbol)
                
                # Configurar session com user-agent customizado
                ticker.session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                info = ticker.info
                
                # Verificar se os dados são válidos
                if not info or len(info) < 5:
                    if attempt < max_retries - 1:
                        continue
                    return None
                    
                return info
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for {symbol}: {e}")
                if attempt == max_retries - 1:
                    return None
                
        return None
    
    def _get_fallback_data(self, symbol: str) -> Dict[str, Any]:
        """
        Retorna dados mock quando Yahoo Finance não está disponível
        """
        # Dados mock para alguns symbols conhecidos
        fallback_data = {
            "AAPL": {"name": "Apple Inc.", "exchange": "NASDAQ", "currency": "USD"},
            "GOOGL": {"name": "Alphabet Inc.", "exchange": "NASDAQ", "currency": "USD"},
            "MSFT": {"name": "Microsoft Corporation", "exchange": "NASDAQ", "currency": "USD"},
            "TSLA": {"name": "Tesla, Inc.", "exchange": "NASDAQ", "currency": "USD"},
            "AMZN": {"name": "Amazon.com, Inc.", "exchange": "NASDAQ", "currency": "USD"},
            "META": {"name": "Meta Platforms, Inc.", "exchange": "NASDAQ", "currency": "USD"},
            "NFLX": {"name": "Netflix, Inc.", "exchange": "NASDAQ", "currency": "USD"},
            "NVDA": {"name": "NVIDIA Corporation", "exchange": "NASDAQ", "currency": "USD"},
        }
        
        if symbol in fallback_data:
            data = fallback_data[symbol]
            return {
                "ticker": symbol,
                "name": data["name"],
                "exchange": data["exchange"],
                "currency": data["currency"]
            }
        else:
            # Fallback genérico para symbols desconhecidos
            return {
                "ticker": symbol,
                "name": f"{symbol} Corp.",
                "exchange": "NYSE",
                "currency": "USD"
            }
    
    async def get_stock_history(self, symbol: str, period: str = "1mo") -> Optional[Dict[str, Any]]:
        """
        Obtém histórico de preços do ativo
        """
        try:
            history_data = await run_in_threadpool(self._get_history_data, symbol, period)
            return history_data
        except Exception as e:
            print(f"Error fetching history for {symbol}: {e}")
            return None
    
    def _get_history_data(self, symbol: str, period: str) -> Optional[Dict[str, Any]]:
        """
        Função síncrona para buscar histórico de preços
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
            
            # Converter para formato serializável
            return hist.tail(5).to_dict(orient="index")  # Últimos 5 registros
        except Exception as e:
            print(f"Error in _get_history_data for {symbol}: {e}")
            return None

yahoo_finance = YahooFinanceService()