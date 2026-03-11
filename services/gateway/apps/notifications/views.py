import uuid

from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response

from apps.ideas.authentication import MiddlewareAuthentication

from .models import Notification


def _require_auth(request: Request):
    user = request.user
    if user is None or not getattr(user, "id", None):
        return None
    return user


def _unauthorized_response() -> Response:
    return Response(
        {"error": "UNAUTHORIZED", "message": "Authentication required"},
        status=status.HTTP_401_UNAUTHORIZED,
    )


def _serialize_notification(notif: Notification) -> dict:
    return {
        "id": str(notif.id),
        "user_id": str(notif.user_id),
        "event_type": notif.event_type,
        "title": notif.title,
        "body": notif.body,
        "reference_id": str(notif.reference_id) if notif.reference_id else None,
        "reference_type": notif.reference_type,
        "is_read": notif.is_read,
        "action_taken": notif.action_taken,
        "created_at": notif.created_at.isoformat(),
    }


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def notification_list(request: Request) -> Response:
    """GET /api/notifications — paginated list with unread_count."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    unread_only = request.query_params.get("unread_only", "").lower() == "true"
    page = int(request.query_params.get("page", "1"))
    page_size = int(request.query_params.get("page_size", "20"))

    qs = Notification.objects.filter(user_id=user.id).order_by("-created_at")

    if unread_only:
        qs = qs.filter(is_read=False)

    count = qs.count()
    offset = (page - 1) * page_size
    notifications = list(qs[offset : offset + page_size])

    unread_count = Notification.objects.filter(
        user_id=user.id, is_read=False, action_taken=False
    ).count()

    return Response(
        {
            "notifications": [_serialize_notification(n) for n in notifications],
            "unread_count": unread_count,
            "count": count,
            "page": page,
            "page_size": page_size,
        }
    )


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def unread_count(request: Request) -> Response:
    """GET /api/notifications/unread-count — badge count."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    count = Notification.objects.filter(
        user_id=user.id, is_read=False, action_taken=False
    ).count()

    return Response({"unread_count": count})


@api_view(["PATCH"])
@authentication_classes([MiddlewareAuthentication])
def mark_notification(request: Request, notification_id: str) -> Response:
    """PATCH /api/notifications/:id — mark is_read or action_taken."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        notif_uuid = uuid.UUID(notification_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Notification not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        notif = Notification.objects.get(id=notif_uuid)
    except Notification.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Notification not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if notif.user_id != user.id:
        return Response(
            {"error": "NOT_FOUND", "message": "Notification not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    update_fields = []
    if "is_read" in request.data:
        notif.is_read = request.data["is_read"]
        update_fields.append("is_read")
    if "action_taken" in request.data:
        notif.action_taken = request.data["action_taken"]
        update_fields.append("action_taken")

    if update_fields:
        notif.save(update_fields=update_fields)

    return Response(_serialize_notification(notif))


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def mark_all_read(request: Request) -> Response:
    """POST /api/notifications/mark-all-read — bulk update."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    Notification.objects.filter(user_id=user.id, is_read=False).update(is_read=True)

    return Response({"message": "All notifications marked as read"})
