from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class LogStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRY = "retry"

class LogChannel(str, Enum):
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"

class NotificationLogEntry(BaseModel):
    """Single log entry for notification events"""
    
    # Core identifiers
    notification_id: int = Field(..., description="Reference to SQL notification ID")
    recipient_id: Optional[int] = Field(None, description="Reference to SQL recipient ID")
    
    # Event details
    channel: LogChannel = Field(..., description="Notification channel")
    status: LogStatus = Field(..., description="Current status")
    message: str = Field(..., description="Log message")
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Optional fields for debugging
    external_id: Optional[str] = Field(None, description="External service tracking ID")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    retry_count: Optional[int] = Field(default=0, description="Current retry attempt")
    
    # Response data from external services (for debugging)
    response_data: Optional[Dict[str, Any]] = Field(None, description="Response from external service")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class LogQuery(BaseModel):
    """Query parameters for searching logs"""
    
    notification_id: Optional[int] = None
    recipient_id: Optional[int] = None
    channel: Optional[LogChannel] = None
    status: Optional[LogStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)

class LogStats(BaseModel):
    """Simple aggregated statistics"""
    
    total_logs: int
    success_count: int
    failure_count: int
    channel_breakdown: Dict[str, int]
    status_breakdown: Dict[str, int]
    time_period: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)