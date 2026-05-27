import time
from typing import Tuple
from app.core.redis_client import get_redis_client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter using Redis.
    Each service gets a bucket with:
    - capacity = RATE_LIMIT_REQUESTS_PER_MINUTE + RATE_LIMIT_BURST
    - refill rate = RATE_LIMIT_REQUESTS_PER_MINUTE per 60 seconds
    """

    def __init__(
        self,
        requests_per_minute: int = None,
        burst: int = None,
    ):
        self.capacity = (requests_per_minute or settings.RATE_LIMIT_REQUESTS_PER_MINUTE) + \
                        (burst or settings.RATE_LIMIT_BURST)
        self.refill_rate = requests_per_minute or settings.RATE_LIMIT_REQUESTS_PER_MINUTE  # tokens per second
        self.redis = get_redis_client()

    def _key(self, service_id: str) -> str:
        return f"rate_limit:{service_id}"

    def allow_request(self, service_id: str) -> Tuple[bool, int]:
        """
        Check if request is allowed using token bucket algorithm.
        Returns (allowed, remaining_tokens).
        """
        if not settings.RATE_LIMIT_ENABLED:
            return True, self.capacity

        key = self._key(service_id)
        now = time.time()

        # Lua script for atomic token bucket
        lua_script = """
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])

        local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(bucket[1])
        local last_refill = tonumber(bucket[2])

        if tokens == nil then
            tokens = capacity
            last_refill = now
        end

        -- Refill tokens based on elapsed time
        local elapsed = now - last_refill
        local tokens_to_add = elapsed * refill_rate
        tokens = math.min(capacity, tokens + tokens_to_add)
        last_refill = now

        local allowed = 0
        if tokens >= 1 then
            tokens = tokens - 1
            allowed = 1
        end

        redis.call('HMSET', key, 'tokens', tokens, 'last_refill', last_refill)
        redis.call('EXPIRE', key, 120)  -- Expire after 2 min of inactivity

        return {allowed, math.floor(tokens)}
        """

        try:
            result = self.redis.eval(
                lua_script,
                1,
                key,
                self.capacity,
                self.refill_rate / 60.0,  # convert per-minute to per-second
                now,
            )
            allowed = bool(result[0])
            remaining = int(result[1])
            return allowed, remaining
        except redis.RedisError as e:
            logger.error("Rate limiter Redis error, allowing request", extra={"error": str(e)})
            return True, self.capacity  # Fail open


# Global limiter instance
rate_limiter = RateLimiter()


def check_rate_limit(service_id: str) -> Tuple[bool, int]:
    """
    Check if service_id is within rate limit.
    Returns (allowed, remaining_requests).
    """
    return rate_limiter.allow_request(service_id)