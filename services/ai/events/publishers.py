"""Publish processing results to message broker (RabbitMQ).

Events are published as JSON to the ziqreq.events topic exchange.
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from typing import Any

import pika

logger = logging.getLogger(__name__)

BROKER_URL = os.environ.get("BROKER_URL", "amqp://guest:guest@localhost:5672/")
EXCHANGE_NAME = "ziqreq.events"

# In-memory store for tests — cleared between tests via fixture
_published_events: list[dict[str, Any]] = []


def get_published_events() -> list[dict[str, Any]]:
    """Return all events published during the current test run."""
    return list(_published_events)


def clear_published_events() -> None:
    """Clear the in-memory event store (call between tests)."""
    _published_events.clear()


def _get_connection() -> pika.BlockingConnection:
    params = pika.URLParameters(BROKER_URL)
    return pika.BlockingConnection(params)


async def publish_event(event_type: str, payload: dict[str, Any]) -> None:
    """Publish an event to RabbitMQ.

    Args:
        event_type: Dotted event name (e.g. "ai.chat_response.ready").
        payload: Event payload dict. An event_id is added automatically.
    """
    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        **payload,
    }
    _published_events.append(event)

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
            body=json.dumps(event),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json",
            ),
        )
        connection.close()
        logger.info("Published event %s: %s", event_type, event["event_id"])
    except Exception:
        logger.exception("Failed to publish event %s to RabbitMQ", event_type)
