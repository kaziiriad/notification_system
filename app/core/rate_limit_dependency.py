from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.rate_limiter import check_rate_limit
from app.core.auth import verify_service_token, ServiceTokenPayload
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def rate_limit_dependency(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> ServiceTokenPayload:
    """
    FastAPI dependency that:
    1. Validates JWT token
    2. Checks rate limit for the service_id
    3. Returns the service payload if allowed

    Use as: `service: ServiceTokenPayload = Depends(rate_limit_dependency)`
    """
    # Verify JWT first
    payload = verify_service_token(credentials.credentials)

    # Check rate limit
    allowed, remaining = check_rate_limit(payload.service_id)

    if not allowed:
        logger.warning("Rate limit exceeded", extra={
            "service_id": payload.service_id,
            "scope": payload.scope,
        })
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later.",
            headers={
                "X-RateLimit-Remaining": str(0),
                "Retry-After": "60",
            },
        )

    return payload