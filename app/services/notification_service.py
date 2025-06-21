from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from app.db.sql.repositories import NotificationRepository
from app.api.schemas import (
    NotificationCreate,
    NotificationResponse,
    Status,
    Channel
)
from .recipient_resolver import RecipientResolver
from .channel_services import ChannelServiceFactory
from app.utils.validators import NotificationValidator
from app.db.sql.models import Notification  
import logging

logger = logging.getLogger(__name__)




class NotificationService:

    def __init__(self, db_session: Session):
        self.db = db_session
        self.notification_repository = NotificationRepository(self.db)
        self.recipient_resolver = RecipientResolver(self.db)
        self.validator = NotificationValidator()

    async def create_notification(self, request: NotificationCreate) -> NotificationResponse:
        
        try:
            # step 1: Validate the request
            errors = self.validator.validate_request(request)
            if errors:
                raise ValueError(f"Validation errors: {', '.join(errors)}")


            # step 2: create the notification record
            notification_data = {
                "id": str(uuid.uuid4()),
                "content": request.content,
                "channel": request.channel,
                "priority": request.priority,
                "scheduled_at": request.scheduled_at or datetime.now(timezone.utc),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "status": Status.PENDING
            }
            notification = self.notification_repository.create_notification(notification_data)


            # step 3: resolve and create recipients
            if request.channel == Channel.ALL:
                # Resolve recipients for all channels
                all_recipients = []
                for channel in [Channel.EMAIL, Channel.SMS, Channel.PUSH]:
                    recipients = self.recipient_resolver.resolve_recipients(request, channel)
                    all_recipients.extend(recipients)
                recipients = all_recipients
            else:
                # Resolve recipients for the specified channel
                recipients = self.recipient_resolver.resolve_recipients(request, request.channel)

            if not recipients:
                raise ValueError("No valid recipients found for the notification.")
            # Create recipient records in the database
            self.notification_repository.create_recipients(notification.id, recipients)

            # step 4: send or schedule the notification
            if request.scheduled_at and request.scheduled_at > datetime.now(timezone.utc):
                # TODO: Schedule the notification for later
                logger.info(f"Notification {notification.id} scheduled for {request.scheduled_at}")
            else:
                # Send the notification immediately
                await self._send_notification(notification, recipients, request.channel)
                logger.info(f"Notification {notification.id} sent immediately")
            
            # step 5: return the response
            response = NotificationResponse(
                id=notification.id,
                status=notification.status.value,
                created_at=notification.created_at,
                scheduled_at=notification.scheduled_at
            )
            return response
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            self.db.rollback()  # Rollback the transaction in case of error
            self.notification_repository.update_notification_status(notification.id, Status.FAILED)
            raise e

    async def _send_notification(self, notification: Notification, recipient: List[Dict[str, Any]], channel: Channel) -> None:
        """
        Placeholder for the actual notification sending logic.
        This method should handle the logic to send the notification
        via the appropriate channel (email, SMS, push, etc.).
        """        

        try:

            self.repository.update_notification_status(notification.id, Status.PROCESSING)


            if channel == Channel.ALL:
                services = ChannelServiceFactory.get_all_services()
                for ch, service in services.items():
                    channel_recipients = [r for r in recipient if r.get('channel') == ch]
                    if channel_recipients and service.validate_recipients(channel_recipients):
                        await service.send_notification(notification.content, channel_recipients)
            else:
                service = ChannelServiceFactory.get_service(channel)
                if service and service.validate_recipients(recipient):
                    await service.send_notification(notification.content, recipient)
            
            # Update notification status to SENT
            self.notification_repository.update_notification_status(notification.id, Status.SENT)
        except Exception as e:
            logger.error(f"Error sending notification {notification.id}: {e}")
            self.notification_repository.update_notification_status(notification.id, Status.FAILED)
            raise e

        def _is_recipient_for_channel(self, recipient: Dict[str, Any], channel: Channel) -> bool:
            """
            Check if the recipient is valid for the specified channel.
            """
            if channel == Channel.EMAIL:
                return recipient.get('email') is not None
            elif channel == Channel.SMS:
                return recipient.get('phone_number') is not None
            elif channel == Channel.PUSH:
                return recipient.get('push_token') is not None
            return True

        def get_notification_status(self, notification_id: int) -> Optional[Notification]:
            """
            Get the status of a notification by its ID.
            """
            return self.notification_repository.get_notification_by_id(notification_id)

    
        
    