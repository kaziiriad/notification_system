import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.core.auth import create_service_token, verify_service_token, ServiceTokenPayload
from datetime import datetime, timezone


@pytest.fixture
def client():
    return TestClient(app)


class TestServiceToken:
    """Unit tests for service token creation and verification."""

    def test_create_and_verify_token(self):
        """Test that a created token can be verified."""
        token_response = create_service_token(
            service_id="test-service",
            scope=["notifications:read", "notifications:write"],
        )
        payload = verify_service_token(token_response.access_token)

        assert payload.service_id == "test-service"
        assert "notifications:read" in payload.scope
        assert "notifications:write" in payload.scope

    def test_verify_invalid_token_raises(self):
        """Test that an invalid token raises HTTPException 401."""
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            verify_service_token("invalid.token.here")
        assert exc_info.value.status_code == 401

    def test_token_payload_model(self):
        """Test ServiceTokenPayload model."""
        now = datetime.now(timezone.utc)
        payload = ServiceTokenPayload(
            service_id="svc-1",
            scope=["test:read"],
            exp=now,
            iat=now,
        )
        assert payload.service_id == "svc-1"
        assert payload.scope == ["test:read"]


class TestAuthEndpoints:
    """Integration tests for auth endpoints."""

    def test_get_token_with_valid_credentials(self, client):
        """Test token endpoint with valid credentials."""
        response = client.post(
            "/api/v1/auth/token",
            json={
                "service_id": "test-service",
                "service_secret": "service-secret-change-in-production",
                "scope": ["notifications:read"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 3600

    def test_get_token_with_invalid_credentials(self, client):
        """Test token endpoint with invalid credentials returns 401."""
        response = client.post(
            "/api/v1/auth/token",
            json={
                "service_id": "test-service",
                "service_secret": "wrong-secret",
            },
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid service credentials"

    def test_protected_endpoint_without_token(self, client):
        """Test that protected endpoints require authentication."""
        response = client.post(
            "/api/v1/notifications/",
            json={
                "subject": "Test",
                "content": "Hello",
                "channel": "email",
                "user_ids": [1],
                "emails": ["test@example.com"],
                "priority": "high",
            },
        )
        assert response.status_code == 401  # HTTPBearer returns 401 when no auth header

    def test_protected_endpoint_with_valid_token(self, client):
        """Test that protected endpoints work with valid token."""
        # First get a token
        token_response = client.post(
            "/api/v1/auth/token",
            json={
                "service_id": "test-service",
                "service_secret": "service-secret-change-in-production",
            },
        )
        token = token_response.json()["access_token"]

        # Now call protected endpoint
        response = client.post(
            "/api/v1/notifications/",
            json={
                "subject": "Test",
                "content": "Hello",
                "channel": "email",
                "user_ids": [1],
                "emails": ["test@example.com"],
                "priority": "high",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        # Either 201 (success) or 400/500 (business error) — not 401/403
        assert response.status_code != 401
        assert response.status_code != 403

    def test_protected_endpoint_with_invalid_token(self, client):
        """Test that invalid token returns 401."""
        response = client.post(
            "/api/v1/notifications/",
            json={
                "subject": "Test",
                "content": "Hello",
                "channel": "email",
                "user_ids": [1],
                "emails": ["test@example.com"],
                "priority": "high",
            },
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401