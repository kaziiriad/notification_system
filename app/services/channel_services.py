from typing import List, Dict, Any, Optional
from app.utils.interfaces import IChannelService
from app.api.schemas import Status, Channel, Priority

class EmailChannelService(IChannelService):
    """Email channel service for sending notifications via email."""

    async def send_notification(self, content: str, recipients: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Here you would implement the logic to send an email
        # For example, using an email sending library
        # This is a placeholder implementation
        return {
            "status": "success",
            "message": "Email sent successfully",
            "recipients": recipients
        }

    def validate_recipients(self, recipients: List[Dict[str, Any]]) -> bool:
        # Validate that all recipients have a valid email address
        for recipient in recipients:
            if 'email' not in recipient or not isinstance(recipient['email'], str):
                return False
        return True

class SMSChannelService(IChannelService):
    """SMS channel service for sending notifications via SMS."""

    async def send_notification(self, content: str, recipients: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Here you would implement the logic to send an SMS
        # This is a placeholder implementation
        return {
            "status": "success",
            "message": "SMS sent successfully",
            "recipients": recipients
        }

    def validate_recipients(self, recipients: List[Dict[str, Any]]) -> bool:
        # Validate that all recipients have a valid phone number
        for recipient in recipients:
            if 'phone' not in recipient or not isinstance(recipient['phone'], str):
                return False
        return True

class PushChannelService(IChannelService):
    """Push notification channel service for sending notifications via push notifications."""

    async def send_notification(self, content: str, recipients: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Here you would implement the logic to send a push notification
        # This is a placeholder implementation
        return {
            "status": "success",
            "message": "Push notification sent successfully",
            "recipients": recipients
        }

    def validate_recipients(self, recipients: List[Dict[str, Any]]) -> bool:
        # Validate that all recipients have a valid device token
        for recipient in recipients:
            if 'device_token' not in recipient or not isinstance(recipient['device_token'], str):
                return False
        return True

class ChannelServiceFactory:
    """Factory for creating channel services based on the channel type."""

    _services = {
        Channel.EMAIL: EmailChannelService(),
        Channel.SMS: SMSChannelService(),
        Channel.PUSH: PushChannelService()
    }

    @classmethod
    def create_service(cls, channel: Channel) -> Optional[IChannelService]:
        """Create a channel service based on the channel type."""
        
        service = cls._services.get(channel)
        if service is None:
            raise ValueError(f"Unsupported channel: {channel}")
        return service()

    @classmethod
    def get_all_services(cls) -> List[IChannelService]:
        """Get all available channel services."""
        return {channel: cls.create_service(channel) for channel in cls._services.keys()}

