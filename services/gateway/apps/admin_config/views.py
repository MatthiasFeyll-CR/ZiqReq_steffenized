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
def admin_attachments_list(request: Request) -> Response:
    """GET /api/admin/attachments — list all attachments with filter/search/pagination/stats."""
    denied = _require_admin(request)
    if denied:
        return denied

    from django.db.models import Count, Sum

    from apps.projects.models import Attachment, Project

    filter_param = request.query_params.get("filter", "all")
    search_param = request.query_params.get("search", "")
    page = max(int(request.query_params.get("page", 1)), 1)
    page_size = min(
        int(request.query_params.get("page_size", 35)),
        MAX_PAGE_SIZE,
    )

    qs = Attachment.objects.all()

    if filter_param == "active":
        qs = qs.filter(deleted_at__isnull=True)
    elif filter_param == "deleted":
        qs = qs.filter(deleted_at__isnull=False)

    if search_param:
        qs = qs.filter(Q(filename__icontains=search_param))

    qs = qs.order_by("-created_at")

    total_count = qs.count()
    offset = (page - 1) * page_size
    attachments = list(qs[offset : offset + page_size])

    # Get project names
    project_ids = {a.project_id for a in attachments}
    projects = Project.objects.filter(id__in=project_ids)
    project_map = {p.id: p for p in projects}

    # Stats (unfiltered)
    stats = Attachment.objects.aggregate(
        total_size=Sum("size_bytes"),
        total_count=Count("id"),
    )

    results = []
    for att in attachments:
        proj = project_map.get(att.project_id)
        results.append(
            {
                "id": str(att.id),
                "filename": att.filename,
                "content_type": att.content_type,
                "size_bytes": att.size_bytes,
                "extraction_status": att.extraction_status,
                "created_at": att.created_at.isoformat(),
                "deleted_at": att.deleted_at.isoformat() if att.deleted_at else None,
                "message_id": str(att.message_id) if att.message_id else None,
                "project": {
                    "id": str(att.project_id),
                    "title": proj.title if proj else "Unknown",
                },
            }
        )

    return Response(
        {
            "results": results,
            "count": total_count,
            "next": page + 1 if offset + page_size < total_count else None,
            "previous": page - 1 if page > 1 else None,
            "stats": {
                "total_size_bytes": stats["total_size"] or 0,
                "total_count": stats["total_count"] or 0,
            },
        }
    )


@api_view(["DELETE"])
@authentication_classes([MiddlewareAuthentication])
def admin_attachment_delete(request: Request, attachment_id: str) -> Response:
    """DELETE /api/admin/attachments/:id — hard-delete attachment (DB record + storage file)."""
    denied = _require_admin(request)
    if denied:
        return denied

    import uuid

    from apps.projects.models import Attachment

    try:
        uuid.UUID(attachment_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Attachment not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        attachment = Attachment.objects.get(id=attachment_id)
    except Attachment.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Attachment not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Delete storage file (best-effort)
    try:
        from storage.factory import get_storage_backend

        backend = get_storage_backend()
        backend.delete_file(attachment.storage_key)
    except Exception:
        logger.warning("Failed to delete storage file %s", attachment.storage_key)

    logger.info("Admin %s hard-deleted attachment %s (storage_key=%s)", request.user.id, attachment_id, attachment.storage_key)
    attachment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def admin_attachment_restore(request: Request, attachment_id: str) -> Response:
    """POST /api/admin/attachments/:id/restore/ — restore soft-deleted attachment."""
    denied = _require_admin(request)
    if denied:
        return denied

    import uuid

    from apps.attachments.serializers import AttachmentResponseSerializer
    from apps.projects.models import Attachment, Project

    try:
        uuid.UUID(attachment_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Attachment not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        attachment = Attachment.objects.get(id=attachment_id, deleted_at__isnull=False)
    except Attachment.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Attachment not found or not deleted"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Verify project still exists
    if not Project.objects.filter(id=attachment.project_id, deleted_at__isnull=True).exists():
        return Response(
            {"error": "PROJECT_DELETED", "message": "Cannot restore attachment for deleted project"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check storage file still exists
    from storage.factory import get_storage_backend

    backend = get_storage_backend()
    if not backend.file_exists(attachment.storage_key):
        return Response(
            {"error": "FILE_GONE", "message": "Storage file no longer exists"},
            status=status.HTTP_410_GONE,
        )

    attachment.deleted_at = None
    attachment.save(update_fields=["deleted_at"])
    logger.info("Admin %s restored attachment %s", request.user.id, attachment_id)
    return Response(AttachmentResponseSerializer(attachment).data)


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
