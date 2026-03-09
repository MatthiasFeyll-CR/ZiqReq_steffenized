import logging
import uuid

import jwt
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

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
