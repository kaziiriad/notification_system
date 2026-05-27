
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from .models import Notification, NotificationRecipient
from app.utils.interfaces import INotificationRepository
from app.api.schemas import Status
from app.core.cache import cache

class NotificationRepository(INotificationRepository):
    """Concrete implementation of notification repository"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def create_notification(self, notification_data: dict) -> Notification:
        notification = Notification(**notification_data)
        self.db.add(notification)
        self.db.flush()
        return notification

    def create_recipients(self, notification_id: str, recipients_data: List[dict]) -> List[NotificationRecipient]:
        """Create recipient records for a notification"""
        recipients = []
        for recipient_data in recipients_data:
            recipient_data['notification_id'] = notification_id
            recipient = NotificationRecipient(**recipient_data)
            recipients.append(recipient)
            self.db.add(recipient)

        return recipients

    def get_notification_by_id(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID with caching."""
        # Try cache first
        cached = cache.get("notification", notification_id)
        if cached:
            # Return notification from DB (cached data is for response enrichment only)
            notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
            return notification

        # Cache miss - fetch from DB
        notification = self.db.query(Notification).filter(Notification.id == notification_id).first()

        if notification:
            # Cache the status for quick lookup
            cache.set("notification", notification_id, {
                "id": notification.id,
                "status": notification.status.value,
                "created_at": notification.created_at.isoformat() if notification.created_at else None,
                "scheduled_at": notification.scheduled_at.isoformat() if notification.scheduled_at else None,
            })

        return notification

    def get_recipients_by_notification_id(self, notification_id: str) -> List[NotificationRecipient]:
        """Get all recipients for a given notification"""
        return self.db.query(NotificationRecipient).filter(NotificationRecipient.notification_id == notification_id).all()

    def list_notifications(self, page: int, page_size: int) -> Tuple[List[Notification], int]:
        """List all notifications with pagination"""

        query = self.db.query(Notification).order_by(Notification.created_at.desc())

        total_count = query.count()

        notifications = query.offset((page - 1) * page_size).limit(page_size).all()

        return notifications, total_count

    def update_notification_status(self, notification_id: str, status: Status, failure_reason: Optional[str] = None) -> bool:
        """Update notification status"""
        try:
            update_data = {"status": status, "updated_at": datetime.now(timezone.utc)}

            self.db.query(Notification).filter(Notification.id == notification_id).update(update_data)

            # Invalidate cache on status update
            cache.delete("notification", notification_id)

            return True
        except Exception:
            self.db.rollback()
            return False

    def update_recipient_status(self, recipient_id: int, status: Status, failure_reason: Optional[str] = None) -> bool:
        """Update recipient status and failure reason if provided"""
        try:
            update_data = {"status": status, "updated_at": datetime.now(timezone.utc)}
            if failure_reason:
                update_data["failed_reason"] = failure_reason
            
            self.db.query(NotificationRecipient).filter(NotificationRecipient.id == recipient_id).update(update_data)
            return True
        except Exception:
            self.db.rollback()
            return False
