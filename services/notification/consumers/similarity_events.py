"""Similarity event consumer — handles similarity alerts and merge/append events."""

from __future__ import annotations

import logging
import os
from mailer.sender import send_email
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

# Routing-key-based event types from publish_event()
MERGE_APPEND_EVENT_TYPES = {
    "notification.similarity.merge_request_created",
    "notification.similarity.append_request_created",
    "notification.similarity.merge_request_accepted",
    "notification.similarity.append_accepted",
    "notification.similarity.merge_request_declined",
    "notification.similarity.append_declined",
    "notification.similarity.merge_complete",
    "notification.similarity.append_complete",
}


def handle_similarity_event(
    gateway_client: GatewayClient,
    event: dict[str, Any],
) -> None:
    """Process a similarity notification event."""
    event_type = event.get("event_type", "")

    # Route merge/append events to dedicated handler
    if event_type in MERGE_APPEND_EVENT_TYPES:
        _handle_merge_append_event(gateway_client, event_type, event)
        return

    # Legacy pre-formatted notification events
    user_id = event.get("user_id", "")
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


def _handle_merge_append_event(
    gateway_client: GatewayClient,
    event_type: str,
    event: dict[str, Any],
) -> None:
    """Route merge/append events to appropriate handlers."""
    handler_map = {
        "notification.similarity.merge_request_created": _handle_merge_request_created,
        "notification.similarity.append_request_created": _handle_append_request_created,
        "notification.similarity.merge_request_accepted": _handle_merge_accepted,
        "notification.similarity.append_accepted": _handle_append_accepted,
        "notification.similarity.merge_request_declined": _handle_merge_declined,
        "notification.similarity.append_declined": _handle_append_declined,
        "notification.similarity.merge_complete": _handle_merge_complete,
        "notification.similarity.append_complete": _handle_append_complete,
    }

    handler = handler_map.get(event_type)
    if handler is None:
        logger.warning("No handler for merge/append event type: %s", event_type)
        return

    try:
        handler(gateway_client, event)
    except Exception:
        logger.exception("Error handling merge/append event %s: %s", event_type, event)


def _get_idea_title(gateway_client: GatewayClient, idea_id: str) -> str:
    """Fetch idea title via gRPC, returning 'Untitled' on failure."""
    try:
        details = gateway_client.get_idea_details(idea_id)
        return details.get("title", "Untitled") or "Untitled"
    except Exception:
        logger.exception("Failed to fetch idea title for %s", idea_id)
        return "Untitled"


def _handle_merge_request_created(
    gateway_client: GatewayClient,
    event: dict[str, Any],
) -> None:
    """merge_request.created → notify target owner."""
    target_owner_id = event.get("target_owner_id", "")
    requesting_idea_id = event.get("requesting_idea_id", "")
    target_idea_id = event.get("target_idea_id", "")

    if not target_owner_id:
        logger.error("merge_request_created missing target_owner_id: %s", event)
        return

    requesting_title = _get_idea_title(gateway_client, requesting_idea_id)
    target_title = _get_idea_title(gateway_client, target_idea_id)

    notify_user(
        gateway_client=gateway_client,
        user_id=target_owner_id,
        event_type="merge_request_received",
        title="Merge request received",
        body=f'A merge has been requested between your idea "{target_title}" and "{requesting_title}".',
        reference_id=target_idea_id,
        reference_type="idea",
    )


def _handle_append_request_created(
    gateway_client: GatewayClient,
    event: dict[str, Any],
) -> None:
    """append_request.created → notify target owner + reviewer(s)."""
    target_owner_id = event.get("target_owner_id", "")
    requesting_idea_id = event.get("requesting_idea_id", "")
    target_idea_id = event.get("target_idea_id", "")
    reviewer_ids: list[str] = event.get("reviewer_ids", [])

    if not target_owner_id:
        logger.error("append_request_created missing target_owner_id: %s", event)
        return

    requesting_title = _get_idea_title(gateway_client, requesting_idea_id)
    target_title = _get_idea_title(gateway_client, target_idea_id)

    # Notify target owner
    notify_user(
        gateway_client=gateway_client,
        user_id=target_owner_id,
        event_type="merge_request_received",
        title="Append request received",
        body=f'An append has been requested to your idea "{target_title}" from "{requesting_title}".',
        reference_id=target_idea_id,
        reference_type="idea",
    )

    # Notify each reviewer
    for reviewer_id in reviewer_ids:
        notify_user(
            gateway_client=gateway_client,
            user_id=reviewer_id,
            event_type="merge_request_received",
            title="Append request — reviewer approval needed",
            body=f'An append request to "{target_title}" from "{requesting_title}" requires your review.',
            reference_id=target_idea_id,
            reference_type="idea",
        )


