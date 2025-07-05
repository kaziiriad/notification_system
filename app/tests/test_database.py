import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.sql.models import Base, Notification, NotificationRecipient as Recipient
from app.db.sql.repositories import NotificationRepository
from app.api.schemas import Status, Channel, Priority
import uuid
from datetime import datetime, timezone

# Setup an in-memory SQLite database for testing
@pytest.fixture(scope="module")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="module")
def notification_repository(db_session):
    return NotificationRepository(db_session)

@pytest.mark.asyncio
async def test_create_notification(notification_repository: NotificationRepository, db_session):
    notification_data = {
        "subject": "DB Test",
        "content": "Testing database creation",
        "channel": Channel.SMS,
        "priority": Priority.MEDIUM,
        "status": Status.QUEUED
    }
    notification = notification_repository.create_notification(notification_data)
    db_session.commit()

    assert notification.id is not None
    assert notification.subject == "DB Test"
    
    # Verify it's in the database
    retrieved = db_session.query(Notification).filter_by(id=notification.id).first()
    assert retrieved is not None

@pytest.mark.asyncio
async def test_create_recipients(notification_repository: NotificationRepository, db_session):
    # First, create a notification to associate with
    notification = Notification(
        id=str(uuid.uuid4()),
        subject="Recipient Test",
        content="Testing recipient creation",
        channel=Channel.EMAIL,
        priority=Priority.LOW,
        status=Status.QUEUED,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(notification)
    db_session.commit()

    recipients_data = [
        {"notification_id": notification.id, "user_id": 1, "email": "user1@test.com"},
        {"notification_id": notification.id, "user_id": None, "email": "user2@test.com"},
    ]
    notification_repository.create_recipients(notification.id, recipients_data)
    db_session.commit()

    # Verify recipients are in the database
    recipients = db_session.query(Recipient).filter_by(notification_id=notification.id).all()
    assert len(recipients) == 2
    assert recipients[0].email == "user1@test.com"

@pytest.mark.asyncio
async def test_get_notification_by_id(notification_repository: NotificationRepository, db_session):
    notification = Notification(
        id=str(uuid.uuid4()),
        subject="Get Test",
        content="Testing retrieval",
        channel=Channel.PUSH,
        priority=Priority.HIGH,
        status=Status.SENT,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(notification)
    db_session.commit()

    retrieved = notification_repository.get_notification_by_id(notification.id)
    assert retrieved is not None
    assert retrieved.id == notification.id
    assert retrieved.status == Status.SENT

@pytest.mark.asyncio
async def test_update_notification_status(notification_repository: NotificationRepository, db_session):
    notification = Notification(
        id=str(uuid.uuid4()),
        subject="Update Test",
        content="Testing status update",
        channel=Channel.EMAIL,
        priority=Priority.HIGH,
        status=Status.QUEUED,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(notification)
    db_session.commit()

    notification_repository.update_notification_status(notification.id, Status.FAILED)
    db_session.commit()

    updated = db_session.query(Notification).filter_by(id=notification.id).first()
    assert updated.status == Status.FAILED
