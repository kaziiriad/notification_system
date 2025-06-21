from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.db.sql.models import Notification, NotificationRecipient
from app.api.schemas import Status, Channel, Priority


class IChannelService(ABC):
    """Interface for channel-specific notification services"""
    
    @abstractmethod
    async def send_notification(self, content: str, recipients: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send notification through specific channel"""
        pass
    
    @abstractmethod
    def validate_recipients(self, recipients: List[Dict[str, Any]]) -> bool:
        """Validate recipients for this channel"""
        pass


class INotificationRepository(ABC):
    """Interface for notification data access"""
    
    @abstractmethod
    def create_notification(self, notification_data: dict) -> Notification:
        """Create a new notification record"""
        pass
    
    @abstractmethod
    def create_recipients(self, notification_id: int, recipients_data: List[dict]) -> List[NotificationRecipient]:
        """Create recipient records for a notification"""
        pass
    
    @abstractmethod
    def get_notification_by_id(self, notification_id: int) -> Optional[Notification]:
        """Get notification by ID"""
        pass
    
    @abstractmethod
    def update_notification_status(self, notification_id: int, status: Status) -> bool:
        """Update notification status"""
        pass
