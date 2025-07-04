import pytest
from unittest.mock import MagicMock, patch
from app.services.recipient_resolver import RecipientResolver
from app.api.schemas import NotificationCreate, Channel, Priority

@pytest.fixture
def mock_user_service():
    """Pytest fixture for a mock user service."""
    return MagicMock()

@pytest.fixture
def recipient_resolver(mock_user_service):
    """Pytest fixture for a RecipientResolver instance."""
    with patch('app.services.recipient_resolver.user_service', mock_user_service):
        resolver = RecipientResolver()
        yield resolver

def test_resolve_recipients_email_channel(recipient_resolver, mock_user_service):
    """Test resolving recipients for the EMAIL channel."""
    # Arrange
    request = NotificationCreate(
        user_ids=[1],
        emails=["direct@example.com"],
        priority=Priority.HIGH,
        channel=Channel.EMAIL,
        subject="Test",
        content="Test"
    )
    mock_user_service.get_user_by_id.return_value = {"id": 1, "email": "user1@example.com"}

    # Act
    recipients = recipient_resolver.resolve_recipients(request, Channel.EMAIL)

    # Assert
    assert len(recipients) == 2
    assert {'user_id': 1, 'email': 'user1@example.com', 'phone_number': None, 'push_token': None} in recipients
    assert {'user_id': None, 'email': 'direct@example.com', 'phone_number': None, 'push_token': None} in recipients

def test_resolve_recipients_sms_channel(recipient_resolver, mock_user_service):
    """Test resolving recipients for the SMS channel."""
    # Arrange
    request = NotificationCreate(
        user_ids=[1],
        sms_numbers=["+1234567890"],
        priority=Priority.HIGH,
        channel=Channel.SMS,
        subject="Test",
        content="Test"
    )
    mock_user_service.get_user_by_id.return_value = {"id": 1, "phone_number": "+1111111111"}

    # Act
    recipients = recipient_resolver.resolve_recipients(request, Channel.SMS)

    # Assert
    assert len(recipients) == 2
    assert {'user_id': 1, 'email': None, 'phone_number': '+1111111111', 'push_token': None} in recipients
    assert {'user_id': None, 'email': None, 'phone_number': '+1234567890', 'push_token': None} in recipients

def test_resolve_recipients_push_channel(recipient_resolver, mock_user_service):
    """Test resolving recipients for the PUSH channel."""
    # Arrange
    request = NotificationCreate(
        user_ids=[1],
        priority=Priority.HIGH,
        channel=Channel.PUSH,
        subject="Test",
        content="Test"
    )
    mock_user_service.get_user_by_id.return_value = {"id": 1, "push_token": "push_token_123"}

    # Act
    recipients = recipient_resolver.resolve_recipients(request, Channel.PUSH)

    # Assert
    assert len(recipients) == 1
    assert {'user_id': 1, 'email': None, 'phone_number': None, 'push_token': 'push_token_123'} in recipients

def test_resolve_recipients_all_channels(recipient_resolver, mock_user_service):
    """Test resolving recipients for the ALL channel."""
    # Arrange
    request = NotificationCreate(
        user_ids=[1],
        emails=["direct@example.com"],
        sms_numbers=["+1234567890"],
        priority=Priority.HIGH,
        channel=Channel.ALL,
        subject="Test",
        content="Test"
    )
    mock_user_service.get_user_by_id.return_value = {
        "id": 1,
        "email": "user1@example.com",
        "phone_number": "+1111111111",
        "push_token": "push_token_123"
    }

    # Act
    recipients = recipient_resolver.resolve_recipients(request, Channel.ALL)

    # Assert
    assert len(recipients) == 5 # 3 from user, 2 direct
    # Check user-derived recipients
    assert {'user_id': 1, 'email': 'user1@example.com', 'phone_number': None, 'push_token': None} in recipients
    assert {'user_id': 1, 'email': None, 'phone_number': '+1111111111', 'push_token': None} in recipients
    assert {'user_id': 1, 'email': None, 'phone_number': None, 'push_token': 'push_token_123'} in recipients
    # Check direct recipients
    assert {'user_id': None, 'email': 'direct@example.com', 'phone_number': None, 'push_token': None} in recipients
    assert {'user_id': None, 'email': None, 'phone_number': '+1234567890', 'push_token': None} in recipients

def test_resolve_recipients_user_not_found(recipient_resolver, mock_user_service):
    """Test that a user not found is handled gracefully."""
    # Arrange
    request = NotificationCreate(
        user_ids=[999], # Non-existent user
        priority=Priority.HIGH,
        channel=Channel.EMAIL,
        subject="Test",
        content="Test"
    )
    mock_user_service.get_user_by_id.return_value = None

    # Act
    recipients = recipient_resolver.resolve_recipients(request, Channel.EMAIL)

    # Assert
    assert len(recipients) == 0
    mock_user_service.get_user_by_id.assert_called_once_with(999)
