from enum import Enum


class Priority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Channel(str, Enum):
    """Notification delivery channels"""
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"
    ALL = "all"


class Status(str, Enum):
    """Notification status values"""
    PENDING = "pending"
    PROCESSING = "processing"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"