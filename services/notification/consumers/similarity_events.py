"""Similarity event consumer — handles similarity alerts and merge events."""

from __future__ import annotations

import logging
import os
from email.sender import send_email
from typing import Any

from grpc_clients.gateway_client import GatewayClient

from consumers.base import notify_user

logger = logging.getLogger(__name__)

BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:5173")

SIMILARITY_EVENT_TYPES = {
    "similarity_alert",
    "merge_request_received",
    "merge_accepted",
    "merge_declined",
    "idea_closed_append",
}


def handle_similarity_event(
    gateway_client: GatewayClient,
    event: dict[str, Any],
) -> None:
    """Process a similarity notification event."""
    user_id = event.get("user_id", "")
    event_type = event.get("event_type", "")
    title = event.get("title", "")
    body = event.get("body", "")
    reference_id = event.get("reference_id", "")
    reference_type = event.get("reference_type", "")

    if event_type not in SIMILARITY_EVENT_TYPES:
        logger.warning("Unknown similarity event type: %s", event_type)
        return

    if not user_id:
        logger.error("Similarity event missing user_id: %s", event)
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


def handle_ai_similarity_confirmed(
    gateway_client: GatewayClient,
    event: dict[str, Any],
) -> None:
    """Process an ai.similarity.confirmed event.

    Creates two in-app notifications (one per idea owner), sends emails
    to both (subject to 'similarity' email preference), and ensures
    share_link_tokens exist for read-only cross-access.
    """
    requesting_idea_id: str = event.get("requesting_idea_id", "")
    target_idea_id: str = event.get("target_idea_id", "")

    if not requesting_idea_id or not target_idea_id:
        logger.error(
            "ai.similarity.confirmed missing idea IDs: %s", event
        )
        return

    overlap_areas: list[str] = event.get("overlap_areas", [])

    # Fetch idea details + ensure share link tokens for both
    try:
        requesting_idea = gateway_client.get_idea_details(
            requesting_idea_id, ensure_share_link_token=True
        )
        target_idea = gateway_client.get_idea_details(
            target_idea_id, ensure_share_link_token=True
        )
    except Exception:
        logger.exception(
            "Failed to fetch idea details for similarity notification: %s <-> %s",
            requesting_idea_id,
            target_idea_id,
        )
        return

    requesting_owner_id = requesting_idea.get("owner_id", "")
    target_owner_id = target_idea.get("owner_id", "")
    requesting_title = requesting_idea.get("title", "Untitled")
    target_title = target_idea.get("title", "Untitled")

    if not requesting_owner_id or not target_owner_id:
        logger.error(
            "Missing owner IDs: requesting=%s target=%s",
            requesting_owner_id,
            target_owner_id,
        )
        return

    notification_title = "Similar idea detected"
    event_type = "similarity_alert"

    # Notify requesting idea owner (reference points to target idea)
    requesting_body = (
        f'Your idea "{requesting_title}" is similar to "{target_title}"'
    )
    notify_user(
        gateway_client=gateway_client,
        user_id=requesting_owner_id,
        event_type=event_type,
        title=notification_title,
        body=requesting_body,
        reference_id=target_idea_id,
        reference_type="idea",
    )

    # Notify target idea owner (reference points to requesting idea)
    target_body = (
        f'Your idea "{target_title}" is similar to "{requesting_title}"'
    )
    notify_user(
        gateway_client=gateway_client,
        user_id=target_owner_id,
        event_type=event_type,
        title=notification_title,
        body=target_body,
        reference_id=requesting_idea_id,
        reference_type="idea",
    )

    # Send detailed similarity emails to both owners
    _send_similarity_email(
        gateway_client=gateway_client,
        owner_id=requesting_owner_id,
        owner_idea_title=requesting_title,
        other_idea_title=target_title,
        owner_idea_id=requesting_idea_id,
        other_idea_id=target_idea_id,
        other_share_token=target_idea.get("share_link_token", ""),
        overlap_areas=overlap_areas,
    )
    _send_similarity_email(
        gateway_client=gateway_client,
        owner_id=target_owner_id,
        owner_idea_title=target_title,
        other_idea_title=requesting_title,
        owner_idea_id=target_idea_id,
        other_idea_id=requesting_idea_id,
        other_share_token=requesting_idea.get("share_link_token", ""),
        overlap_areas=overlap_areas,
    )

    logger.info(
        "Similarity notifications sent for %s <-> %s",
        requesting_idea_id,
        target_idea_id,
    )


def _send_similarity_email(
    *,
    gateway_client: GatewayClient,
    owner_id: str,
    owner_idea_title: str,
    other_idea_title: str,
    owner_idea_id: str,
    other_idea_id: str,
    other_share_token: str,
    overlap_areas: list[str],
) -> None:
    """Send a similarity-detected email to one idea owner."""
    try:
        prefs = gateway_client.get_user_preferences(owner_id)
    except Exception:
        logger.exception(
            "Failed to fetch preferences for user %s, skipping similarity email",
            owner_id,
        )
        return

    email_prefs = prefs.get("email_notification_preferences", {})
    user_email = prefs.get("email", "")
    display_name = prefs.get("display_name", "there")

    # Check 'similarity' preference group (default: enabled)
    if not email_prefs.get("similarity", True):
        logger.info("Email disabled for similarity group, user=%s", owner_id)
        return

    if not user_email:
        logger.warning("No email address for user %s, skipping email", owner_id)
        return

    owner_idea_link = f"{BASE_URL}/ideas/{owner_idea_id}"
    other_idea_link = f"{BASE_URL}/idea/{other_idea_id}?token={other_share_token}"

    overlap_summary = ""
    if overlap_areas:
        overlap_summary = "Overlapping areas: " + ", ".join(overlap_areas)

    subject = f"ZiqReq: Similar idea detected — {owner_idea_title}"

    text_body = (
        f"Hi {display_name},\n\n"
        f'Your idea "{owner_idea_title}" is similar to "{other_idea_title}".\n\n'
        f"{overlap_summary}\n\n" if overlap_summary else ""
        f"Your idea: {owner_idea_link}\n"
        f"Similar idea: {other_idea_link}\n\n"
        f"---\n"
        f"To manage your email notification preferences, "
        f"visit your account settings.\n"
    )

    html_body = (
        f"<html><body>"
        f"<p>Hi {display_name},</p>"
        f'<p>Your idea "<strong>{owner_idea_title}</strong>" is similar to '
        f'"<strong>{other_idea_title}</strong>".</p>'
        f"{f'<p>{overlap_summary}</p>' if overlap_summary else ''}"
        f'<p><a href="{owner_idea_link}">View your idea</a> | '
        f'<a href="{other_idea_link}">View similar idea</a></p>'
        f"<hr>"
        f'<p style="color:#888;font-size:12px">'
        f"To manage your email notification preferences, "
        f"visit your account settings."
        f"</p>"
        f"</body></html>"
    )

    send_email(
        to_email=user_email,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
    )
