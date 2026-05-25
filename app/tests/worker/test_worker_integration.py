import pytest
import subprocess
import time
import requests
from app.worker.tasks import send_notification_task
from app.db.sql.models import Notification, NotificationRecipient
from app.api.schemas.common import Status, Priority, Channel
import uuid
from unittest.mock import patch, AsyncMock

@pytest.mark.skip(reason="Celery-based integration tests - superseded by direct MQ consumer pattern")
@pytest.mark.integration
def test_send_notification_task_integration(mock_db_session, celery_worker):
    """
    Test the end-to-end flow of a notification task through Celery.
    
    This test uses Celery's eager mode to run tasks synchronously
    without requiring a separate worker process.
    """
    # Mock the channel service to avoid real API calls
    with patch('app.services.channel_services.EmailChannelService.send_notification', new_callable=AsyncMock) as mock_send:
        mock_send.return_value = None  # Simulate successful send
        
        # 1. Create a notification in the test database
        notification = Notification(
            id=str(uuid.uuid4()),
            subject="Integration Test",
            priority=Priority.MEDIUM,
            channel=Channel.EMAIL,
            content="This is an integration test.",
            status=Status.PENDING
        )
        mock_db_session.add(notification)
        mock_db_session.commit()
        mock_db_session.refresh(notification)

        # Create a recipient for this notification
        recipient = NotificationRecipient(
            notification_id=notification.id,
            email="test@example.com",
            status=Status.PENDING
        )
        mock_db_session.add(recipient)
        mock_db_session.commit()

        # 2. Execute the task synchronously using eager mode
        notification_id = str(notification.id)
        result = send_notification_task.delay(notification_id)

        # 3. Assert the notification status in the database
        # Query the database using the session, avoiding detached objects
        updated_notification = mock_db_session.query(Notification).filter(
            Notification.id == notification_id
        ).first()
        
        assert updated_notification is not None, "Notification not found in database"
        assert updated_notification.status == Status.SENT
        
        # Verify the mock was called
        mock_send.assert_called_once()

@pytest.mark.skip(reason="Celery-based integration tests - superseded by direct MQ consumer pattern")
@pytest.mark.integration
def test_worker_task_failure_handling(mock_db_session, celery_worker):
    """Test that worker properly handles task failures."""
    # Mock the channel service to simulate a failure
    with patch('app.services.channel_services.EmailChannelService.send_notification', new_callable=AsyncMock) as mock_send:
        mock_send.side_effect = Exception("Simulated email service failure")
        
        # Create a notification
        notification = Notification(
            id=str(uuid.uuid4()),
            subject="Failure Test",
            priority=Priority.HIGH,
            channel=Channel.EMAIL,
            content="This should fail.",
            status=Status.PENDING
        )
        mock_db_session.add(notification)
        mock_db_session.commit()
        mock_db_session.refresh(notification)

        # Create a recipient for this notification
        recipient = NotificationRecipient(
            notification_id=notification.id,
            email="test@example.com",
            status=Status.PENDING
        )
        mock_db_session.add(recipient)
        mock_db_session.commit()

        # Execute the task and expect it to fail
        notification_id = str(notification.id)
        result = send_notification_task.delay(notification_id)

        # Check that the notification status reflects the failure
        updated_notification = mock_db_session.query(Notification).filter(
            Notification.id == notification_id
        ).first()

        if updated_notification is None:
            mock_db_session.rollback()
            updated_notification = mock_db_session.query(Notification).filter(
                Notification.id == notification_id
            ).first()
        
        assert updated_notification is not None, "Notification not found in database"
        assert updated_notification.status == Status.FAILED