
from datetime import datetime
from typing import List
from app.api.schemas import NotificationCreate, Channel

class NotificationValidator:
    """Validates notification requests and business rules"""
    
    @staticmethod
    def validate_request(request: NotificationCreate) -> List[str]:
        """Validate notification request"""
        errors = []
        
        # Check if we have any recipients
        if not request.user_ids and not request.emails and not request.sms_numbers:
            errors.append("At least one recipient must be specified")
        
        # Validate channel-specific requirements
        if request.channel == Channel.EMAIL and not request.user_ids and not request.emails:
            errors.append("Email channel requires either user_ids or email addresses")
        
        if request.channel == Channel.SMS and not request.user_ids and not request.sms_numbers:
            errors.append("SMS channel requires either user_ids or SMS numbers")
        
        if request.channel == Channel.PUSH and not request.user_ids:
            errors.append("Push channel requires user_ids")
        
        # Validate content
        if not request.content or not request.content.strip():
            errors.append("Content cannot be empty")
        
        # Validate scheduled time
        if request.scheduled_at and request.scheduled_at <= datetime.utcnow():
            errors.append("Scheduled time must be in the future")
        
        return errors

