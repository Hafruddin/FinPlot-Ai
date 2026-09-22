import time
from typing import Any, Optional, Dict
import threading

class MarketCache:
    """Thread-safe in-memory cache with configurable TTLs."""
    
    DEFAULT_TTLS = {
        "quote": 5,          # 5 seconds for live quotes
        "technicals": 60,     # 60 seconds for indicators
        "history": 300,       # 5 minutes for historical candles
        "news": 600,          # 10 minutes for news/sentiment
        "overview": 3600,     # 1 hour for company fundamentals
        "instruments": 86400  # 24 hours for instrument master list
    }

    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            if time.time() > entry["expires_at"]:
                del self._store[key]
                return None
            return entry["data"]

    def set(self, key: str, data: Any, ttl_seconds: Optional[int] = None, category: str = "quote") -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self.DEFAULT_TTLS.get(category, 10)
        with self._lock:
            self._store[key] = {
                "data": data,
                "expires_at": time.time() + ttl,
                "created_at": time.time(),
                "ttl": ttl
            }

    def delete(self, key: str) -> None:
        with self._lock:
            if key in self._store:
                del self._store[key]

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def stats(self) -> Dict[str, int]:
        with self._lock:
            now = time.time()
            active = sum(1 for e in self._store.values() if e["expires_at"] > now)
            return {"total_entries": len(self._store), "active_entries": active}


market_cache = MarketCache()