def _handle_merge_accepted(
    gateway_client: GatewayClient,
    event: dict[str, Any],
) -> None:
    """merge.accepted → notify requesting owner."""
    requesting_idea_id = event.get("requesting_idea_id", "")
    target_idea_id = event.get("target_idea_id", "")

    # Look up requesting idea to find owner
    try:
        requesting_idea = gateway_client.get_idea_details(requesting_idea_id)
    except Exception:
        logger.exception("Failed to fetch requesting idea %s for merge_accepted", requesting_idea_id)
        return

    requesting_owner_id = requesting_idea.get("owner_id", "")
    if not requesting_owner_id:
        logger.error("merge_accepted: no owner_id for requesting idea %s", requesting_idea_id)
        return

    requesting_title = requesting_idea.get("title", "Untitled")
    target_title = _get_idea_title(gateway_client, target_idea_id)

    notify_user(
        gateway_client=gateway_client,
        user_id=requesting_owner_id,
        event_type="merge_accepted",
        title="Merge request accepted",
        body=f'Your merge request between "{requesting_title}" and "{target_title}" has been accepted.',
        reference_id=requesting_idea_id,
        reference_type="idea",
    )


def _handle_append_accepted(
    gateway_client: GatewayClient,
    event: dict[str, Any],
) -> None:
    """append.accepted → notify requesting owner."""
    requesting_idea_id = event.get("requesting_idea_id", "")
    target_idea_id = event.get("target_idea_id", "")

    try:
        requesting_idea = gateway_client.get_idea_details(requesting_idea_id)
    except Exception:
        logger.exception("Failed to fetch requesting idea %s for append_accepted", requesting_idea_id)
        return

    requesting_owner_id = requesting_idea.get("owner_id", "")
    if not requesting_owner_id:
        logger.error("append_accepted: no owner_id for requesting idea %s", requesting_idea_id)
        return

    requesting_title = requesting_idea.get("title", "Untitled")
    target_title = _get_idea_title(gateway_client, target_idea_id)

    notify_user(
        gateway_client=gateway_client,
        user_id=requesting_owner_id,
        event_type="merge_accepted",
        title="Append request accepted",
        body=f'Your append request from "{requesting_title}" to "{target_title}" has been accepted.',
        reference_id=requesting_idea_id,
        reference_type="idea",
    )


def _handle_merge_declined(
    gateway_client: GatewayClient,
    event: dict[str, Any],
) -> None:
    """merge.declined → notify requesting owner."""
    requesting_idea_id = event.get("requesting_idea_id", "")
    target_idea_id = event.get("target_idea_id", "")

    try:
        requesting_idea = gateway_client.get_idea_details(requesting_idea_id)
    except Exception:
        logger.exception("Failed to fetch requesting idea %s for merge_declined", requesting_idea_id)
        return

    requesting_owner_id = requesting_idea.get("owner_id", "")
    if not requesting_owner_id:
        logger.error("merge_declined: no owner_id for requesting idea %s", requesting_idea_id)
        return

    requesting_title = requesting_idea.get("title", "Untitled")
    target_title = _get_idea_title(gateway_client, target_idea_id)

    notify_user(
        gateway_client=gateway_client,
        user_id=requesting_owner_id,
        event_type="merge_declined",
        title="Merge request declined",
        body=f'Your merge request between "{requesting_title}" and "{target_title}" has been declined.',
        reference_id=requesting_idea_id,
        reference_type="idea",
    )


def _handle_append_declined(
    gateway_client: GatewayClient,
    event: dict[str, Any],
) -> None:
    """append.declined → notify requesting owner."""
    requesting_idea_id = event.get("requesting_idea_id", "")
    target_idea_id = event.get("target_idea_id", "")

    try:
        requesting_idea = gateway_client.get_idea_details(requesting_idea_id)
    except Exception:
        logger.exception("Failed to fetch requesting idea %s for append_declined", requesting_idea_id)
        return

    requesting_owner_id = requesting_idea.get("owner_id", "")
    if not requesting_owner_id:
        logger.error("append_declined: no owner_id for requesting idea %s", requesting_idea_id)
        return

    requesting_title = requesting_idea.get("title", "Untitled")
    target_title = _get_idea_title(gateway_client, target_idea_id)

    notify_user(
        gateway_client=gateway_client,
        user_id=requesting_owner_id,
        event_type="merge_declined",
        title="Append request declined",
        body=f'Your append request from "{requesting_title}" to "{target_title}" has been declined.',
        reference_id=requesting_idea_id,
        reference_type="idea",
    )


def _handle_merge_complete(
    gateway_client: GatewayClient,
    event: dict[str, Any],
) -> None:
    """merge.complete → notify all collaborators + co-owners."""
    resulting_idea_id = event.get("resulting_idea_id", "")
    all_collaborators: list[str] = event.get("all_collaborators", [])
    owner_ids: list[str] = event.get("owner_ids", [])
    demoted_co_owners: list[str] = event.get("demoted_co_owners", [])

    resulting_title = _get_idea_title(gateway_client, resulting_idea_id)

    # Notify all owners, collaborators, and demoted co-owners
    all_recipients = set(owner_ids) | set(all_collaborators) | set(demoted_co_owners)

    for user_id in all_recipients:
        notify_user(
            gateway_client=gateway_client,
            user_id=user_id,
            event_type="merge_accepted",
            title="Merge complete",
            body=f'A merge has been completed. View the new idea: "{resulting_title}".',
            reference_id=resulting_idea_id,
            reference_type="idea",
        )


