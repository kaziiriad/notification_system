from time import strptime
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Channel(str, Enum):

    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"
    ALL = "all"

class NotificationCreate(BaseModel):

    user_ids: List[int] = Field(..., description="List of user IDs to notify.")
    emails: List[EmailStr] = Field(default=[], description="List of email addresses to notify.")
    sms_numbers: List[str] = Field(default=[], description="List of SMS numbers to notify.")
    priority: Priority = Field(..., description="Priority of the notification.")
    channel: Channel = Field(..., description="Channel to send the notification to.")
    content: str = Field(..., description="Content of the notification.")
    template: Optional[str] = None
    scheduled_at: Optional[datetime] = Field(
        None, 
        description="Optional scheduled time for the notification. If not provided, notification is sent immediately."
    )

    @field_validator('user_ids')
    @classmethod
    def validate_user_ids(cls, v):
        if not v:
            raise ValueError('At least one user ID must be provided')
        if any(user_id <= 0 for user_id in v):
            raise ValueError('All user IDs must be positive integers')
        return v
    
