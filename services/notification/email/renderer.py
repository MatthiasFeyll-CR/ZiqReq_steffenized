"""Simple string-based email rendering for notification emails.

Supports i18n: pass ``language='de'`` or ``language='en'`` (default ``'de'``)
to render the email chrome (greeting, footer) in the chosen language.  The
``title`` and ``body`` are passed through as-is since they are composed by
the event consumers which already have context.
"""

from __future__ import annotations

import os
from typing import Any

BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:5173")

_REFERENCE_URLS: dict[str, str] = {
    "idea": "/ideas/{reference_id}",
    "invitation": "/ideas/{reference_id}",
    "merge_request": "/ideas/{reference_id}",
}

# Bilingual email chrome strings
_EMAIL_STRINGS: dict[str, dict[str, str]] = {
    "de": {
        "greeting": "Hallo {name},",
        "view_details": "Details anzeigen",
        "manage_preferences": (
            "Um Ihre E-Mail-Benachrichtigungseinstellungen zu verwalten, "
            "besuchen Sie Ihre Kontoeinstellungen."
        ),
    },
    "en": {
        "greeting": "Hi {name},",
        "view_details": "View details",
        "manage_preferences": (
            "To manage your email notification preferences, "
            "visit your account settings."
        ),
    },
}


def _get_strings(language: str) -> dict[str, str]:
    return _EMAIL_STRINGS.get(language, _EMAIL_STRINGS["de"])


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
    language: str = "de",
    **_kwargs: Any,
) -> dict[str, str]:
    """Render a notification email as plain text + HTML.

    Returns dict with 'subject', 'text_body', and 'html_body' keys.
    """
    link = _build_link(reference_id, reference_type)
    s = _get_strings(language)

    subject = f"ZiqReq: {title}"

    greeting = s["greeting"].format(name=recipient_name)
    view_details = s["view_details"]
    manage_prefs = s["manage_preferences"]

    text_body = (
        f"{greeting}\n\n"
        f"{body}\n\n"
        f"{view_details}: {link}\n\n"
        f"---\n"
        f"{manage_prefs}\n"
        f"Event type: {event_type}\n"
    )

    html_body = (
        f"<html><body>"
        f"<p>{greeting}</p>"
        f"<p>{body}</p>"
        f'<p><a href="{link}">{view_details}</a></p>'
        f"<hr>"
        f'<p style="color:#888;font-size:12px">'
        f"{manage_prefs}"
        f"</p>"
        f"</body></html>"
    )

    return {
        "subject": subject,
        "text_body": text_body,
        "html_body": html_body,
    }
