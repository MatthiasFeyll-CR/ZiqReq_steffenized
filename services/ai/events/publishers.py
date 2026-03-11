"""Publish processing results to message broker.

Events are published as JSON to a RabbitMQ exchange. In test/mock mode,
events are stored in-memory for assertion.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

logger = logging.getLogger(__name__)

# In-memory store for tests — cleared between tests via fixture
_published_events: list[dict[str, Any]] = []


def get_published_events() -> list[dict[str, Any]]:
    """Return all events published during the current test run."""
    return list(_published_events)


def clear_published_events() -> None:
    """Clear the in-memory event store (call between tests)."""
    _published_events.clear()


async def publish_event(event_type: str, payload: dict[str, Any]) -> None:
    """Publish an event to the message broker.

    In the current milestone, events are stored in-memory.
    Future milestones will wire this to RabbitMQ via pika.

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
    logger.info("Published event %s: %s", event_type, event["event_id"])
