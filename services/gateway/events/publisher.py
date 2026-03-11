"""RabbitMQ event publisher for notification events.

Publishes events to the ``ziqreq.events`` topic exchange so that the
notification service can consume them and create persistent notifications
+ dispatch emails.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone

import pika

logger = logging.getLogger(__name__)

BROKER_URL = os.environ.get("BROKER_URL", "amqp://guest:guest@localhost:5672/")
EXCHANGE_NAME = "ziqreq.events"


def _get_connection() -> pika.BlockingConnection:
    params = pika.URLParameters(BROKER_URL)
    return pika.BlockingConnection(params)


def publish_notification_event(
    *,
    routing_key: str,
    user_id: str,
    event_type: str,
    title: str,
    body: str,
    reference_id: str = "",
    reference_type: str = "",
) -> None:
    """Publish a notification event to RabbitMQ.

    Parameters
    ----------
    routing_key:
        Topic routing key, e.g. ``notification.collaboration.invitation``.
    user_id:
        UUID of the notification recipient.
    event_type:
        Notification event type, e.g. ``collaboration_invitation``.
    title:
        Human-readable notification title.
    body:
        Human-readable notification body.
    reference_id:
        Optional UUID of the related entity.
    reference_type:
        Optional type of the related entity (``idea``, ``invitation``, etc.).
    """
    payload = {
        "user_id": str(user_id),
        "event_type": event_type,
        "title": title,
        "body": body,
        "reference_id": str(reference_id) if reference_id else "",
        "reference_type": reference_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    try:
        connection = _get_connection()
        channel = connection.channel()
        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type="topic",
            durable=True,
        )
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=routing_key,
            body=json.dumps(payload),
            properties=pika.BasicProperties(
                delivery_mode=2,  # persistent
                content_type="application/json",
            ),
        )
        connection.close()
        logger.info(
            "Published notification event %s for user %s (routing_key=%s)",
            event_type,
            user_id,
            routing_key,
        )
    except Exception:
        logger.exception(
            "Failed to publish notification event %s for user %s",
            event_type,
            user_id,
        )


def publish_event(event_type: str, payload: dict) -> None:
    """Publish a generic event to RabbitMQ.

    Parameters
    ----------
    event_type:
        Event type used as the routing key, e.g. ``similarity.detected``.
    payload:
        Arbitrary JSON-serializable dict.
    """
    message = {
        **payload,
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    try:
        connection = _get_connection()
        channel = connection.channel()
        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type="topic",
            durable=True,
        )
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=event_type,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json",
            ),
        )
        connection.close()
        logger.info("Published event %s", event_type)
    except Exception:
        logger.exception("Failed to publish event %s", event_type)
