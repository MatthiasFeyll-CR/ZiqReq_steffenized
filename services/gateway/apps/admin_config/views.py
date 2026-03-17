import logging

from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response

from apps.projects.authentication import MiddlewareAuthentication

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


DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def admin_projects_list(request: Request) -> Response:
    """GET /api/admin/projects — list all projects with state and keywords (admin only)."""
    denied = _require_admin(request)
    if denied:
        return denied

    from apps.authentication.models import User
    from apps.projects.models import Project

    state_param = request.query_params.get("state")
    search_param = request.query_params.get("search")
    page = max(int(request.query_params.get("page", 1)), 1)
    page_size = min(
        int(request.query_params.get("page_size", DEFAULT_PAGE_SIZE)),
        MAX_PAGE_SIZE,
    )

    qs = Project.objects.filter(deleted_at__isnull=True)

    if state_param:
        qs = qs.filter(state=state_param)

    if search_param:
        qs = qs.filter(Q(title__icontains=search_param))

    qs = qs.order_by("-updated_at")

    total_count = qs.count()
    offset = (page - 1) * page_size
    projects = list(qs[offset : offset + page_size])

    # Fetch owners
    owner_ids = {project.owner_id for project in projects}
    users = User.objects.filter(id__in=owner_ids)
    user_map = {u.id: u for u in users}

    results = []
    for project in projects:
        owner = user_map.get(project.owner_id)
        results.append(
            {
                "id": str(project.id),
                "title": project.title,
                "state": project.state,
                "owner": {
                    "id": str(owner.id) if owner else str(project.owner_id),
                    "display_name": owner.display_name if owner else "",
                },
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat(),
            }
        )

    next_page = page + 1 if offset + page_size < total_count else None
    previous_page = page - 1 if page > 1 else None

    return Response(
        {
            "results": results,
            "count": total_count,
            "next": next_page,
            "previous": previous_page,
        }
    )
