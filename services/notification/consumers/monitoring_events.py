"""Monitoring event consumer — handles system monitoring alerts (US-007)."""

from __future__ import annotations

import logging
from typing import Any

from grpc_clients.gateway_client import GatewayClient
from mailer.sender import send_email

from consumers.base import notify_user

logger = logging.getLogger(__name__)

MONITORING_EVENT_TYPES = {
    "monitoring_alert",
}


def handle_monitoring_event(
    gateway_client: GatewayClient,
    event: dict[str, Any],
) -> None:
    """Process a monitoring notification event (per-user notification)."""
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


def handle_monitoring_alert(
    gateway_client: GatewayClient,
    event: dict[str, Any],
) -> None:
    """Process a monitoring.alert event — send email to opted-in admins."""
    alert_type = event.get("alert_type", "unknown")
    service_name = event.get("service_name", "unknown")
    details = event.get("details", "")
    timestamp = event.get("timestamp", "")

    logger.info(
        "Processing monitoring alert: %s - %s (%s)",
        alert_type,
        service_name,
        details,
    )

    try:
        recipients_data = gateway_client.get_alert_recipients()
        recipients = recipients_data.get("recipients", [])
    except Exception:
        logger.exception("Failed to fetch alert recipients from gateway")
        return

    if not recipients:
        logger.info("No opted-in admin recipients for monitoring alert")
        return

    subject = f"[ZiqReq Alert] {service_name} - {alert_type}"
    text_body = (
        f"Monitoring Alert\n"
        f"================\n\n"
        f"Service: {service_name}\n"
        f"Alert Type: {alert_type}\n"
        f"Details: {details}\n"
        f"Timestamp: {timestamp}\n\n"
        f"Please check the admin monitoring dashboard for more information."
    )
    html_body = (
        f"<html><body>"
        f"<h2>Monitoring Alert</h2>"
        f"<table>"
        f"<tr><td><strong>Service:</strong></td><td>{service_name}</td></tr>"
        f"<tr><td><strong>Alert Type:</strong></td><td>{alert_type}</td></tr>"
        f"<tr><td><strong>Details:</strong></td><td>{details}</td></tr>"
        f"<tr><td><strong>Timestamp:</strong></td><td>{timestamp}</td></tr>"
        f"</table>"
        f"<p>Please check the admin monitoring dashboard for more information.</p>"
        f"</body></html>"
    )

    for recipient in recipients:
        email = recipient.get("email", "")
        display_name = recipient.get("display_name", "Admin")
        if not email:
            logger.warning(
                "Alert recipient %s has no email, skipping",
                recipient.get("user_id"),
            )
            continue

        personalized_text = f"Hi {display_name},\n\n{text_body}"
        personalized_html = (
            f"<html><body>"
            f"<p>Hi {display_name},</p>"
            f"{html_body[len('<html><body>'):]}"
        )

        success = send_email(
            to_email=email,
            subject=subject,
            text_body=personalized_text,
            html_body=personalized_html,
        )
        if success:
            logger.info("Alert email sent to %s (%s)", display_name, email)
        else:
            logger.error("Failed to send alert email to %s (%s)", display_name, email)
