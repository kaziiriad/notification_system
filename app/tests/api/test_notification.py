import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import patch, MagicMock
import uuid
from datetime import datetime, timezone, timedelta

from app.main import app
from app.api.schemas import Status, Channel, Priority

# Fixture for the TestClient
@pytest.fixture(scope="module")
def client():
    with patch("app.main.run_migrations"):
        with TestClient(app) as c:
            yield c

# Test for successful notification creation
def test_create_notification_success(client: TestClient):
    with patch('app.services.notification_service.NotificationService.create_notification') as mock_create:
        mock_create.return_value = MagicMock(
            id=str(uuid.uuid4()),
            status=Status.QUEUED,
            channel=Channel.EMAIL,
            priority=Priority.HIGH,
            subject="Test Subject",
            content="Test Content",
            created_at=datetime.now(timezone.utc)
        )
        
        response = client.post("/api/v1/notifications/", json={
            "user_ids": [1],
            "channel": "email",
            "priority": "high",
            "subject": "Test Subject",
            "content": "Test Content"
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["status"] == "queued"

# Test for validation errors
def test_create_notification_validation_error(client: TestClient):
    response = client.post("/api/v1/notifications/", json={
        "user_ids": [],
        "channel": "email",
        "priority": "high",
        "subject": "Test Subject",
        "content": ""
    })
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# Test for not found recipients
def test_create_notification_no_recipients_found(client: TestClient):
    with patch('app.services.notification_service.NotificationService.create_notification', 
               side_effect=ValueError("No valid recipients found")):
        
        response = client.post("/api/v1/notifications/", json={
            "user_ids": [999], # Assuming user 999 does not exist
            "channel": "email",
            "priority": "high",
            "subject": "Test Subject",
            "content": "Test Content"
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "No valid recipients found" in response.json()["detail"]

# Test for scheduled notifications
def test_create_scheduled_notification_success(client: TestClient):
    scheduled_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    
    with patch('app.services.notification_service.NotificationService.create_notification') as mock_create:
        mock_create.return_value = MagicMock(
            id=str(uuid.uuid4()),
            status=Status.SCHEDULED,
            channel=Channel.EMAIL,
            priority=Priority.HIGH,
            subject="Test Subject",
            content="Test Content",
            created_at=datetime.now(timezone.utc),
            scheduled_at=datetime.fromisoformat(scheduled_time)
        )
        
        response = client.post("/api/v1/notifications/", json={
            "user_ids": [1],
            "channel": "email",
            "priority": "high",
            "subject": "Test Subject",
            "content": "Test Content",
            "scheduled_at": scheduled_time
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["status"] == "scheduled"

# Test for health check endpoint
def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy", "version": "1.0.0"}

# Test for root endpoint
def test_read_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "Welcome" in response.json()["message"]
