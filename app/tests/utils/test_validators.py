import pytest
from datetime import datetime, timedelta, timezone
from app.utils.validators import NotificationValidator
from app.api.schemas import NotificationCreate, Channel, Priority

@pytest.fixture
def valid_request():
    """Fixture for a valid NotificationCreate object."""
    return NotificationCreate(
        user_ids=[1],
        channel=Channel.EMAIL,
        priority=Priority.HIGH,
        subject="Test",
        content="Valid content"
    )

def test_validate_request_valid(valid_request):
    """Test a completely valid request."""
    errors = NotificationValidator.validate_request(valid_request)
    assert not errors

def test_validate_request_no_recipients(valid_request):
    """Test request with no recipients specified."""
    valid_request.user_ids = []
    valid_request.emails = []
    valid_request.sms_numbers = []
    errors = NotificationValidator.validate_request(valid_request)
    assert "At least one recipient must be specified" in errors

def test_validate_email_channel_requirements(valid_request):
    """Test validation for email channel without email recipients."""
    valid_request.channel = Channel.EMAIL
    valid_request.user_ids = []
    valid_request.emails = []
    errors = NotificationValidator.validate_request(valid_request)
    assert "Email channel requires either user_ids or email addresses" in errors

def test_validate_sms_channel_requirements(valid_request):
    """Test validation for SMS channel without SMS recipients."""
    valid_request.channel = Channel.SMS
    valid_request.user_ids = []
    valid_request.sms_numbers = []
    errors = NotificationValidator.validate_request(valid_request)
    assert "SMS channel requires either user_ids or SMS numbers" in errors

def test_validate_push_channel_requirements(valid_request):
    """Test validation for push channel without user_ids."""
    valid_request.channel = Channel.PUSH
    valid_request.user_ids = []
    errors = NotificationValidator.validate_request(valid_request)
    assert "Push channel requires user_ids" in errors

def test_validate_empty_content(valid_request):
    """Test request with empty or whitespace-only content."""
    valid_request.content = "   "
    errors = NotificationValidator.validate_request(valid_request)
    assert "Content cannot be empty" in errors

def test_validate_scheduled_time_in_past(valid_request):
    """Test request with a scheduled time in the past."""
    past_time = datetime.now(timezone.utc) - timedelta(minutes=10)
    valid_request.scheduled_at = past_time
    errors = NotificationValidator.validate_request(valid_request)
    assert "Scheduled time must be in the future" in errors

def test_validate_scheduled_time_in_future(valid_request):
    """Test request with a valid scheduled time in the future."""
    future_time = datetime.now(timezone.utc) + timedelta(minutes=10)
    valid_request.scheduled_at = future_time
    errors = NotificationValidator.validate_request(valid_request)
    assert "Scheduled time must be in the future" not in errors
