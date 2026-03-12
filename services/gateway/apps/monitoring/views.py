"""Monitoring dashboard views — US-003, US-007."""

import logging

from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response

from apps.ideas.authentication import MiddlewareAuthentication

from .models import MonitoringAlertConfig
from .serializers import MonitoringAlertConfigSerializer, MonitoringAlertConfigUpdateSerializer
from .services import get_dashboard_stats

logger = logging.getLogger(__name__)


def _require_admin(request: Request) -> Response | None:
    """Return a 403 Response if the user is not an admin, else None."""
    user = getattr(request, "user", None)
    if user is None or not getattr(user, "id", None):
        return Response(
            {"error": "UNAUTHORIZED", "message": "Authentication required"},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    roles = getattr(user, "roles", []) or []
    if "admin" not in roles:
        return Response(
            {"error": "FORBIDDEN", "message": "Admin role required"},
            status=status.HTTP_403_FORBIDDEN,
        )
    return None


@api_view(["GET"])
def health_check(request: Request) -> Response:
    """GET /api/health/ — lightweight health probe for monitoring."""
    return Response({"status": "ok"})


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def monitoring_dashboard(request: Request) -> Response:
    """GET /api/admin/monitoring — aggregate monitoring dashboard stats."""
    denied = _require_admin(request)
    if denied:
        return denied

    stats = get_dashboard_stats()
    return Response(stats)


@api_view(["GET", "PATCH"])
@authentication_classes([MiddlewareAuthentication])
def alert_config(request: Request) -> Response:
    """GET/PATCH /api/admin/monitoring/alerts — admin alert opt-in config."""
    denied = _require_admin(request)
    if denied:
        return denied

    user_id = request.user.id

    if request.method == "GET":
        config, _created = MonitoringAlertConfig.objects.get_or_create(
            user_id=user_id,
            defaults={"is_active": False},
        )
        serializer = MonitoringAlertConfigSerializer(config)
        return Response(serializer.data)

    # PATCH
    update_serializer = MonitoringAlertConfigUpdateSerializer(data=request.data)
    if not update_serializer.is_valid():
        return Response(
            {"error": "VALIDATION_ERROR", "message": update_serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    config, _created = MonitoringAlertConfig.objects.get_or_create(
        user_id=user_id,
        defaults={"is_active": False},
    )
    config.is_active = update_serializer.validated_data["is_active"]
    config.save()

    serializer = MonitoringAlertConfigSerializer(config)
    return Response(serializer.data)
