from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Boolean, Enum as SQLEnum, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
<<<<<<< HEAD
import uuid
from app.api.schemas.common import Priority, Channel, Status  # More specific import
=======
from app.api.schemas import Priority, Channel, Status as NotificationStatus
>>>>>>> a1ecdf7b4d1c4a83234c658db78c8214db5dc0f2
from .connection import Base

# Enums
# class Priority(str, Enum):
#     LOW = "low"
#     MEDIUM = "medium"
#     HIGH = "high"
#     CRITICAL = "critical"

# class Channel(str, Enum):
#     PUSH = "push"
#     EMAIL = "email"
#     SMS = "sms"
#     ALL = "all"

# class Status(str, Enum):
#     PENDING = "pending"
#     PROCESSING = "processing"
#     SENT = "sent"
#     FAILED = "failed"
#     CANCELLED = "cancelled"

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    sender_user_id = Column(Integer, nullable=True, index=True)  # Reference to external user service
    subject = Column(String(255), nullable=True)
    priority = Column(SQLEnum(Priority), nullable=False, index=True)
    channel = Column(SQLEnum(Channel), nullable=False)
    content = Column(Text, nullable=False)
    # template = Column(String(100), nullable=True)
<<<<<<< HEAD
    status = Column(SQLEnum(Status), default=Status.PENDING, index=True)
=======
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.PENDING, index=True)
>>>>>>> a1ecdf7b4d1c4a83234c658db78c8214db5dc0f2
    scheduled_at = Column(DateTime(timezone=True), nullable=True, index=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    recipients = relationship("NotificationRecipient", back_populates="notification", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_notification_status_priority', 'status', 'priority'),
        Index('idx_notification_scheduled_at', 'scheduled_at'),
        Index('idx_notification_sender', 'sender_user_id'),
    )

class NotificationRecipient(Base):
    __tablename__ = "notification_recipients"
    
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(String(36), ForeignKey("notifications.id"), nullable=False)
    
    # Store recipient info directly (from external user service or provided directly)
    user_id = Column(Integer, nullable=True, index=True)  # Reference to external user service
    email = Column(String(255), nullable=True, index=True)
    phone_number = Column(String(20), nullable=True, index=True)
    push_token = Column(String(500), nullable=True)
    
    status = Column(SQLEnum(Status), default=Status.PENDING, index=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    failed_reason = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    notification = relationship("Notification", back_populates="recipients")
    
    __table_args__ = (
        Index('idx_recipient_notification_status', 'notification_id', 'status'),
        Index('idx_recipient_user_id', 'user_id'),
    )

# class NotificationTemplate(Base):
#     __tablename__ = "notification_templates"
    
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(100), unique=True, nullable=False, index=True)
#     channel = Column(SQLEnum(Channel), nullable=False)
#     subject = Column(String(255), nullable=True)
#     content = Column(Text, nullable=False)
#     variables = Column(Text, nullable=True)  # JSON string of available variables
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
#     __table_args__ = (
#         Index('idx_template_name_channel', 'name', 'channel'),
#         Index('idx_template_active', 'is_active'),
#     )