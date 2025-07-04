import pytest
from unittest.mock import patch, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.sql.connection import Base
from app.services.notification_service import NotificationService
from app.api.schemas import NotificationCreate, Priority, Channel, Status
from app.db.sql.repositories import NotificationRepository

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Fixture to create a new database session for each test function."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.mark.asyncio
async def test_create_and_retrieve_notification(db_session):
    """
    Integration test to verify creating and retrieving a notification.
    """
    # Arrange
    notification_service = NotificationService(db_session)
    notification_repo = NotificationRepository(db_session)
    
    request = NotificationCreate(
        user_ids=[1],
        priority=Priority.HIGH,
        channel=Channel.EMAIL,
        subject="Integration Test",
        content="This is an integration test."
    )

    # Act
    with patch('app.services.notification_service.send_notification_task.delay'):
        created_notification_response = await notification_service.create_notification(request)
    
    retrieved_notification = notification_repo.get_notification_by_id(created_notification_response.id)

    # Assert
    assert retrieved_notification is not None
    assert retrieved_notification.id == created_notification_response.id
    assert retrieved_notification.subject == "Integration Test"
    assert retrieved_notification.content == "This is an integration test."
    assert retrieved_notification.status == Status.PENDING

@pytest.mark.asyncio
async def test_process_notification(db_session):
    """
    Integration test to verify processing a notification.
    """
    # Arrange
    notification_service = NotificationService(db_session)
    
    request = NotificationCreate(
        user_ids=[1],
        priority=Priority.HIGH,
        channel=Channel.EMAIL,
        subject="Process Test",
        content="This is a process test."
    )

    with patch('app.services.notification_service.send_notification_task.delay'):
        created_notification_response = await notification_service.create_notification(request)

    # Act
    with patch('app.services.channel_services.EmailChannelService.send_notification', new_callable=AsyncMock) as mock_send:
        await notification_service.process_notification(created_notification_response.id)

    # Assert
    retrieved_notification = notification_service.get_notification_status(created_notification_response.id)
    assert retrieved_notification.status == Status.SENT
    mock_send.assert_called_once()
