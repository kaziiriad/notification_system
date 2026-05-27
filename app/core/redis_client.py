import redis
from typing import Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """Get or create Redis client singleton."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True,
        )
    return _redis_client


def close_redis_client():
    """Close Redis connection on shutdown."""
    global _redis_client
    if _redis_client:
        _redis_client.close()
        _redis_client = None