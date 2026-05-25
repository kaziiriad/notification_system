import pika
import json
import asyncio
import logging
from typing import Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)


class NotificationConsumer:
    """Consumes messages directly from RabbitMQ and sends via channel services."""

    MAX_RETRIES = 3
    RETRY_DELAYS = [1, 2, 4]  # seconds

    def __init__(self, process_callback):
        self._connection = None
        self._channel = None
        self._process = process_callback

    def _connect(self):
        if self._connection is None or self._connection.is_closed:
            params = pika.URLParameters(settings.CELERY_BROKER_URL)
            self._connection = pika.BlockingConnection(params)
            self._channel = self._connection.channel()
            self._channel.queue_declare(queue="notifications", durable=True)
            self._channel.basic_qos(prefetch_count=1)

    def _process_message(self, ch, method, properties, body):
        """Synchronous message handler with retry logic."""
        payload = json.loads(body)
        notification_id = payload.get("id")

        logger.info("Received notification", extra={
            "notification_id": str(notification_id),
            "channel": str(payload.get("channel"))
        })

        # Retry loop
        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                # Check if already processed — skip if SENT
                from app.db.sql.connection import SessionLocal
                db = SessionLocal()
                try:
                    from app.db.sql.repositories import NotificationRepository
                    repo = NotificationRepository(db)
                    notification = repo.get_notification_by_id(notification_id)
                    if notification and notification.status.value == "SENT":
                        logger.info("Notification already sent, skipping", extra={
                            "notification_id": str(notification_id)
                        })
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        return
                finally:
                    db.close()

                asyncio.run(self._process(payload))
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info("Notification processed successfully", extra={
                    "notification_id": str(notification_id),
                    "attempt": attempt + 1
                })
                return
            except Exception as e:
                last_error = e
                logger.warning("Send attempt failed", extra={
                    "notification_id": str(notification_id),
                    "attempt": attempt + 1,
                    "error": str(e)
                })
                if attempt < self.MAX_RETRIES - 1:
                    import time
                    time.sleep(self.RETRY_DELAYS[attempt])

        # All retries exhausted
        logger.error("All retry attempts failed", extra={
            "notification_id": str(notification_id),
            "error": str(last_error)
        })
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def start(self):
        """Start consuming messages."""
        self._connect()
        logger.info("Starting notification consumer")
        self._channel.basic_consume(
            queue="notifications",
            on_message_callback=self._process_message,
            auto_ack=False,
        )
        self._channel.start_consuming()

    def stop(self):
        """Stop consuming messages."""
        if self._channel:
            self._channel.stop_consuming()
        if self._connection and not self._connection.is_closed:
            self._connection.close()
        logger.info("Consumer stopped")


def main():
    """Standalone entry point for running the consumer."""
    from app.core.logging_config import configure_logging
    from app.db.sql.connection import SessionLocal
    from app.services.notification_service import NotificationService
    from app.services.channel_services import ChannelServiceFactory

    configure_logging()
    logger.info("Starting notification worker")

    def get_service():
        db = SessionLocal()
        return NotificationService(db)

    def handle_message(payload: Dict[str, Any]):
        service = get_service()
        try:
            asyncio.run(service.process_notification(payload))
        finally:
            db = SessionLocal()
            db.close()

    consumer = NotificationConsumer(handle_message)
    try:
        consumer.start()
    except KeyboardInterrupt:
        consumer.stop()


if __name__ == "__main__":
    main()