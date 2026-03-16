import logging
import secrets
import sys
import uuid
from pathlib import Path

import grpc

logger = logging.getLogger(__name__)

# Ensure proto directory is on sys.path for generated imports
def _find_proto_dir() -> str:
    """Search upward from this file for a 'proto' directory."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        candidate = current / "proto"
        if candidate.is_dir():
            return str(candidate)
        current = current.parent
    return ""

_proto_dir = _find_proto_dir()
if _proto_dir and _proto_dir not in sys.path:
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

        # Broadcast WebSocket notification to the related idea group
        if ref_id and request.reference_type == "idea":
            try:
                from asgiref.sync import async_to_sync
                from channels.layers import get_channel_layer

                channel_layer = get_channel_layer()
                if channel_layer:
                    async_to_sync(channel_layer.group_send)(
                        f"idea_{ref_id}",
                        {
                            "type": "notification",
                            "payload": {
                                "event_type": request.event_type,
                                "title": request.title,
                                "body": request.body,
                                "reference_id": str(ref_id),
                                "reference_type": request.reference_type,
                            },
                        },
                    )
            except Exception:
                logger.exception(
                    "Failed to broadcast WS notification for %s", notification.id
                )

        return gateway_pb2.CreateNotificationResponse(
            notification_id=str(notification.id),
        )

    def GetUserPreferences(
        self,
        request: gateway_pb2.UserPreferencesRequest,
        context: grpc.ServicerContext,
    ) -> gateway_pb2.UserPreferencesResponse:
        from apps.authentication.models import User

        try:
            user = User.objects.get(id=uuid.UUID(request.user_id))
        except (ValueError, User.DoesNotExist):
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("User not found")
            return gateway_pb2.UserPreferencesResponse()

        stored_prefs = user.email_notification_preferences or {}
        # Convert to map<string, bool> — only include explicitly set preferences
        prefs_map = {
            k: bool(v) for k, v in stored_prefs.items() if isinstance(v, bool)
        }

        return gateway_pb2.UserPreferencesResponse(
            user_id=str(user.id),
            email=user.email,
            display_name=user.display_name,
            email_notification_preferences=prefs_map,
        )

    def GetAlertRecipients(
        self,
        request: gateway_pb2.AlertRecipientsRequest,
        context: grpc.ServicerContext,
    ) -> gateway_pb2.AlertRecipientsResponse:
        from apps.authentication.models import User
        from apps.monitoring.models import MonitoringAlertConfig

        opted_in_configs = MonitoringAlertConfig.objects.filter(is_active=True)
        opted_in_user_ids = [c.user_id for c in opted_in_configs]

        if not opted_in_user_ids:
            return gateway_pb2.AlertRecipientsResponse(recipients=[])

        users = User.objects.filter(id__in=opted_in_user_ids)
        recipients = [
            gateway_pb2.AlertRecipient(
                user_id=str(u.id),
                email=u.email,
                display_name=u.display_name,
            )
            for u in users
        ]
        return gateway_pb2.AlertRecipientsResponse(recipients=recipients)

    def GetIdeaDetails(
        self,
        request: gateway_pb2.IdeaDetailsRequest,
        context: grpc.ServicerContext,
    ) -> gateway_pb2.IdeaDetailsResponse:
        from apps.ideas.models import Idea

        try:
            idea = Idea.objects.get(id=uuid.UUID(request.idea_id))
        except (ValueError, Idea.DoesNotExist):
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Idea not found")
            return gateway_pb2.IdeaDetailsResponse()

        if request.ensure_share_link_token and not idea.share_link_token:
            idea.share_link_token = secrets.token_hex(32)
            idea.save(update_fields=["share_link_token"])

        return gateway_pb2.IdeaDetailsResponse(
            idea_id=str(idea.id),
            title=idea.title,
            owner_id=str(idea.owner_id),
            share_link_token=idea.share_link_token or "",
        )
