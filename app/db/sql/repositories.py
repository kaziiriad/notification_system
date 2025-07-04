
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from .models import Notification, NotificationRecipient
from app.utils.interfaces import INotificationRepository
from app.api.schemas import Status

class NotificationRepository(INotificationRepository):
    """Concrete implementation of notification repository"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create_notification(self, notification_data: dict) -> Notification:
        notification = Notification(**notification_data)
        self.db.add(notification)
        return notification
    
    def create_recipients(self, notification_id: str, recipients_data: List[dict]) -> List[NotificationRecipient]:
        """Create recipient records for a notification"""
        notification = self.get_notification_by_id(notification_id)
        recipients = []
        for recipient_data in recipients_data:
            recipient_data['notification_id'] = notification_id
            recipient = NotificationRecipient(**recipient_data)
            recipients.append(recipient)
            self.db.add(recipient)
        
        return recipients
    
    def get_notification_by_id(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID"""
        return self.db.query(Notification).filter(Notification.id == notification_id).first()
    
    def get_recipients_by_notification_id(self, notification_id: str) -> List[NotificationRecipient]:
        """Get all recipients for a given notification"""
        return self.db.query(NotificationRecipient).filter(NotificationRecipient.notification_id == notification_id).all()

    def list_notifications(self, page: int, page_size: int) -> (List[Notification], int):
        """List all notifications with pagination"""
        
        query = self.db.query(Notification).order_by(Notification.created_at.desc())
        
        total_count = query.count()
        
        notifications = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return notifications, total_count

    def update_notification_status(self, notification_id: str, status: Status, failure_reason: Optional[str] = None) -> bool:
        """Update notification status"""
        try:
            update_data = {"status": status, "updated_at": datetime.now(timezone.utc)}
            # Note: failure_reason is not stored in Notification model, only in NotificationRecipient
            # If you need to store failure_reason at notification level, add the field to the model
            
            self.db.query(Notification).filter(Notification.id == notification_id).update(update_data)
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
