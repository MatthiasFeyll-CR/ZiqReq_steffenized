"""Email sending logic via Azure Communication Services."""

from __future__ import annotations

import logging
import os
import time

from azure.communication.email import EmailClient

logger = logging.getLogger(__name__)

ACS_EMAIL_ENDPOINT = os.environ.get("ACS_EMAIL_ENDPOINT", "")
ACS_EMAIL_KEY = os.environ.get("ACS_EMAIL_ACCESS_KEY", "")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "noreply@ziqreq.com")

_POLL_WAIT = 2  # seconds between status polls
_POLL_TIMEOUT = 60  # max seconds to wait for send completion


def _get_client() -> EmailClient:
    connection_string = f"endpoint={ACS_EMAIL_ENDPOINT};accesskey={ACS_EMAIL_KEY}"
    return EmailClient.from_connection_string(connection_string)


def send_email(
    to_email: str,
    subject: str,
    text_body: str,
    html_body: str,
) -> bool:
    """Send an email via Azure Communication Services.

    Returns True on success, False on failure (logged, not raised).
    """
    if not ACS_EMAIL_ENDPOINT or not ACS_EMAIL_KEY:
        logger.error("ACS_EMAIL_ENDPOINT=%r ACS_EMAIL_ACCESS_KEY=%s", ACS_EMAIL_ENDPOINT, "set" if ACS_EMAIL_KEY else "empty")
        logger.error("ACS_EMAIL_ENDPOINT or ACS_EMAIL_KEY not configured")
        return False

    message = {
        "senderAddress": EMAIL_FROM,
        "recipients": {
            "to": [{"address": to_email}],
        },
        "content": {
            "subject": subject,
            "plainText": text_body,
            "html": html_body,
        },
    }

    try:
        client = _get_client()
        poller = client.begin_send(message)
        elapsed = 0
        while not poller.done():
            if elapsed >= _POLL_TIMEOUT:
                logger.error("Timed out waiting for email send to %s", to_email)
                return False
            time.sleep(_POLL_WAIT)
            elapsed += _POLL_WAIT

        result = poller.result()
        if result["status"] == "Succeeded":
            logger.info("Email sent to %s: %s", to_email, subject)
            return True

        logger.error(
            "Email send failed for %s: status=%s error=%s",
            to_email,
            result.get("status"),
            result.get("error"),
        )
        return False
    except Exception:
        logger.exception("Failed to send email to %s: %s", to_email, subject)
        return False
