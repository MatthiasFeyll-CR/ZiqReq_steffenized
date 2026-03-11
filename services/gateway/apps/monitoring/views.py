"""Monitoring dashboard views — US-003."""

import logging

from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response

from apps.ideas.authentication import MiddlewareAuthentication

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
@authentication_classes([MiddlewareAuthentication])
def monitoring_dashboard(request: Request) -> Response:
    """GET /api/admin/monitoring — aggregate monitoring dashboard stats."""
    denied = _require_admin(request)
    if denied:
        return denied

    stats = get_dashboard_stats()
    return Response(stats)
