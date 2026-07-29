"""Cache Service."""
import time
from typing import Any, Optional
from collections import OrderedDict

from backend.agents.security_agent.config.settings import CACHE_SIZE


class CacheService:
    """In-memory TTL caching."""

    def __init__(self) -> None:
        self.capacity = CACHE_SIZE
        # OrderedDict to maintain insertion order for LRU-like eviction if needed
        self._cache: OrderedDict[str, dict[str, Any]] = OrderedDict()

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        if key not in self._cache:
            return None
            
        entry = self._cache[key]
        if time.time() > entry["expires_at"]:
            # Expired, remove it
            del self._cache[key]
            return None
            
        # Move to end to mark as recently used (LRU)
        self._cache.move_to_end(key)
        return entry["value"]

    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set value in cache."""
        if len(self._cache) >= self.capacity:
            # Evict oldest
            self._cache.popitem(last=False)
            
        self._cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl
        }

    def invalidate(self, key: str) -> None:
        """Invalidate a specific key."""
        if key in self._cache:
            del self._cache[key]
            
    def clear(self) -> None:
        """Clear entire cache."""
        self._cache.clear()

    def health(self) -> dict[str, Any]:
        """Return health and metrics of cache."""
        # Optional: could do a lazy cleanup of expired keys here
        return {
            "status": "healthy",
            "keys_count": len(self._cache),
            "capacity": self.capacity,
            "utilization_pct": round((len(self._cache) / self.capacity) * 100, 2) if self.capacity > 0 else 0
        }
