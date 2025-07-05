import asyncio
from celery import Celery
from app.core.config import settings
from app.db.sql.connection import SessionLocal

# Create a Celery instance
celery_app = Celery(
    "tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.worker.tasks"]
)

@celery_app.task(bind=True)
def send_notification_task(self, notification_id: str):
    """
    Celery task to send a notification.
    This task is a thin wrapper around the NotificationService's process_notification method.
    """
    from app.services.notification_service import NotificationService
    db = SessionLocal()
    try:
        notification_service = NotificationService(db)
        asyncio.run(notification_service.process_notification(notification_id))
    except Exception as e:
        raise self.retry(exc=e)
    finally:
        db.close()