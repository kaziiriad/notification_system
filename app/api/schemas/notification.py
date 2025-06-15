from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from .common import Priority, Channel


class NotificationCreate(BaseModel):
    """Schema for creating a new notification"""
    
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

    @field_validator('sms_numbers')
    @classmethod
    def validate_sms_numbers(cls, v):
        if v:  # Only validate if sms_numbers are provided
            for number in v:
                if not number.strip():
                    raise ValueError('SMS numbers cannot be empty')
        return v


class NotificationResponse(BaseModel):
    """Schema for notification creation response"""
    
    id: int
    status: str
    message: str
    created_at: datetime
    scheduled_at: Optional[datetime] = None


class NotificationStatus(BaseModel):
    """Schema for notification status response"""
    
    id: int
    status: str
    sent_at: Optional[datetime] = None
    delivered_count: int
    failed_count: int
    pending_count: int


class NotificationListResponse(BaseModel):
    """Schema for listing notifications"""
    
    notifications: List[NotificationResponse]
    total: int
    page: int
    per_page: int