import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4

from app.worker.tasks import send_notification_task
from app.db.sql.models import Notification, NotificationRecipient as Recipient
from app.api.schemas import Status, Channel, Priority
from app.services.channel_services import ChannelServiceFactory

# Mock database session for the task
@pytest.fixture
def mock_db_session():
    return MagicMock()

# Test successful task execution
@patch('app.worker.tasks.NotificationService')
@patch('app.worker.tasks.SessionLocal')
def test_send_notification_task_success(mock_session_local, mock_notification_service):
    # Arrange
    db_session = MagicMock()
    mock_session_local.return_value = db_session
    notification_id = str(uuid4())
    mock_notification_service.return_value.process_notification = AsyncMock()
    
    # Act
    send_notification_task(notification_id)

    # Assert
    mock_notification_service.assert_called_once_with(db_session)
    mock_notification_service.return_value.process_notification.assert_called_once_with(notification_id)

# Test task when notification is not found
@patch('app.worker.tasks.NotificationService')
@patch('app.worker.tasks.SessionLocal')
def test_send_notification_task_not_found(mock_session_local, mock_notification_service):
    # Arrange
    db_session = MagicMock()
    mock_session_local.return_value = db_session
    notification_id = str(uuid4())
    mock_notification_service.return_value.process_notification = AsyncMock(side_effect=FileNotFoundError)

    # Act
    with pytest.raises(FileNotFoundError):
        send_notification_task(notification_id)

    # Assert
    mock_notification_service.assert_called_once_with(db_session)
    mock_notification_service.return_value.process_notification.assert_called_once_with(notification_id)

# Test task failure due to channel service error
@patch('app.worker.tasks.send_notification_task.retry')
@patch('app.worker.tasks.NotificationService')
@patch('app.worker.tasks.SessionLocal')
def test_send_notification_task_failure_and_retry(mock_session_local, mock_notification_service, mock_retry):
    # Arrange
    db_session = MagicMock()
    mock_session_local.return_value = db_session
    notification_id = str(uuid4())
    mock_notification_service.return_value.process_notification = AsyncMock(side_effect=Exception("Service down"))
    mock_retry.side_effect = Exception("Retry called")

    # Act & Assert
    with pytest.raises(Exception, match="Retry called"):
        send_notification_task(notification_id)

    mock_notification_service.assert_called_once_with(db_session)
    mock_notification_service.return_value.process_notification.assert_called_once_with(notification_id)
    assert mock_retry.called

# Test task with no recipients
@patch('app.worker.tasks.NotificationService')
@patch('app.worker.tasks.SessionLocal')
def test_send_notification_task_no_recipients(mock_session_local, mock_notification_service):
    # Arrange
    db_session = MagicMock()
    mock_session_local.return_value = db_session
    notification_id = str(uuid4())
    mock_notification_service.return_value.process_notification = AsyncMock(side_effect=ValueError("No recipients"))

    # Act
    with pytest.raises(ValueError, match="No recipients"):
        send_notification_task(notification_id)

    # Assert
    mock_notification_service.assert_called_once_with(db_session)
    mock_notification_service.return_value.process_notification.assert_called_once_with(notification_id)