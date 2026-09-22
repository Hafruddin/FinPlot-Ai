import os
import csv
import io
import time
import logging
import asyncio
from typing import Dict, Any, Optional, List
import httpx
import certifi

from .symbol_mapper import symbol_mapper
from .market_cache import market_cache

logger = logging.getLogger("finpilot.kite")

class KiteService:
    """
    Zerodha Kite Connect integration service.
    Handles Kite REST APIs, Session / Access Token verification, Instruments, and Streaming.
    """
    BASE_URL = "https://api.kite.trade"
    LOGIN_URL = "https://kite.zerodha.com/connect/login"
    WS_URL = "wss://ws.kite.trade"

    def __init__(self):
        self.api_key = os.getenv("KITE_API_KEY", "").strip()
        self.api_secret = os.getenv("KITE_API_SECRET", "").strip()
        self.access_token = os.getenv("KITE_ACCESS_TOKEN", "").strip()
        self._is_connected = False
        self._last_error = None
        self._instruments_loaded = False
        self._subscribers: set = set()
        self._live_ticks: Dict[str, Dict[str, Any]] = {}
        self._ws_task = None
        self._running = True

    def reload_credentials(self):
        """Reload credentials if changed at runtime or from .env."""
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip())
        self.api_key = os.getenv("KITE_API_KEY", "").strip()
        self.api_secret = os.getenv("KITE_API_SECRET", "").strip()
        self.access_token = os.getenv("KITE_ACCESS_TOKEN", "").strip()

    def get_login_url(self) -> str:
        """Construct the official Kite Connect web login URL."""
        if not self.api_key:
            return ""
        return f"{self.LOGIN_URL}?v=3&api_key={self.api_key}"

    def get_auth_status(self) -> Dict[str, Any]:
        """Returns clear Kite Connect status without leaking secrets."""
        self.reload_credentials()
        if not self.api_key:
            return {
                "configured": False,
                "connected": False,
                "reason": "KITE_API_KEY_MISSING",
                "message": "Kite API key is not configured."
            }
        if not self.access_token:
            return {
                "configured": True,
                "connected": False,
                "reason": "KITE_ACCESS_TOKEN_REQUIRED",
                "message": "Zerodha Kite Connect requires a daily access token. Visit the login URL to authorize.",
                "login_url": self.get_login_url(),
                "api_key_suffix": f"...{self.api_key[-4:]}" if len(self.api_key) > 4 else "***"
            }
        return {
            "configured": True,
            "connected": self._is_connected,
            "reason": None if self._is_connected else (self._last_error or "SESSION_INITIALIZING"),
            "message": "Kite Connect authenticated and active." if self._is_connected else "Verifying Kite session token...",
            "api_key_suffix": f"...{self.api_key[-4:]}" if len(self.api_key) > 4 else "***"
        }

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "X-Kite-Version": "3",
            "User-Agent": "FinPilotAI/1.0"
        }
        if self.api_key and self.access_token:
            headers["Authorization"] = f"token {self.api_key}:{self.access_token}"
        return headers

    async def fetch_instruments(self) -> List[Dict[str, Any]]:
        """
        Download and cache the master instruments list from Kite.
        The /instruments endpoint does not require user access token.
        """
        cache_key = "kite_instruments_master"
        cached = market_cache.get(cache_key)
        if cached:
            return cached

        try:
            async with httpx.AsyncClient(verify=certifi.where(), timeout=15.0) as client:
                res = await client.get(f"{self.BASE_URL}/instruments", headers={"X-Kite-Version": "3"})
                if res.status_code == 200:
                    text = res.text
                    reader = csv.DictReader(io.StringIO(text))
                    instruments = []
                    for row in reader:
                        instruments.append({
                            "instrument_token": int(row["instrument_token"]) if row.get("instrument_token") else None,
                            "tradingsymbol": row.get("tradingsymbol"),
                            "name": row.get("name"),
                            "last_price": float(row.get("last_price", 0) or 0),
                            "exchange": row.get("exchange"),
                            "segment": row.get("segment")
                        })
                    symbol_mapper.update_from_instruments(instruments)
                    market_cache.set(cache_key, instruments, category="instruments")
                    self._instruments_loaded = True
                    logger.info(f"Loaded {len(instruments)} Kite instruments.")
                    return instruments
                else:
                    logger.warning(f"Kite instruments fetch returned HTTP {res.status_code}")
        except Exception as e:
            logger.warning(f"Failed to fetch Kite instruments: {e}")
        return []

    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch quote from Kite if access_token is configured."""
        self.reload_credentials()
        if not self.api_key or not self.access_token:
            return None

        kite_sym = symbol_mapper.get_kite_symbol(symbol)
        cache_key = f"kite_quote_{kite_sym}"
        cached = market_cache.get(cache_key)
        if cached:
            return cached

        try:
            async with httpx.AsyncClient(verify=certifi.where(), timeout=8.0) as client:
                res = await client.get(
                    f"{self.BASE_URL}/quote",
                    params={"i": kite_sym},
                    headers=self._get_headers()
                )
                if res.status_code == 200:
                    payload = res.json()
                    if payload.get("status") == "success" and "data" in payload:
                        data = payload["data"].get(kite_sym)
                        if data:
                            self._is_connected = True
                            self._last_error = None
                            ohlc = data.get("ohlc", {})
                            normalized = {
                                "symbol": symbol_mapper.normalize(symbol),
                                "tradingsymbol": data.get("tradingsymbol") or symbol,
                                "price": float(data.get("last_price", 0)),
                                "change": float(data.get("net_change", 0)),
                                "change_percent": float(data.get("net_change_percentage", 0) or 0),
                                "open": float(ohlc.get("open", 0)),
                                "high": float(ohlc.get("high", 0)),
                                "low": float(ohlc.get("low", 0)),
                                "close": float(ohlc.get("close", 0)),
                                "volume": int(data.get("volume", 0)),
                                "last_trade_time": str(data.get("last_trade_time", "")),
                                "source": "Zerodha Kite Connect",
                                "cached": False,
                                "timestamp": time.time()
                            }
                            market_cache.set(cache_key, normalized, category="quote")
                            return normalized
                elif res.status_code == 403:
                    self._is_connected = False
                    self._last_error = "KITE_TOKEN_EXPIRED"
                    logger.warning("Kite access token expired or invalid.")
                else:
                    logger.warning(f"Kite quote error HTTP {res.status_code}: {res.text[:120]}")
        except Exception as e:
            logger.warning(f"Kite quote network error: {e}")
        return None

    async def get_historical(self, symbol: str, interval: str = "day", from_date: str = "", to_date: str = "") -> Optional[List[Dict[str, Any]]]:
        """Fetch historical candles from Kite."""
        self.reload_credentials()
        if not self.api_key or not self.access_token:
            return None

        token = symbol_mapper.get_token(symbol)
        if not token:
            return None

        cache_key = f"kite_hist_{token}_{interval}_{from_date}_{to_date}"
        cached = market_cache.get(cache_key)
        if cached:
            return cached

        try:
            async with httpx.AsyncClient(verify=certifi.where(), timeout=10.0) as client:
                res = await client.get(
                    f"{self.BASE_URL}/instruments/historical/{token}/{interval}",
                    params={"from": from_date, "to": to_date},
                    headers=self._get_headers()
                )
                if res.status_code == 200:
                    payload = res.json()
                    candles_raw = payload.get("data", {}).get("candles", [])
                    candles = []
                    for c in candles_raw:
                        candles.append({
                            "time": c[0],
                            "open": float(c[1]),
                            "high": float(c[2]),
                            "low": float(c[3]),
                            "close": float(c[4]),
                            "volume": int(c[5])
                        })
                    market_cache.set(cache_key, candles, category="history")
                    return candles
        except Exception as e:
            logger.warning(f"Kite historical candles error: {e}")
        return None


kite_service = KiteService()
