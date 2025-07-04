import os
from typing import List, Dict, Any, Optional
from app.utils.interfaces import IChannelService
from app.api.schemas import Channel
from app.core.config import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging

logger = logging.getLogger(__name__)

class EmailChannelService(IChannelService):
    """Email channel service for sending notifications via email using SendGrid."""

    def __init__(self):
        self.api_key = settings.SENDGRID_API_KEY
        self.from_email = settings.SENDGRID_FROM_EMAIL
        if not self.api_key:
            raise ValueError("SENDGRID_API_KEY is not configured.")
        if not self.from_email:
            raise ValueError("SENDGRID_FROM_EMAIL is not configured.")

    async def send_notification(self, subject: str, content: str, recipients: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sends an email notification using the SendGrid API.
        """
        if not self.validate_recipients(recipients):
            return {
                "status": "error",
                "message": "Invalid recipients for email channel.",
                "failed_recipients": recipients
            }

        message = Mail(
            from_email=self.from_email,
            to_emails=[r['email'] for r in recipients],
            subject=subject or 'New Notification',
            html_content=content
        )
        
        try:
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)
            
            if 200 <= response.status_code < 300:
                return {
                    "status": "success",
                    "message": "Email sent successfully.",
                    "recipients": recipients
                }
            else:
                logger.error(f"Failed to send email: {response.body}")
                return {
                    "status": "error",
                    "message": "Failed to send email.",
                    "details": response.body
                }
        except Exception as e:
            logger.exception("An error occurred while sending email with SendGrid.")
            return {
                "status": "error",
                "message": "An unexpected error occurred.",
                "details": str(e)
            }

    def validate_recipients(self, recipients: List[Dict[str, Any]]) -> bool:
        """Validate that all recipients have a valid email address."""
        for recipient in recipients:
            if 'email' not in recipient or not isinstance(recipient['email'], str):
                return False
        return True

class SMSChannelService(IChannelService):
    """SMS channel service for sending notifications via SMS."""

    async def send_notification(self, subject: str, content: str, recipients: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Here you would implement the logic to send an SMS
        # This is a placeholder implementation
        # TODO: Integrate with an SMS gateway
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

    async def send_notification(self, subject: str, content: str, recipients: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Here you would implement the logic to send a push notification
        # This is a placeholder implementation
        # TODO: Implement actual push notification logic
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
        return service

    @classmethod
    def get_all_services(cls) -> Dict[Channel, IChannelService]:
        """Get all available channel services."""
        return cls._services

