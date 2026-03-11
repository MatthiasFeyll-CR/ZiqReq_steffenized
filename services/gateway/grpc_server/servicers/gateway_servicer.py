import logging
import sys
import uuid
from pathlib import Path

import grpc

logger = logging.getLogger(__name__)

# Ensure proto directory is on sys.path for generated imports
_proto_dir = str(Path(__file__).resolve().parents[4] / "proto")
if _proto_dir not in sys.path:
    sys.path.insert(0, _proto_dir)

import gateway_pb2  # noqa: E402
import gateway_pb2_grpc  # noqa: E402


class GatewayServicer(gateway_pb2_grpc.GatewayServiceServicer):
    """gRPC servicer for the Gateway service."""

    def CreateNotification(
        self,
        request: gateway_pb2.CreateNotificationRequest,
        context: grpc.ServicerContext,
    ) -> gateway_pb2.CreateNotificationResponse:
        from apps.notifications.models import Notification

        try:
            ref_id = uuid.UUID(request.reference_id) if request.reference_id else None
        except ValueError:
            ref_id = None

        notification = Notification.objects.create(
            user_id=uuid.UUID(request.user_id),
            event_type=request.event_type,
            title=request.title,
            body=request.body,
            reference_id=ref_id,
            reference_type=request.reference_type or None,
        )

        return gateway_pb2.CreateNotificationResponse(
            notification_id=str(notification.id),
        )

    def GetUserPreferences(
        self,
        request: gateway_pb2.UserPreferencesRequest,
        context: grpc.ServicerContext,
    ) -> gateway_pb2.UserPreferencesResponse:
        return gateway_pb2.UserPreferencesResponse(
            user_id="",
            email="",
            display_name="",
            email_notification_preferences={},
        )

    def GetAlertRecipients(
        self,
        request: gateway_pb2.AlertRecipientsRequest,
        context: grpc.ServicerContext,
    ) -> gateway_pb2.AlertRecipientsResponse:
        return gateway_pb2.AlertRecipientsResponse(recipients=[])
