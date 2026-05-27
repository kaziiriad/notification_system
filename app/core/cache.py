import json
from typing import Optional, Any
from app.core.redis_client import get_redis_client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class Cache:
    """
    Redis-based cache for notification data.
    """

    def __init__(self, ttl_seconds: int = None):
        self.ttl = ttl_seconds or settings.CACHE_TTL_SECONDS
        self.redis = get_redis_client()

    def _key(self, prefix: str, identifier: str) -> str:
        return f"cache:{prefix}:{identifier}"

    def get(self, prefix: str, identifier: str) -> Optional[Any]:
        """Get value from cache."""
        if not settings.CACHE_ENABLED:
            return None

        key = self._key(prefix, identifier)
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except redis.RedisError as e:
            logger.warning("Cache get error", extra={"key": key, "error": str(e)})
            return None
        except json.JSONDecodeError as e:
            logger.warning("Cache decode error", extra={"key": key, "error": str(e)})
            return None

    def set(self, prefix: str, identifier: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with TTL."""
        if not settings.CACHE_ENABLED:
            return False

        key = self._key(prefix, identifier)
        ttl = ttl or self.ttl
        try:
            self.redis.setex(key, ttl, json.dumps(value, default=str))
            return True
        except redis.RedisError as e:
            logger.warning("Cache set error", extra={"key": key, "error": str(e)})
            return False

    def delete(self, prefix: str, identifier: str) -> bool:
        """Delete value from cache."""
        key = self._key(prefix, identifier)
        try:
            self.redis.delete(key)
            return True
        except redis.RedisError as e:
            logger.warning("Cache delete error", extra={"key": key, "error": str(e)})
            return False

    def invalidate_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not settings.CACHE_ENABLED:
            return 0

        full_pattern = f"cache:{pattern}"
        try:
            keys = self.redis.keys(full_pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except redis.RedisError as e:
            logger.warning("Cache invalidate error", extra={"pattern": pattern, "error": str(e)})
            return 0


# Global cache instance
cache = Cache()


# Import redis for error handling
import redis