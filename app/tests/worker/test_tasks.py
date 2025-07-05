import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4

from app.worker.tasks import send_notification_task

# Mock database session for the task
@pytest.fixture
def mock_db_session():
    return MagicMock()

# Test successful task execution
@patch('app.worker.tasks.SessionLocal')
@patch('app.services.notification_service.NotificationService')
def test_send_notification_task_success(mock_notification_service, mock_session_local):
    # Arrange
    db_session = MagicMock()
    mock_session_local.return_value = db_session
    notification_id = str(uuid4())
    
    # Make the instance's method an AsyncMock
    mock_notification_service.return_value.process_notification = AsyncMock()
    
    # Act
    send_notification_task(notification_id)

    # Assert
    mock_session_local.assert_called_once()
    mock_notification_service.assert_called_once_with(db_session)
    mock_notification_service.return_value.process_notification.assert_awaited_once_with(notification_id)

# Test task when notification is not found
@patch('app.worker.tasks.SessionLocal')
@patch('app.services.notification_service.NotificationService')
def test_send_notification_task_not_found(mock_notification_service, mock_session_local):
    # Arrange
    db_session = MagicMock()
    mock_session_local.return_value = db_session
    notification_id = str(uuid4())
    mock_notification_service.return_value.process_notification = AsyncMock(side_effect=FileNotFoundError("Notification not found"))

    # Act & Assert
    with pytest.raises(FileNotFoundError):
        send_notification_task(notification_id)

    mock_session_local.assert_called_once()
    mock_notification_service.assert_called_once_with(db_session)
    mock_notification_service.return_value.process_notification.assert_awaited_once_with(notification_id)

# Test task failure due to channel service error
@patch('app.worker.tasks.send_notification_task.retry')
@patch('app.worker.tasks.SessionLocal')
@patch('app.services.notification_service.NotificationService')
def test_send_notification_task_failure_and_retry(mock_notification_service, mock_session_local, mock_retry):
    # Arrange
    db_session = MagicMock()
    mock_session_local.return_value = db_session
    notification_id = str(uuid4())
    
    # Configure the mock to raise an exception when process_notification is awaited
    mock_notification_service.return_value.process_notification = AsyncMock(side_effect=Exception("Service down"))
    mock_retry.side_effect = Exception("Retry called")

    # Act & Assert
    with pytest.raises(Exception, match="Retry called"):
        send_notification_task(notification_id)

    mock_session_local.assert_called_once()
    mock_notification_service.assert_called_once_with(db_session)
    mock_notification_service.return_value.process_notification.assert_awaited_once_with(notification_id)
    mock_retry.assert_called_once()

# Test task with no recipients
@patch('app.worker.tasks.SessionLocal')
@patch('app.services.notification_service.NotificationService')
def test_send_notification_task_no_recipients(mock_notification_service, mock_session_local):
    # Arrange
    db_session = MagicMock()
    mock_session_local.return_value = db_session
    notification_id = str(uuid4())
    mock_notification_service.return_value.process_notification = AsyncMock(side_effect=ValueError("No recipients"))

    # Act & Assert
    with pytest.raises(ValueError, match="No recipients"):
        send_notification_task(notification_id)

    mock_session_local.assert_called_once()
    mock_notification_service.assert_called_once_with(db_session)
    mock_notification_service.return_value.process_notification.assert_awaited_once_with(notification_id)
