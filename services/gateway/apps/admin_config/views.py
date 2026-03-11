import logging

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response

from apps.ideas.authentication import MiddlewareAuthentication

from .models import AdminParameter
from .serializers import AdminParameterSerializer, AdminParameterUpdateSerializer

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
def parameter_list(request: Request) -> Response:
    """GET /api/admin/parameters — list all parameters."""
    denied = _require_admin(request)
    if denied:
        return denied

    params = AdminParameter.objects.all().order_by("key")
    serializer = AdminParameterSerializer(params, many=True)
    return Response(serializer.data)


@api_view(["PATCH"])
@authentication_classes([MiddlewareAuthentication])
def parameter_update(request: Request, key: str) -> Response:
    """PATCH /api/admin/parameters/:key — update parameter value."""
    denied = _require_admin(request)
    if denied:
        return denied

    try:
        param = AdminParameter.objects.get(key=key)
    except AdminParameter.DoesNotExist:
        return Response(
            {"error": "PARAMETER_NOT_FOUND", "message": f"Parameter '{key}' not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = AdminParameterUpdateSerializer(
        data=request.data, context={"parameter": param}
    )
    if not serializer.is_valid():
        return Response(
            {"error": "INVALID_VALUE", "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    param.value = serializer.validated_data["value"]
    param.updated_by = request.user.id
    param.updated_at = timezone.now()
    param.save(update_fields=["value", "updated_by", "updated_at"])

    return Response(AdminParameterSerializer(param).data)
