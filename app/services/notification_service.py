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
from app.worker.tasks import send_notification_task
import logging

logger = logging.getLogger(__name__)

class NotificationService:

    def __init__(self, db_session: Session):
        self.db = db_session
        self.notification_repository = NotificationRepository(self.db)
        self.recipient_resolver = RecipientResolver()
        self.validator = NotificationValidator()

    async def create_notification(self, request: NotificationCreate) -> NotificationResponse:
        """        Create a new notification and send it to the specified recipients.
        This method handles the entire process of creating a notification, resolving recipients,
        and sending the notification through the appropriate channels.
        Args:
            request (NotificationCreate): The request object containing notification details.
        Returns:
            NotificationResponse: The response object containing the notification ID and status.
        Raises:
            ValueError: If there are validation errors or if no valid recipients are found.
            Exception: For any other errors that occur during the process.
        """
        # Initialize notification variable to None
        
        notification = None

        try:
            # step 1: Validate the request
            errors = self.validator.validate_request(request)
            if errors:
                raise ValueError(f"Validation errors: {', '.join(errors)}")

            # step 2: create the notification record
            notification_data = {
                "id": str(uuid.uuid4()),
                "subject": request.subject,
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
            
            # Determine the final status and schedule/queue the notification
            if request.scheduled_at and request.scheduled_at > datetime.now(timezone.utc):
                # Schedule the notification for later
                send_notification_task.apply_async(
                    (notification.id,),
                    eta=request.scheduled_at
                )
                self.notification_repository.update_notification_status(notification.id, Status.SCHEDULED)
                final_status = Status.SCHEDULED
                logger.info(f"Notification {notification.id} scheduled for {request.scheduled_at}")
            else:
                # Send the notification immediately
                send_notification_task.delay(notification.id)
                self.notification_repository.update_notification_status(notification.id, Status.QUEUED)
                final_status = Status.QUEUED
                logger.info(f"Notification {notification.id} queued for immediate sending")
            
            self.db.commit()
            self.db.refresh(notification)
            
            # step 5: return the response
            response = NotificationResponse(
                id=notification.id,
                status=final_status.value,
                created_at=notification.created_at,
                scheduled_at=notification.scheduled_at
            )
            return response
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            # Only update notification status if notification was successfully created
            if notification is not None and hasattr(notification, 'id'):
                try:
                    self.notification_repository.update_notification_status(notification.id, Status.FAILED)
                except Exception as update_error:
                    logger.error(f"Failed to update notification status to FAILED: {update_error}")
            self.db.rollback()  # Rollback the transaction in case of error
            raise e

    async def process_notification(self, notification_id: str):
        """
        Process and send a notification. This method is intended to be called by a Celery worker.
        """
        notification = self.get_notification_status(notification_id)
        if not notification:
            logger.error(f"Notification {notification_id} not found for processing.")
            return

        try:
            self.notification_repository.update_notification_status(notification.id, Status.PROCESSING)
            self.db.commit()

            recipients = self.notification_repository.get_recipients_by_notification_id(notification.id)
            recipient_list = [
                {"email": r.email, "phone_number": r.phone_number, "push_token": r.push_token}
                for r in recipients
            ]

            if notification.channel == Channel.ALL:
                services = ChannelServiceFactory.get_all_services()
                for ch, service in services.items():
                    channel_recipients = [r for r in recipient_list if self._is_recipient_for_channel(r, ch)]
                    if channel_recipients and service.validate_recipients(channel_recipients):
                        await service.send_notification(notification.subject, notification.content, channel_recipients)
            else:
                service = ChannelServiceFactory.create_service(notification.channel)
                if service and service.validate_recipients(recipient_list):
                    await service.send_notification(notification.subject, notification.content, recipient_list)
            
            self.notification_repository.update_notification_status(notification.id, Status.SENT)
            self.db.commit()
        except Exception as e:
            logger.exception(f"Error processing notification {notification.id}")
            self.notification_repository.update_notification_status(notification.id, Status.FAILED, failure_reason=str(e))
            self.db.commit()
            # Optionally re-raise the exception if you want Celery to handle retries
            # raise e


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

    def get_notification_status(self, notification_id: str) -> Optional[Notification]:
        """
        Get the status of a notification by its ID.
        """
        if not notification_id:
            raise ValueError("Notification ID must be provided")
        return self.notification_repository.get_notification_by_id(notification_id)

    def list_notifications(self, page: int, page_size: int) -> (List[Notification], int):
        """
        List all notifications with pagination.
        """
        return self.notification_repository.list_notifications(page, page_size)

    
        
    