def _handle_append_complete(
    gateway_client: GatewayClient,
    event: dict[str, Any],
) -> None:
    """append.complete → notify all collaborators + co-owners."""
    target_idea_id = event.get("target_idea_id", "")
    requesting_owner_id = event.get("requesting_owner_id", "")
    target_owner_id = event.get("target_owner_id", "")
    target_collaborator_ids: list[str] = event.get("target_collaborator_ids", [])

    target_title = _get_idea_title(gateway_client, target_idea_id)

    # Notify all: target owner, requesting owner, all target collaborators
    all_recipients = {requesting_owner_id, target_owner_id} | set(target_collaborator_ids)

    for user_id in all_recipients:
        if not user_id:
            continue
        notify_user(
            gateway_client=gateway_client,
            user_id=user_id,
            event_type="merge_accepted",
            title="Append complete",
            body=f'An append has been completed on "{target_title}".',
            reference_id=target_idea_id,
            reference_type="idea",
        )


def _classify_match_behavior(
    requesting_state: str,
    target_state: str,
) -> str:
    """Determine match behavior based on both idea states.

    Returns one of:
        'merge'         — both open/rejected → full merge flow
        'informational' — at least one idea is in_review/accepted/dropped
    """
    MERGEABLE_STATES = {"open", "rejected"}

    if requesting_state in MERGEABLE_STATES and target_state in MERGEABLE_STATES:
        return "merge"

    # in_review, accepted, dropped → informational only
    # (append flow for in_review deferred to M14)
    return "informational"


def _informational_body_for_owner(
    owner_idea_title: str,
    other_idea_title: str,
    other_state: str,
) -> str:
    """Build an informational notification body based on the other idea's state."""
    if other_state == "in_review":
        return (
            f'Your idea "{owner_idea_title}" is similar to '
            f'"{other_idea_title}" which is currently in review. '
            f"An append request may be available once review is complete."
        )
    if other_state == "accepted":
        return (
            f'Your idea "{owner_idea_title}" is similar to '
            f'"{other_idea_title}" which was already accepted. '
            f"Is this a change request or a new application?"
        )
    if other_state == "dropped":
        return (
            f'Your idea "{owner_idea_title}" is similar to '
            f'"{other_idea_title}" which was permanently closed. '
            f"What's different about yours?"
        )
    # Fallback (shouldn't happen for informational path)
    return (
        f'Your idea "{owner_idea_title}" is similar to "{other_idea_title}"'
    )


def handle_ai_similarity_confirmed(
    gateway_client: GatewayClient,
    event: dict[str, Any],
) -> None:
    """Process an ai.similarity.confirmed event.

    Creates state-aware notifications for both idea owners:
    - open/rejected + open/rejected → full merge flow notifications
    - in_review/accepted/dropped → informational notifications only

    Also sends emails to both (subject to 'similarity' email preference),
    and ensures share_link_tokens exist for read-only cross-access.
    """
    requesting_idea_id: str = event.get("requesting_idea_id", "")
    target_idea_id: str = event.get("target_idea_id", "")

    if not requesting_idea_id or not target_idea_id:
        logger.error(
            "ai.similarity.confirmed missing idea IDs: %s", event
        )
        return

    overlap_areas: list[str] = event.get("overlap_areas", [])
    requesting_idea_state: str = event.get("requesting_idea_state", "open")
    target_idea_state: str = event.get("target_idea_state", "open")

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

    match_behavior = _classify_match_behavior(
        requesting_idea_state, target_idea_state
    )

    if match_behavior == "merge":
        notification_title = "Similar idea detected"
        event_type = "similarity_alert"

        requesting_body = (
            f'Your idea "{requesting_title}" is similar to "{target_title}"'
        )
        target_body = (
            f'Your idea "{target_title}" is similar to "{requesting_title}"'
        )
    else:
        notification_title = "Similar idea detected"
        event_type = "similarity_alert"

        requesting_body = _informational_body_for_owner(
            requesting_title, target_title, target_idea_state
        )
        target_body = _informational_body_for_owner(
            target_title, requesting_title, requesting_idea_state
        )

    # Notify requesting idea owner (reference points to target idea)
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
        "Similarity notifications sent for %s <-> %s (behavior=%s, states=%s/%s)",
        requesting_idea_id,
        target_idea_id,
        match_behavior,
        requesting_idea_state,
        target_idea_state,
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

    owner_idea_link = f"{BASE_URL}/idea/{owner_idea_id}"
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
