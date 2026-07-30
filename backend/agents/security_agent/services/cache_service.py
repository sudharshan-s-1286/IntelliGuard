"""Cache Service."""
import json
import sqlite3
import time
from typing import Any
import logging
from pathlib import Path

from agents.security_agent.config.settings import CACHE_SIZE

logger = logging.getLogger(__name__)

class CacheService:
    """Persistent SQLite-based caching."""

    def __init__(self, db_path: str = ".cache.db") -> None:
        self.capacity = CACHE_SIZE
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    expires_at REAL,
                    last_accessed REAL
                )
            ''')
            # Index for eviction
            conn.execute('CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache(last_accessed)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_expires_at ON cache(expires_at)')
            conn.commit()

    async def get(self, key: str) -> Any | None:
        """Retrieve value from cache."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value, expires_at FROM cache WHERE key = ?', (key,))
            row = cursor.fetchone()

            if not row:
                return None

            value_json, expires_at = row
            if time.time() > expires_at:
                cursor.execute('DELETE FROM cache WHERE key = ?', (key,))
                conn.commit()
                return None

            cursor.execute('UPDATE cache SET last_accessed = ? WHERE key = ?', (time.time(), key))
            conn.commit()
            
            try:
                return json.loads(value_json)
            except Exception as e:
                logger.error(f"Failed to decode cache entry for {key}: {e}")
                return None

    async def set(self, key: str, value: Any, ttl: int = 86400) -> None:
        """Set value in cache."""
        try:
            value_json = json.dumps(value)
        except Exception as e:
            logger.error(f"Failed to encode cache entry for {key}: {e}")
            return
            
        now = time.time()
        expires_at = now + ttl

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Enforce capacity by evicting oldest accessed
            cursor.execute('SELECT COUNT(*) FROM cache')
            count = cursor.fetchone()[0]
            if count >= self.capacity:
                limit = (count - self.capacity) + 1
                cursor.execute('''
                    DELETE FROM cache 
                    WHERE key IN (
                        SELECT key FROM cache 
                        ORDER BY last_accessed ASC 
                        LIMIT ?
                    )
                ''', (limit,))

            cursor.execute('''
                INSERT INTO cache (key, value, expires_at, last_accessed) 
                VALUES (?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET 
                    value=excluded.value, 
                    expires_at=excluded.expires_at, 
                    last_accessed=excluded.last_accessed
            ''', (key, value_json, expires_at, now))
            conn.commit()

    def invalidate(self, key: str) -> None:
        """Invalidate a specific key."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM cache WHERE key = ?', (key,))
            conn.commit()
            
    def clear(self) -> None:
        """Clear entire cache."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM cache')
            conn.commit()

    def health(self) -> dict[str, Any]:
        """Return health and metrics of cache."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM cache')
                count = cursor.fetchone()[0]
        except Exception:
            count = 0
            
        return {
            "status": "healthy",
            "keys_count": count,
            "capacity": self.capacity,
            "utilization_pct": round((count / self.capacity) * 100, 2) if self.capacity > 0 else 0,
            "type": "sqlite"
        }
