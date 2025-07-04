import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.notification_service import NotificationService
from app.api.schemas import NotificationCreate, Priority, Channel, Status
from app.db.sql.models import Notification
import uuid
from datetime import datetime, timezone, timedelta

@pytest.fixture
def mock_db_session():
    """Pytest fixture for a mock SQLAlchemy session."""
    return MagicMock()

@pytest.fixture
def notification_service(mock_db_session):
    """Pytest fixture for a NotificationService instance."""
    with patch('app.services.notification_service.NotificationRepository') as MockRepository, \
         patch('app.services.notification_service.RecipientResolver') as MockResolver, \
         patch('app.services.notification_service.NotificationValidator') as MockValidator:
        service = NotificationService(mock_db_session)
        service.notification_repository = MockRepository()
        service.recipient_resolver = MockResolver()
        service.validator = MockValidator()
        yield service



@pytest.mark.asyncio
async def test_create_notification_success(notification_service, mock_db_session):
    """
    Test successful creation of a notification.
    """
    # Arrange
    request = NotificationCreate(
        user_ids=[1],
        emails=[],
        sms_numbers=[],
        priority=Priority.HIGH,
        channel=Channel.EMAIL,
        subject="Test Subject",
        content="Test Content"
    )

    mock_notification = Notification(
        id=str(uuid.uuid4()),
        subject="Test Subject",
        content="Test Content",
        channel=Channel.EMAIL,
        priority=Priority.HIGH,
        status=Status.QUEUED,
        created_at=datetime.now(timezone.utc),
        scheduled_at=None
    )

    # Mock repository and other dependencies
    notification_service.validator.validate_request.return_value = []
    notification_service.notification_repository.create_notification.return_value = mock_notification
    notification_service.recipient_resolver.resolve_recipients.return_value = [{'user_id': 1, 'email': 'test@example.com'}]
    notification_service.notification_repository.create_recipients.return_value = []
    
    with patch('app.worker.tasks.send_notification_task.delay', new_callable=MagicMock) as mock_delay:
        # Act
        response = await notification_service.create_notification(request)

        # Assert
        assert response.id == mock_notification.id
        assert response.status == mock_notification.status.value
        
        # Verify that the correct methods were called
        notification_service.validator.validate_request.assert_called_once_with(request)
        notification_service.notification_repository.create_notification.assert_called_once()
        notification_service.recipient_resolver.resolve_recipients.assert_called_once()
        notification_service.notification_repository.create_recipients.assert_called_once()
        mock_delay.assert_called_once_with(mock_notification.id)
        mock_db_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_create_notification_validation_error(notification_service):
    """
    Test that a ValueError is raised when validation fails.
    """
    # Arrange
    request = NotificationCreate(
        user_ids=[1],  # Valid request
        emails=[],
        sms_numbers=[],
        priority=Priority.HIGH,
        channel=Channel.EMAIL,
        subject="Test Subject",
        content="Test Content"
    )
    notification_service.validator.validate_request.return_value = ["User IDs, emails, or SMS numbers must be provided."]

    # Act & Assert
    with pytest.raises(ValueError, match="Validation errors"):
        await notification_service.create_notification(request)

@pytest.mark.asyncio
async def test_create_notification_no_recipients(notification_service):
    """
    Test that a ValueError is raised when no recipients are found.
    """
    # Arrange
    request = NotificationCreate(
        user_ids=[1],
        emails=[],
        sms_numbers=[],
        priority=Priority.HIGH,
        channel=Channel.EMAIL,
        subject="Test Subject",
        content="Test Content"
    )
    
    mock_notification = Notification(id=str(uuid.uuid4()))
    notification_service.notification_repository.create_notification.return_value = mock_notification
    notification_service.validator.validate_request.return_value = []
    notification_service.recipient_resolver.resolve_recipients.return_value = []

    # Act & Assert
    with pytest.raises(ValueError, match="No valid recipients found"):
        await notification_service.create_notification(request)

@pytest.mark.asyncio
async def test_create_scheduled_notification(notification_service, mock_db_session):
    """
    Test successful creation of a scheduled notification.
    """
    # Arrange
    scheduled_time = datetime.now(timezone.utc) + timedelta(hours=1)
    request = NotificationCreate(
        user_ids=[1],
        emails=[],
        sms_numbers=[],
        priority=Priority.HIGH,
        channel=Channel.EMAIL,
        subject="Test Subject",
        content="Test Content",
        scheduled_at=scheduled_time
    )

    mock_notification = Notification(
        id=str(uuid.uuid4()),
        subject="Test Subject",
        content="Test Content",
        channel=Channel.EMAIL,
        priority=Priority.HIGH,
        status=Status.SCHEDULED,
        created_at=datetime.now(timezone.utc),
        scheduled_at=scheduled_time
    )

    notification_service.validator.validate_request.return_value = []
    notification_service.notification_repository.create_notification.return_value = mock_notification
    notification_service.recipient_resolver.resolve_recipients.return_value = [{'user_id': 1, 'email': 'test@example.com'}]
    
    with patch('app.worker.tasks.send_notification_task.apply_async', new_callable=MagicMock) as mock_apply_async:
        # Act
        response = await notification_service.create_notification(request)

        # Assert
        assert response.status == Status.SCHEDULED.value
        mock_apply_async.assert_called_once_with((mock_notification.id,), eta=scheduled_time)
        mock_db_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_create_notification_channel_all(notification_service):
    """
    Test that recipients are resolved for all channels when channel is 'all'.
    """
    # Arrange
    request = NotificationCreate(
        user_ids=[1],
        emails=["test@example.com"],
        sms_numbers=["+1234567890"],
        priority=Priority.HIGH,
        channel=Channel.ALL,
        subject="Test Subject",
        content="Test Content"
    )
    notification_service.validator.validate_request.return_value = []
    notification_service.recipient_resolver.resolve_recipients.side_effect = [
        [{'user_id': 1, 'email': 'test@example.com'}],  # For EMAIL
        [{'user_id': 1, 'phone_number': '+1234567890'}],  # For SMS
        [{'user_id': 1, 'push_token': 'some_token'}]  # For PUSH
    ]
    
    mock_notification = Notification(
        id=str(uuid.uuid4()),
        status=Status.QUEUED,
        created_at=datetime.now(timezone.utc),
        scheduled_at=None
    )
    notification_service.notification_repository.create_notification.return_value = mock_notification

    with patch('app.worker.tasks.send_notification_task.delay', new_callable=MagicMock):
        # Act
        await notification_service.create_notification(request)

        # Assert
        assert notification_service.recipient_resolver.resolve_recipients.call_count == 3

@pytest.mark.asyncio
async def test_create_notification_fails(notification_service, mock_db_session):
    """
    Test that the correct exception is raised if notification creation fails.
    """
    # Arrange
    request = NotificationCreate(
        user_ids=[1],
        emails=[],
        sms_numbers=[],
        priority=Priority.HIGH,
        channel=Channel.EMAIL,
        subject="Test Subject",
        content="Test Content"
    )
    notification_service.validator.validate_request.return_value = []
    notification_service.notification_repository.create_notification.side_effect = Exception("DB error")

    # Act & Assert
    with pytest.raises(Exception, match="DB error"):
        await notification_service.create_notification(request)
    
    mock_db_session.rollback.assert_called_once()
