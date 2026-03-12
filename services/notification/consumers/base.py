"""Shared notify_user helper with email preference checking."""

from __future__ import annotations

import logging
from mailer.renderer import render_email
from mailer.sender import send_email
from typing import Any

from grpc_clients.gateway_client import GatewayClient

logger = logging.getLogger(__name__)

# Event types that are OFF by default — users must explicitly opt in.
_DEFAULT_DISABLED_EVENT_TYPES = frozenset({
    "ai_delegation_complete",
})


def notify_user(
    gateway_client: GatewayClient,
    user_id: str,
    event_type: str,
    title: str,
    body: str,
    reference_id: str = "",
    reference_type: str = "",
) -> dict[str, Any]:
    """Create a persistent notification and optionally send an email.

    1. Calls gateway CreateNotification gRPC to persist the notification.
    2. Calls gateway GetUserPreferences gRPC to check email prefs.
    3. If email is enabled for this event_type (default: enabled), sends email.

    Returns the CreateNotification response dict.
    """
    # Step 1: Create persistent notification via gRPC
    result = gateway_client.create_notification(
        user_id=user_id,
        event_type=event_type,
        title=title,
        body=body,
        reference_id=reference_id,
        reference_type=reference_type,
    )
    logger.info(
        "Created notification %s for user %s (type=%s)",
        result.get("notification_id"),
        user_id,
        event_type,
    )

    # Step 2: Fetch user email preferences
    try:
        prefs = gateway_client.get_user_preferences(user_id)
    except Exception:
        logger.exception(
            "Failed to fetch preferences for user %s, defaulting to email enabled",
            user_id,
        )
        prefs = {
            "email": "",
            "display_name": "there",
            "email_notification_preferences": {},
        }

    email_prefs = prefs.get("email_notification_preferences", {})
    user_email = prefs.get("email", "")
    display_name = prefs.get("display_name", "there")

    # Step 3: Check if email is enabled for this event type
    # Default depends on event type: most default to True (opt-out),
    # but some noisy types default to False (opt-in).
    default_enabled = event_type not in _DEFAULT_DISABLED_EVENT_TYPES
    email_enabled = email_prefs.get(event_type, default_enabled)

    if email_enabled and user_email:
        rendered = render_email(
            event_type=event_type,
            title=title,
            body=body,
            reference_id=reference_id or None,
            reference_type=reference_type or None,
            recipient_name=display_name or "there",
        )
        send_email(
            to_email=user_email,
            subject=rendered["subject"],
            text_body=rendered["text_body"],
            html_body=rendered["html_body"],
        )
    elif not user_email:
        logger.warning("No email address for user %s, skipping email", user_id)
    else:
        logger.info(
            "Email disabled for event_type=%s user=%s", event_type, user_id
        )

    return result
