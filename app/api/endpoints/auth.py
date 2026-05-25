from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.core.auth import create_service_token, ServiceTokenResponse
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Auth"])


class TokenRequest(BaseModel):
    """Request body for service token generation."""
    service_id: str
    service_secret: str
    scope: list[str] = ["notifications:read", "notifications:write"]


class TokenError(BaseModel):
    detail: str


@router.post("/token", response_model=ServiceTokenResponse, responses={401: {"model": TokenError}})
async def get_service_token(request: TokenRequest):
    """
    Generate a JWT token for service-to-service authentication.

    Services call this endpoint with their service_id and service_secret to obtain
    a short-lived JWT token. Tokens expire after JWT_EXPIRY_MINUTES (default 60).

    In production, service_secret should be stored securely (e.g., AWS Secrets Manager).
    For now, it must match the SERVICE_API_SECRET env var.
    """
    if request.service_secret != settings.SERVICE_API_SECRET:
        logger.warning("Invalid service credentials", extra={"service_id": request.service_id})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid service credentials",
        )

    token_response = create_service_token(
        service_id=request.service_id,
        scope=request.scope,
    )
    logger.info("Service token issued", extra={"service_id": request.service_id})
    return token_response