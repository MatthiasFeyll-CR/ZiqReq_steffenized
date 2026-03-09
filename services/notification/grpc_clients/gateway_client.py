"""gRPC client for Gateway — create notifications + read user preferences.

Provides typed methods for GatewayService RPCs.
Full implementations will connect to the gRPC channel in later milestones.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class GatewayClient:
    """gRPC client for Gateway service (notification service side)."""

    def __init__(self, address: str = "localhost:50054") -> None:
        self.address = address

    def create_notification(
        self,
        user_id: str,
        event_type: str,
        title: str,
        body: str,
        reference_id: str = "",
        reference_type: str = "",
    ) -> dict[str, Any]:
        logger.warning("GatewayClient.create_notification stub called")
        return {"notification_id": ""}

    def get_user_preferences(self, user_id: str) -> dict[str, Any]:
        logger.warning("GatewayClient.get_user_preferences stub called")
        return {
            "user_id": "",
            "email": "",
            "display_name": "",
            "email_notification_preferences": {},
        }

    def get_alert_recipients(self) -> dict[str, Any]:
        logger.warning("GatewayClient.get_alert_recipients stub called")
        return {"recipients": []}
