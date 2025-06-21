
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.sql.models import Notification, NotificationRecipient
from app.utils.interfaces import INotificationRepository
from app.api.schemas import Status

class NotificationRepository(INotificationRepository):
    """Concrete implementation of notification repository"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create_notification(self, notification_data: dict) -> Notification:
        """Create a new notification record"""
        notification = Notification(**notification_data)
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    def create_recipients(self, notification_id: int, recipients_data: List[dict]) -> List[NotificationRecipient]:
        """Create recipient records for a notification"""
        recipients = []
        for recipient_data in recipients_data:
            recipient_data['notification_id'] = notification_id
            recipient = NotificationRecipient(**recipient_data)
            recipients.append(recipient)
            self.db.add(recipient)
        
        self.db.commit()
        for recipient in recipients:
            self.db.refresh(recipient)
        return recipients
    
    def get_notification_by_id(self, notification_id: int) -> Optional[Notification]:
        """Get notification by ID"""
        return self.db.query(Notification).filter(Notification.id == notification_id).first()
    
    def update_notification_status(self, notification_id: int, status: Status) -> bool:
        """Update notification status"""
        try:
            self.db.query(Notification).filter(Notification.id == notification_id).update(
                {"status": status, "updated_at": datetime.utcnow()}
            )
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False
