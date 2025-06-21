import pytest
from unittest.mock import MagicMock, patch, call
from datetime import datetime, timezone
from app.services.notification import NotificationService
from app.api.schemas import NotificationCreate, Channel, Priority, Status
from app.db.sql.models import Notification, NotificationRecipient
from sqlalchemy.orm import Session

# Fixtures
@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)

@pytest.fixture
def mock_queue_service():
    return MagicMock()

@pytest.fixture
def mock_template_service():
    return MagicMock()

@pytest.fixture
def mock_delivery_service():
    return MagicMock()

@pytest.fixture
def notification_service(
    mock_db_session,
    mock_queue_service,
    mock_template_service,
    mock_delivery_service
):
    return NotificationService(
        db=mock_db_session,
        queue_service=mock_queue_service,
        template_service=mock_template_service,
        delivery_service=mock_delivery_service
    )

@pytest.fixture
def sample_notification_data():
    return NotificationCreate(
        user_ids=[101, 102],
        emails=["user1@example.com", "user2@example.com"],
        sms_numbers=["+15551234567"],
        priority=Priority.HIGH,
        channel=Channel.EMAIL,
        content="Welcome to our service!",
        template="welcome_email"
    )

# Tests
def test_create_notification_success(
    notification_service, 
    sample_notification_data,
    mock_db_session,
    mock_queue_service,
    mock_template_service
):
    # Setup
    mock_template_service.render_template.return_value = "Rendered content"
    mock_db_session.add.side_effect = lambda x: setattr(x, 'id', 1)  # Simulate ID assignment
    
    # Execute
    notification = notification_service.create_notification(sample_notification_data)
    
    # Assert
    assert notification.id == 1
    assert notification.content == "Rendered content"
    assert notification.status == Status.PENDING
    assert len(notification.recipients) == 3  # 2 users + 1 email + 1 sms
    
    # Verify template rendering
    mock_template_service.render_template.assert_called_once_with(
        template_name="welcome_email",
        channel=Channel.EMAIL,
        variables={'content': "Welcome to our service!"}
    )
    
    # Verify DB operations
    assert mock_db_session.add.call_count == 2  # Notification + recipients
    mock_db_session.flush.assert_called_once()
    mock_db_session.commit.assert_called_once()
    
    # Verify queuing
    mock_queue_service.enqueue_notification.assert_called_once_with(1)

def test_create_notification_without_template(
    notification_service,
    mock_template_service
):
    # Setup
    data = NotificationCreate(
        user_ids=[101],
        emails=[],
        sms_numbers=[],
        priority=Priority.MEDIUM,
        channel=Channel.PUSH,
        content="Direct content"
    )
    
    # Execute
    notification = notification_service.create_notification(data)
    
    # Assert
    assert notification.content == "Direct content"
    mock_template_service.render_template.assert_not_called()

def test_get_notification_found(notification_service, mock_db_session):
    # Setup
    mock_notification = MagicMock(spec=Notification)
    mock_db_session.query().filter().first.return_value = mock_notification
    
    # Execute
    result = notification_service.get_notification(1)
    
    # Assert
    assert result == mock_notification
    mock_db_session.query.assert_called_with(Notification)
    mock_db_session.query().filter.assert_called_with(Notification.id == 1)

def test_get_notification_not_found(notification_service, mock_db_session):
    # Setup
    mock_db_session.query().filter().first.return_value = None
    
    # Execute
    result = notification_service.get_notification(999)
    
    # Assert
    assert result is None

def test_update_notification_status_success(
    notification_service,
    mock_db_session
):
    # Setup
    mock_notification = MagicMock(spec=Notification)
    mock_db_session.query().filter().first.return_value = mock_notification
    
    # Execute
    notification_service.update_notification_status(1, Status.PROCESSING)
    
    # Assert
    assert mock_notification.status == Status.PROCESSING
    assert mock_notification.updated_at is not None
    mock_db_session.commit.assert_called_once()

def test_update_notification_status_not_found(
    notification_service,
    mock_db_session,
    caplog
):
    # Setup
    mock_db_session.query().filter().first.return_value = None
    
    # Execute
    notification_service.update_notification_status(999, Status.PROCESSING)
    
    # Assert
    assert "Notification 999 not found" in caplog.text
    mock_db_session.commit.assert_not_called()

def test_process_notification_success(
    notification_service,
    mock_db_session,
    mock_delivery_service
):
    # Setup
    # Create mock notification with recipients
    mock_notification = MagicMock(spec=Notification)
    mock_notification.id = 1
    mock_notification.channel = Channel.EMAIL
    
    recipient1 = MagicMock(spec=NotificationRecipient)
    recipient1.email = "user1@example.com"
    
    recipient2 = MagicMock(spec=NotificationRecipient)
    recipient2.email = "user2@example.com"
    
    mock_notification.recipients = [recipient1, recipient2]
    
    mock_db_session.query().filter().first.return_value = mock_notification
    mock_delivery_service.deliver.return_value = True
    
    # Execute
    notification_service.process_notification(1)
    
    # Assert
    # Verify status updates
    assert mock_notification.status == Status.PROCESSING
    assert mock_notification.status == Status.DELIVERED
    assert mock_notification.sent_at is not None
    
    # Verify delivery attempts
    assert mock_delivery_service.deliver.call_count == 2
    mock_delivery_service.deliver.assert_has_calls([
        call(channel=Channel.EMAIL, contact_info="user1@example.com", content=mock_notification.content),
        call(channel=Channel.EMAIL, contact_info="user2@example.com", content=mock_notification.content)
    ])
    
    # Verify recipient updates
    assert recipient1.status == Status.DELIVERED
    assert recipient1.delivered_at is not None
    assert recipient2.status == Status.DELIVERED
    assert recipient2.delivered_at is not None
    
    # Verify DB commits
    assert mock_db_session.commit.call_count >= 2

