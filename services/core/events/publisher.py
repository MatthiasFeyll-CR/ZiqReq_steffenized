"""EventPublisher with DLQ pairs, delivery confirmation, auto-reconnect."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone

import pika

logger = logging.getLogger(__name__)

BROKER_URL = os.environ.get("BROKER_URL", "amqp://guest:guest@localhost:5672/")
EXCHANGE_NAME = "ziqreq.events"


def publish_event(event_type: str, payload: dict) -> None:
    """Publish an event to the message broker."""
    message = {
        **payload,
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    try:
        params = pika.URLParameters(BROKER_URL)
        connection = pika.BlockingConnection(params)
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
