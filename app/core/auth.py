import jwt
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()


class ServiceTokenPayload(BaseModel):
    """JWT payload for service-to-service auth."""
    service_id: str
    scope: list[str]
    exp: datetime
    iat: datetime


class ServiceTokenResponse(BaseModel):
    """Response model for token generation."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


def create_service_token(service_id: str, scope: list[str]) -> ServiceTokenResponse:
    """
    Create a JWT token for a service.
    Tokens expire after JWT_EXPIRY_MINUTES (default 60).
    """
    now = datetime.now(timezone.utc)
    payload = {
        "service_id": service_id,
        "scope": scope,
        "exp": now + timedelta(minutes=settings.JWT_EXPIRY_MINUTES),
        "iat": now,
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return ServiceTokenResponse(
        access_token=token,
        expires_in=settings.JWT_EXPIRY_MINUTES * 60,
    )


def verify_service_token(token: str) -> ServiceTokenPayload:
    """
    Verify a service JWT token.
    Returns the decoded payload if valid.
    Raises HTTPException 401 if invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return ServiceTokenPayload(**payload)
    except jwt.ExpiredSignatureError:
        logger.warning("Service token expired", extra={"error": "token_expired"})
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError as e:
        logger.warning("Invalid service token", extra={"error": str(e)})
        raise HTTPException(401, "Invalid token")


def get_current_service(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> ServiceTokenPayload:
    """
    FastAPI dependency to validate JWT and return current service identity.
    Use as: `def endpoint(..., service: ServiceTokenPayload = Depends(get_current_service))`
    """
    return verify_service_token(credentials.credentials)


def require_scope(required_scope: str):
    """
    FastAPI dependency factory that checks if the service has required scope.
    Usage: `def endpoint(..., service: ServiceTokenPayload = Depends(require_scope("notifications:write")))`
    """
    def scope_checker(
        credentials: HTTPAuthorizationCredentials = Security(security),
    ) -> ServiceTokenPayload:
        payload = verify_service_token(credentials.credentials)
        if required_scope not in payload.scope:
            logger.warning("Insufficient scope", extra={
                "service_id": payload.service_id,
                "required_scope": required_scope,
                "actual_scope": payload.scope,
            })
            raise HTTPException(403, f"Missing required scope: {required_scope}")
        return payload

    return scope_checker