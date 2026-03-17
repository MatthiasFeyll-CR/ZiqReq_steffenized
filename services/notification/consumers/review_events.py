"""Review event consumer — handles submission, state change, and comment events."""

from __future__ import annotations

import logging
from typing import Any

from grpc_clients.gateway_client import GatewayClient

from consumers.base import notify_user

logger = logging.getLogger(__name__)

REVIEW_EVENT_TYPES = {
    "review_state_changed",
    "review_comment",
    "project_submitted",
    "project_assigned",
    "project_resubmitted",
    "append_request_received",
}


def handle_review_event(
    gateway_client: GatewayClient,
    event: dict[str, Any],
) -> None:
    """Process a review notification event."""
    user_id = event.get("user_id", "")
    event_type = event.get("event_type", "")
    title = event.get("title", "")
    body = event.get("body", "")
    reference_id = event.get("reference_id", "")
    reference_type = event.get("reference_type", "")

    if event_type not in REVIEW_EVENT_TYPES:
        logger.warning("Unknown review event type: %s", event_type)
        return

    if not user_id:
        logger.error("Review event missing user_id: %s", event)
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
