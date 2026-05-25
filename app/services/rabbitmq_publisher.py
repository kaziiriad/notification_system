import pika
import json
import logging
from typing import Dict, Any, List
from app.core.config import settings

logger = logging.getLogger(__name__)


class RabbitMQPublisher:
    """Publishes messages directly to RabbitMQ queue."""

    def __init__(self):
        self._connection = None
        self._channel = None

    def _connect(self):
        if self._connection is None or self._connection.is_closed:
            params = pika.URLParameters(settings.CELERY_BROKER_URL)
            self._connection = pika.BlockingConnection(params)
            self._channel = self._connection.channel()
            self._channel.queue_declare(queue="notifications", durable=True)

    def publish(self, payload: Dict[str, Any]) -> None:
        """Publish notification payload to queue."""
        self._connect()
        message = json.dumps(payload, default=str)
        self._channel.basic_publish(
            exchange="",
            routing_key="notifications",
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # persistent
                content_type="application/json",
            ),
        )
        logger.info("Published notification to queue", extra={"notification_id": str(payload.get("id"))})

    def close(self):
        if self._connection and not self._connection.is_closed:
            self._connection.close()


publisher = RabbitMQPublisher()