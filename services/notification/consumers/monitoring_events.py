"""Monitoring event consumer — handles system monitoring alerts."""

from __future__ import annotations

import logging
from typing import Any

from grpc_clients.gateway_client import GatewayClient

from consumers.base import notify_user

logger = logging.getLogger(__name__)

MONITORING_EVENT_TYPES = {
    "monitoring_alert",
}


def handle_monitoring_event(
    gateway_client: GatewayClient,
    event: dict[str, Any],
) -> None:
    """Process a monitoring notification event."""
    user_id = event.get("user_id", "")
    event_type = event.get("event_type", "")
    title = event.get("title", "")
    body = event.get("body", "")
    reference_id = event.get("reference_id", "")
    reference_type = event.get("reference_type", "")

    if event_type not in MONITORING_EVENT_TYPES:
        logger.warning("Unknown monitoring event type: %s", event_type)
        return

    if not user_id:
        logger.error("Monitoring event missing user_id: %s", event)
        return

    notify_user(
        gateway_client=gateway_client,
        user_id=user_id,
        event_type=event_type,
        title=title,
        body=body,
        reference_id=reference_id,
        reference_type=reference_type,
    )
