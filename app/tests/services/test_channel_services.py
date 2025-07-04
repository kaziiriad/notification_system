import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.channel_services import (
    EmailChannelService,
    SMSChannelService,
    PushChannelService,
    ChannelServiceFactory,
)
from app.api.schemas import Channel

# Tests for ChannelServiceFactory
def test_factory_creates_email_service():
    """Test that the factory correctly creates an EmailChannelService."""
    with patch('app.services.channel_services.settings') as mock_settings:
        mock_settings.SENDGRID_API_KEY = "test_key"
        mock_settings.SENDGRID_FROM_EMAIL = "test@example.com"
        service = ChannelServiceFactory.create_service(Channel.EMAIL)
        assert isinstance(service, EmailChannelService)

def test_factory_creates_sms_service():
    """Test that the factory correctly creates an SMSChannelService."""
    service = ChannelServiceFactory.create_service(Channel.SMS)
    assert isinstance(service, SMSChannelService)

def test_factory_creates_push_service():
    """Test that the factory correctly creates a PushChannelService."""
    service = ChannelServiceFactory.create_service(Channel.PUSH)
    assert isinstance(service, PushChannelService)

def test_factory_raises_error_for_unsupported_channel():
    """Test that the factory raises a ValueError for an unsupported channel."""
    with pytest.raises(ValueError):
        ChannelServiceFactory.create_service("unsupported_channel")

# Tests for EmailChannelService
@pytest.fixture
def email_service():
    """Pytest fixture for an EmailChannelService instance with mocked settings."""
    with patch('app.services.channel_services.settings') as mock_settings:
        mock_settings.SENDGRID_API_KEY = "test_api_key"
        mock_settings.SENDGRID_FROM_EMAIL = "from@example.com"
        yield EmailChannelService()

@pytest.mark.asyncio
async def test_email_send_notification_success(email_service):
    """Test successful email sending."""
    with patch('app.services.channel_services.SendGridAPIClient') as mock_sendgrid:
        mock_sg_instance = MagicMock()
        mock_sg_instance.send.return_value = MagicMock(status_code=202)
        mock_sendgrid.return_value = mock_sg_instance

        recipients = [{"email": "to@example.com"}]
        response = await email_service.send_notification("Subject", "Content", recipients)

        assert response["status"] == "success"
        mock_sg_instance.send.assert_called_once()

@pytest.mark.asyncio
async def test_email_send_notification_failure(email_service):
    """Test failed email sending."""
    with patch('app.services.channel_services.SendGridAPIClient') as mock_sendgrid:
        mock_sg_instance = MagicMock()
        mock_sg_instance.send.return_value = MagicMock(status_code=400, body="Error")
        mock_sendgrid.return_value = mock_sg_instance

        recipients = [{"email": "to@example.com"}]
        response = await email_service.send_notification("Subject", "Content", recipients)

        assert response["status"] == "error"
        assert response["details"] == "Error"

def test_email_validate_recipients_valid(email_service):
    """Test recipient validation with valid recipients."""
    recipients = [{"email": "test1@example.com"}, {"email": "test2@example.com"}]
    assert email_service.validate_recipients(recipients) is True

def test_email_validate_recipients_invalid(email_service):
    """Test recipient validation with invalid recipients."""
    recipients = [{"email": "test1@example.com"}, {"not_email": "invalid"}]
    assert email_service.validate_recipients(recipients) is False

def test_email_service_missing_api_key():
    """Test that EmailChannelService raises an error if API key is missing."""
    with patch('app.services.channel_services.settings') as mock_settings:
        mock_settings.SENDGRID_API_KEY = None
        mock_settings.SENDGRID_FROM_EMAIL = "from@example.com"
        with pytest.raises(ValueError, match="SENDGRID_API_KEY is not configured"):
            EmailChannelService()

def test_email_service_missing_from_email():
    """Test that EmailChannelService raises an error if from_email is missing."""
    with patch('app.services.channel_services.settings') as mock_settings:
        mock_settings.SENDGRID_API_KEY = "test_api_key"
        mock_settings.SENDGRID_FROM_EMAIL = None
        with pytest.raises(ValueError, match="SENDGRID_FROM_EMAIL is not configured"):
            EmailChannelService()