def test_process_notification_with_failures(
    notification_service,
    mock_db_session,
    mock_delivery_service,
    caplog
):
    # Setup
    mock_notification = MagicMock(spec=Notification)
    mock_notification.id = 1
    mock_notification.channel = Channel.SMS
    mock_notification.content = "Test content"
    
    recipient1 = MagicMock(spec=NotificationRecipient)
    recipient1.phone_number = "+15551234567"
    
    recipient2 = MagicMock(spec=NotificationRecipient)
    recipient2.phone_number = "+15557654321"
    
    mock_notification.recipients = [recipient1, recipient2]
    mock_db_session.query().filter().first.return_value = mock_notification
    
    # First success, second fails
    mock_delivery_service.deliver.side_effect = [True, Exception("SMS failed")]
    
    # Execute
    notification_service.process_notification(1)
    
    # Assert
    # Verify status updates
    assert mock_notification.status == Status.FAILED
    
    # Verify recipient statuses
    assert recipient1.status == Status.DELIVERED
    assert recipient2.status == Status.FAILED
    assert "Failed to deliver to recipient" in caplog.text
    
    # Verify DB commits
    mock_db_session.commit.assert_called()

def test_process_recipient_success_email(notification_service, mock_delivery_service):
    # Setup
    notification = MagicMock(spec=Notification)
    notification.channel = Channel.EMAIL
    notification.content = "Test content"
    
    recipient = MagicMock(spec=NotificationRecipient)
    recipient.email = "test@example.com"
    
    mock_delivery_service.deliver.return_value = True
    
    # Execute
    notification_service._process_recipient(notification, recipient)
    
    # Assert
    mock_delivery_service.deliver.assert_called_once_with(
        channel=Channel.EMAIL,
        contact_info="test@example.com",
        content="Test content"
    )
    assert recipient.status == Status.DELIVERED
    assert recipient.delivered_at is not None

def test_process_recipient_failure_push(notification_service, mock_delivery_service, caplog):
    # Setup
    notification = MagicMock(spec=Notification)
    notification.channel = Channel.PUSH
    notification.content = "Push content"
    
    recipient = MagicMock(spec=NotificationRecipient)
    recipient.user_id = 101
    
    mock_delivery_service.deliver.side_effect = Exception("Push service down")
    
    # Execute
    notification_service._process_recipient(notification, recipient)
    
    # Assert
    assert recipient.status == Status.FAILED
    assert recipient.failed_reason == "Push service down"
    assert "Failed to deliver to recipient" in caplog.text

def test_get_contact_info(notification_service):
    # Setup
    recipient = MagicMock(spec=NotificationRecipient)
    recipient.email = "test@example.com"
    recipient.phone_number = "+15551234567"
    recipient.user_id = 101
    
    # Test email
    contact_info = notification_service._get_contact_info(Channel.EMAIL, recipient)
    assert contact_info == "test@example.com"
    
    # Test SMS
    contact_info = notification_service._get_contact_info(Channel.SMS, recipient)
    assert contact_info == "+15551234567"
    
    # Test PUSH
    contact_info = notification_service._get_contact_info(Channel.PUSH, recipient)
    assert contact_info == 101
    
    # Test invalid channel
    contact_info = notification_service._get_contact_info("invalid", recipient)
    assert contact_info == ""

def test_process_content_with_template(notification_service, mock_template_service):
    # Setup
    data = NotificationCreate(
        user_ids=[101],
        emails=[],
        sms_numbers=[],
        priority=Priority.LOW,
        channel=Channel.EMAIL,
        content="Hello {name}",
        template="welcome"
    )
    
    mock_template_service.render_template.return_value = "Hello John"
    
    # Execute
    content = notification_service._process_content(data)
    
    # Assert
    assert content == "Hello John"
    mock_template_service.render_template.assert_called_once_with(
        template_name="welcome",
        channel=Channel.EMAIL,
        variables={'content': "Hello {name}"}
    )

def test_process_content_without_template(notification_service, mock_template_service):
    # Setup
    data = NotificationCreate(
        user_ids=[101],
        emails=[],
        sms_numbers=[],
        priority=Priority.LOW,
        channel=Channel.SMS,
        content="Direct message"
    )
    
    # Execute
    content = notification_service._process_content(data)
    
    # Assert
    assert content == "Direct message"
    mock_template_service.render_template.assert_not_called()

def test_process_content_template_error(notification_service, mock_template_service, caplog):
    # Setup
    data = NotificationCreate(
        user_ids=[101],
        emails=[],
        sms_numbers=[],
        priority=Priority.LOW,
        channel=Channel.EMAIL,
        content="Hello {name}",
        template="missing_template"
    )
    
    mock_template_service.render_template.side_effect = ValueError("Template not found")
    
    # Execute
    content = notification_service._process_content(data)
    
    # Assert
    assert content == "Hello {name}"  # Falls back to original content
    assert "Error rendering template" in caplog.text