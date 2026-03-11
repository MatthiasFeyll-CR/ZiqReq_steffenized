"""gRPC client for Gateway — create notifications + read user preferences."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

import grpc

# Ensure proto directory is on sys.path for generated imports
_proto_dir = str(Path(__file__).resolve().parents[3] / "proto")
if _proto_dir not in sys.path:
    sys.path.insert(0, _proto_dir)

import gateway_pb2  # noqa: E402
import gateway_pb2_grpc  # noqa: E402

logger = logging.getLogger(__name__)


class GatewayClient:
    """gRPC client for Gateway service (notification service side)."""

    def __init__(self, address: str = "localhost:50054") -> None:
        self.address = address
        self._channel: grpc.Channel | None = None
        self._stub: gateway_pb2_grpc.GatewayServiceStub | None = None

    def _ensure_channel(self) -> gateway_pb2_grpc.GatewayServiceStub:
        if self._stub is None:
            self._channel = grpc.insecure_channel(self.address)
            self._stub = gateway_pb2_grpc.GatewayServiceStub(self._channel)
        return self._stub

    def create_notification(
        self,
        user_id: str,
        event_type: str,
        title: str,
        body: str,
        reference_id: str = "",
        reference_type: str = "",
    ) -> dict[str, Any]:
        stub = self._ensure_channel()
        request = gateway_pb2.CreateNotificationRequest(
            user_id=user_id,
            event_type=event_type,
            title=title,
            body=body,
            reference_id=reference_id,
            reference_type=reference_type,
        )
        response = stub.CreateNotification(request)
        return {"notification_id": response.notification_id}

    def get_user_preferences(self, user_id: str) -> dict[str, Any]:
        stub = self._ensure_channel()
        request = gateway_pb2.UserPreferencesRequest(user_id=user_id)
        response = stub.GetUserPreferences(request)
        return {
            "user_id": response.user_id,
            "email": response.email,
            "display_name": response.display_name,
            "email_notification_preferences": dict(
                response.email_notification_preferences
            ),
        }

    def get_alert_recipients(self) -> dict[str, Any]:
        stub = self._ensure_channel()
        request = gateway_pb2.AlertRecipientsRequest()
        response = stub.GetAlertRecipients(request)
        return {
            "recipients": [
                {
                    "user_id": r.user_id,
                    "email": r.email,
                    "display_name": r.display_name,
                }
                for r in response.recipients
            ]
        }

    def get_idea_details(
        self,
        idea_id: str,
        ensure_share_link_token: bool = False,
    ) -> dict[str, Any]:
        stub = self._ensure_channel()
        request = gateway_pb2.IdeaDetailsRequest(
            idea_id=idea_id,
            ensure_share_link_token=ensure_share_link_token,
        )
        response = stub.GetIdeaDetails(request)
        return {
            "idea_id": response.idea_id,
            "title": response.title,
            "owner_id": response.owner_id,
            "share_link_token": response.share_link_token,
        }

    def close(self) -> None:
        if self._channel is not None:
            self._channel.close()
            self._channel = None
            self._stub = None
