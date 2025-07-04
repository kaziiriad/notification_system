from typing import List, Optional, Dict, Any

class NotificationException(Exception):
    """Base exception for notification-related errors"""
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code or "NOTIFICATION_ERROR"
        self.details = details or {}
        super().__init__(self.message)

class ValidationException(NotificationException):
    """Raised when notification request validation fails"""
    def __init__(self, errors: List[str]):
        self.validation_errors = errors
        message = f"Validation failed: {', '.join(errors)}"
        super().__init__(message, "VALIDATION_ERROR", {"errors": errors})

class RecipientResolutionException(NotificationException):
    """Raised when recipient resolution fails"""
    def __init__(self, message: str, channel: str = None):
        super().__init__(message, "RECIPIENT_RESOLUTION_ERROR", {"channel": channel})

class ChannelServiceException(NotificationException):
    """Raised when channel service operations fail"""
    def __init__(self, message: str, channel: str, retry_after: int = None):
        super().__init__(message)
        self.channel = channel
        self.retry_after = retry_after


class PartialFailureException(NotificationException):
    """Raised when some recipients succeed but others fail"""
    def __init__(self, successful_recipients: List[Dict], failed_recipients: List[Dict]):
        self.successful_recipients = successful_recipients
        self.failed_recipients = failed_recipients
        message = f"Partial failure: {len(successful_recipients)} succeeded, {len(failed_recipients)} failed"
        super().__init__(message, "PARTIAL_FAILURE", {
            "successful_count": len(successful_recipients),
            "failed_count": len(failed_recipients),
            "failed_recipients": failed_recipients
        })

class ExternalServiceException(NotificationException):
    """Raised when external service calls fail"""
    def __init__(self, service_name: str, message: str, status_code: int = None):
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", {
            "service_name": service_name,
            "status_code": status_code
        })

class DatabaseException(NotificationException):
    """
    Raised when database operations fail"""
    pass