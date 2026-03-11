import logging
import uuid

import jwt
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response

from apps.ideas.authentication import MiddlewareAuthentication

from .azure_ad import extract_user_data, validate_azure_ad_token
from .models import User
from .serializers import UserSerializer

logger = logging.getLogger(__name__)


def _is_dev_bypass_enabled() -> bool:
    return bool(getattr(settings, "DEBUG", False) and getattr(settings, "AUTH_BYPASS", False))


@api_view(["POST"])
def validate_token(request: Request) -> Response:
    """POST /api/auth/validate — Validate Azure AD token and sync user."""
    auth_header = request.META.get("HTTP_AUTHORIZATION", "")
    if not auth_header.startswith("Bearer "):
        return Response(
            {"error": "TOKEN_INVALID", "message": "Token validation failed"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    token = auth_header[7:]  # strip "Bearer "

    try:
        claims = validate_azure_ad_token(token)
    except (jwt.InvalidTokenError, jwt.ExpiredSignatureError, Exception) as exc:
        logger.warning("Token validation failed: %s", exc)
        return Response(
            {"error": "TOKEN_INVALID", "message": "Token validation failed"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    user_data = extract_user_data(claims)

    user, _ = User.objects.update_or_create(
        id=user_data["id"],
        defaults={
            "email": user_data["email"],
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"],
            "display_name": user_data["display_name"],
            "roles": user_data["roles"],
            "last_login_at": timezone.now(),
        },
    )

    serializer = UserSerializer(user)
    return Response(serializer.data)


@api_view(["GET"])
def dev_users(request: Request) -> Response:
    """GET /api/auth/dev-users — List dev users (bypass mode only)."""
    if not _is_dev_bypass_enabled():
        return Response(status=status.HTTP_404_NOT_FOUND)

    users = User.objects.all().order_by("email")
    serializer = UserSerializer(users, many=True)
    return Response({"users": serializer.data})


@api_view(["POST"])
def dev_login(request: Request) -> Response:
    """POST /api/auth/dev-login — Login as dev user (bypass mode only)."""
    if not _is_dev_bypass_enabled():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user_id = request.data.get("user_id")
    if not user_id:
        return Response(
            {"error": "MISSING_USER_ID", "message": "user_id is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user_uuid = uuid.UUID(str(user_id))
        user = User.objects.get(id=user_uuid)
    except (ValueError, User.DoesNotExist):
        return Response(
            {"error": "USER_NOT_FOUND", "message": "User not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    request.session["user_id"] = str(user.id)

    user.last_login_at = timezone.now()
    user.save(update_fields=["last_login_at", "updated_at"])

    serializer = UserSerializer(user)
    return Response(serializer.data)


@api_view(["POST"])
def dev_switch(request: Request) -> Response:
    """POST /api/auth/dev-switch — Switch dev user (bypass mode only)."""
    if not _is_dev_bypass_enabled():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user_id = request.data.get("user_id")
    if not user_id:
        return Response(
            {"error": "MISSING_USER_ID", "message": "user_id is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user_uuid = uuid.UUID(str(user_id))
        user = User.objects.get(id=user_uuid)
    except (ValueError, User.DoesNotExist):
        return Response(
            {"error": "USER_NOT_FOUND", "message": "User not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    request.session["user_id"] = str(user.id)

    serializer = UserSerializer(user)
    return Response(serializer.data)


# Notification preference categories and their event types
NOTIFICATION_PREFERENCE_CATEGORIES: dict[str, dict[str, list[str]]] = {
    "Collaboration": {
        "roles": [],  # all users
        "types": [
            "collaboration_invitation",
            "collaborator_joined",
            "collaborator_left",
            "removed_from_idea",
            "ownership_transferred",
        ],
    },
    "Review": {
        "roles": [],
        "types": [
            "review_state_changed",
            "review_comment",
        ],
    },
    "Chat": {
        "roles": [],
        "types": [
            "chat_mention",
        ],
    },
    "Similarity": {
        "roles": [],
        "types": [
            "similarity_alert",
            "merge_request_received",
            "merge_accepted",
            "merge_declined",
            "idea_closed_append",
        ],
    },
    "Review Management": {
        "roles": ["reviewer"],
        "types": [
            "idea_submitted",
            "idea_assigned",
            "idea_resubmitted",
            "append_request_received",
        ],
    },
    "Admin": {
        "roles": ["admin"],
        "types": [
            "monitoring_alert",
        ],
    },
}


def _build_preferences_response(user) -> dict:
    """Build categorized preferences response from user's stored prefs."""
    stored = user.email_notification_preferences or {}
    user_roles = getattr(user, "roles", []) or []
    categories = {}
    for cat_name, cat_info in NOTIFICATION_PREFERENCE_CATEGORIES.items():
        required_roles = cat_info["roles"]
        if required_roles and not any(r in user_roles for r in required_roles):
            continue
        prefs = {}
        for pref_type in cat_info["types"]:
            # Missing key defaults to True (enabled)
            prefs[pref_type] = stored.get(pref_type, True)
        categories[cat_name] = {"label": cat_name, "preferences": prefs}
    return {"categories": categories}


@api_view(["GET", "PATCH"])
@authentication_classes([MiddlewareAuthentication])
def notification_preferences(request: Request) -> Response:
    """GET/PATCH /api/users/me/notification-preferences."""
    user = getattr(request, "user", None)
    if user is None or not getattr(user, "id", None):
        return Response(
            {"error": "UNAUTHORIZED", "message": "Authentication required"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if request.method == "PATCH":
        prefs = user.email_notification_preferences or {}
        for key, value in request.data.items():
            if isinstance(value, bool):
                prefs[key] = value
        user.email_notification_preferences = prefs
        user.save(update_fields=["email_notification_preferences", "updated_at"])

    return Response(_build_preferences_response(user))


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def search_users(request: Request) -> Response:
    """GET /api/users/search?q=<query> — Search user directory."""
    user = getattr(request, "user", None)
    if user is None or not getattr(user, "id", None):
        return Response(
            {"error": "UNAUTHORIZED", "message": "Authentication required"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    query = request.query_params.get("q", "").strip()
    if len(query) < 2:
        return Response(
            {"error": "BAD_REQUEST", "message": "Query must be at least 2 characters"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    users = (
        User.objects.filter(
            Q(display_name__icontains=query) | Q(email__icontains=query)
        )
        .exclude(id=user.id)
        .order_by("display_name")[:20]
    )

    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)
