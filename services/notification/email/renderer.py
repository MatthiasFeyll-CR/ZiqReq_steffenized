"""Simple string-based email rendering for notification emails."""

from __future__ import annotations

import os
from typing import Any

BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:5173")

_REFERENCE_URLS: dict[str, str] = {
    "idea": "/ideas/{reference_id}",
    "invitation": "/ideas/{reference_id}",
    "merge_request": "/ideas/{reference_id}",
}


def _build_link(reference_id: str | None, reference_type: str | None) -> str:
    if not reference_id or not reference_type:
        return BASE_URL
    template = _REFERENCE_URLS.get(reference_type, "")
    if not template:
        return BASE_URL
    return BASE_URL + template.format(reference_id=reference_id)


def render_email(
    event_type: str,
    title: str,
    body: str,
    reference_id: str | None = None,
    reference_type: str | None = None,
    recipient_name: str = "there",
    **_kwargs: Any,
) -> dict[str, str]:
    """Render a notification email as plain text + HTML.

    Returns dict with 'subject', 'text_body', and 'html_body' keys.
    """
    link = _build_link(reference_id, reference_type)

    subject = f"ZiqReq: {title}"

    text_body = (
        f"Hi {recipient_name},\n\n"
        f"{body}\n\n"
        f"View details: {link}\n\n"
        f"---\n"
        f"To manage your email notification preferences, "
        f"visit your account settings.\n"
        f"Event type: {event_type}\n"
    )

    html_body = (
        f"<html><body>"
        f"<p>Hi {recipient_name},</p>"
        f"<p>{body}</p>"
        f'<p><a href="{link}">View details</a></p>'
        f"<hr>"
        f'<p style="color:#888;font-size:12px">'
        f"To manage your email notification preferences, "
        f"visit your account settings."
        f"</p>"
        f"</body></html>"
    )

    return {
        "subject": subject,
        "text_body": text_body,
        "html_body": html_body,
    }
