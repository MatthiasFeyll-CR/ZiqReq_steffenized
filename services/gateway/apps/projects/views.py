import logging
import secrets
import uuid

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response

from apps.authentication.models import User

from .authentication import MiddlewareAuthentication
from .models import ChatContextSummary, ChatMessage, Project, ProjectCollaborator
from .serializers import (
    ProjectCreateSerializer,
    ProjectDetailSerializer,
    ProjectPatchSerializer,
)

logger = logging.getLogger(__name__)

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def _require_auth(request: Request):
    """Return user or None. If None, caller should return 401."""
    user = request.user
    if user is None or not getattr(user, "id", None):
        return None
    return user


def _unauthorized_response() -> Response:
    return Response(
        {"error": "UNAUTHORIZED", "message": "Authentication required"},
        status=status.HTTP_401_UNAUTHORIZED,
    )


@api_view(["GET", "POST"])
@authentication_classes([MiddlewareAuthentication])
def projects_root(request: Request) -> Response:
    """Route /api/projects/ — GET lists, POST creates."""
    if request.method == "POST":
        return _create_project(request)
    return _list_projects(request)


@api_view(["GET", "PATCH", "DELETE"])
@authentication_classes([MiddlewareAuthentication])
def projects_detail(request: Request, project_id: str) -> Response:
    """Route /api/projects/:id — GET detail, PATCH update, DELETE soft-delete."""
    if request.method == "DELETE":
        return _delete_project(request, project_id)
    if request.method == "PATCH":
        return _patch_project(request, project_id)
    return _get_project(request, project_id)


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def restore_project(request: Request, project_id: str) -> Response:
    """POST /api/projects/:id/restore — Restore from trash."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        uuid.UUID(project_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if project.owner_id != user.id:
        return Response(
            {"error": "ACCESS_DENIED", "message": "Only owner can restore"},
            status=status.HTTP_403_FORBIDDEN,
        )

    project.deleted_at = None
    project.save(update_fields=["deleted_at", "updated_at"])

    return Response({"message": "Project restored"})


# --- Internal handlers (called from router views above) ---


def _create_project(request: Request) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    serializer = ProjectCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    project_type = serializer.validated_data["project_type"]
    first_message = serializer.validated_data.get("first_message")

    project = Project.objects.create(
        owner_id=user.id,
        project_type=project_type,
    )

    if first_message:
        message = ChatMessage.objects.create(
            project_id=project.id,
            sender_type="user",
            sender_id=user.id,
            content=first_message,
        )

        # Trigger AI processing for the first message
        try:
            from apps.chat.views import _trigger_ai_processing

            _trigger_ai_processing(str(project.id), str(message.id))
        except Exception:
            logger.exception(
                "AI processing trigger failed for first message project=%s message=%s",
                project.id, message.id,
            )

    user_map = {user.id: user}
    detail_serializer = ProjectDetailSerializer(project, context={"user_map": user_map})
    return Response(detail_serializer.data, status=status.HTTP_201_CREATED)


def _list_projects(request: Request) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    filter_param = request.query_params.get("filter")
    state_param = request.query_params.get("state")
    search_param = request.query_params.get("search")
    page = max(int(request.query_params.get("page", 1)), 1)
    page_size = min(int(request.query_params.get("page_size", DEFAULT_PAGE_SIZE)), MAX_PAGE_SIZE)

    if filter_param == "my_projects":
        qs = Project.objects.filter(owner_id=user.id, deleted_at__isnull=True)
    elif filter_param == "collaborating":
        collab_project_ids = ProjectCollaborator.objects.filter(user_id=user.id).values_list("project_id", flat=True)
        qs = Project.objects.filter(id__in=collab_project_ids, deleted_at__isnull=True)
    elif filter_param == "trash":
        qs = Project.objects.filter(
            owner_id=user.id,
            deleted_at__isnull=False,
        )
    else:
        collab_project_ids = ProjectCollaborator.objects.filter(user_id=user.id).values_list("project_id", flat=True)
        qs = Project.objects.filter(
            Q(owner_id=user.id) | Q(id__in=collab_project_ids),
            deleted_at__isnull=True,
        )

    if state_param:
        qs = qs.filter(state=state_param)

    if search_param:
        qs = qs.filter(title__icontains=search_param)

    qs = qs.annotate(collab_count=Count("collaborators")).order_by("-updated_at")

    total_count = qs.count()
    offset = (page - 1) * page_size
    projects = list(qs[offset : offset + page_size])

    owner_ids = {project.owner_id for project in projects}
    users = User.objects.filter(id__in=owner_ids)
    user_map = {u.id: u for u in users}

    results = []
    for project in projects:
        role = "owner" if project.owner_id == user.id else "collaborator"
        owner = user_map.get(project.owner_id)
        results.append(
            {
                "id": str(project.id),
                "title": project.title,
                "project_type": project.project_type,
                "state": project.state,
                "visibility": project.visibility,
                "role": role,
                "owner": {
                    "id": str(owner.id) if owner else str(project.owner_id),
                    "display_name": owner.display_name if owner else "",
                },
                "collaborator_count": project.collab_count,
                "updated_at": project.updated_at.isoformat(),
                "deleted_at": project.deleted_at.isoformat() if project.deleted_at else None,
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


def _get_project(request: Request, project_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        uuid.UUID(project_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    is_owner = project.owner_id == user.id
    is_collaborator = ProjectCollaborator.objects.filter(project_id=project.id, user_id=user.id).exists()
    has_write_access = is_owner or is_collaborator

    users = User.objects.filter(id=project.owner_id)
    user_map = {u.id: u for u in users}

    detail_serializer = ProjectDetailSerializer(project, context={"user_map": user_map})
    data = detail_serializer.data
    data["read_only"] = not has_write_access

    return Response(data)


def _patch_project(request: Request, project_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        uuid.UUID(project_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if project.owner_id != user.id:
        return Response(
            {"error": "ACCESS_DENIED", "message": "Only owner can update"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if "visibility" in request.data:
        return Response(
            {"error": "BAD_REQUEST", "message": "Visibility cannot be manually set"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = ProjectPatchSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    update_fields = ["updated_at"]
    if "title" in serializer.validated_data:
        project.title = serializer.validated_data["title"]
        project.title_manually_edited = True
        update_fields.extend(["title", "title_manually_edited"])
    project.save(update_fields=update_fields)

    users = User.objects.filter(id=project.owner_id)
    user_map = {u.id: u for u in users}

    detail_serializer = ProjectDetailSerializer(project, context={"user_map": user_map})
    return Response(detail_serializer.data)


def _delete_project(request: Request, project_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        uuid.UUID(project_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if project.owner_id != user.id:
        return Response(
            {"error": "ACCESS_DENIED", "message": "Only owner can delete"},
            status=status.HTTP_403_FORBIDDEN,
        )

    project.deleted_at = timezone.now()
    project.save(update_fields=["deleted_at", "updated_at"])

    return Response({"message": "Project moved to trash"})


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def context_window(request: Request, project_id: str) -> Response:
    """GET /api/projects/:id/context-window — context window usage for AI indicator."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        uuid.UUID(project_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Any authenticated user can read context window (read-only access)

    # Count all messages for this project
    message_count = ChatMessage.objects.filter(project_id=project_id).count()

    # Get latest compression summary (table may not exist yet if AI service hasn't run migrations)
    latest_summary = None
    try:
        latest_summary = (
            ChatContextSummary.objects.filter(project_id=project_id)
            .order_by("-compression_iteration")
            .first()
        )
    except Exception:
        pass

    compression_iterations = latest_summary.compression_iteration if latest_summary else 0

    # Estimate token usage: ~4 chars per token (OpenAI heuristic)
    # Context window limit: 128k tokens (default)
    context_window_limit = 128_000

    from apps.admin_config.models import AdminParameter

    try:
        param = AdminParameter.objects.get(key="context_window_limit")
        context_window_limit = int(param.value)
    except (AdminParameter.DoesNotExist, ValueError):
        pass

    # Calculate recent messages (those after compression, or all if no compression)
    if latest_summary:
        recent_messages = ChatMessage.objects.filter(
            project_id=project_id,
            created_at__gt=latest_summary.created_at,
        )
    else:
        recent_messages = ChatMessage.objects.filter(project_id=project_id)

    recent_message_count = recent_messages.count()

    # Estimate tokens: recent messages + summary
    recent_tokens = sum(len(m.content) // 4 for m in recent_messages.only("content"))
    summary_tokens = len(latest_summary.summary_text) // 4 if latest_summary else 0
    total_tokens = recent_tokens + summary_tokens

    usage_percentage = min(round((total_tokens / context_window_limit) * 100, 1), 100.0)

    return Response(
        {
            "usage_percentage": usage_percentage,
            "message_count": message_count,
            "compression_iterations": compression_iterations,
            "recent_message_count": recent_message_count,
        }
    )


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def generate_share_link(request: Request, project_id: str) -> Response:
    """POST /api/projects/:id/share-link — Generate read-only share link token (owner only)."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        uuid.UUID(project_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if project.owner_id != user.id:
        return Response(
            {"error": "FORBIDDEN", "message": "Only the project owner can generate share links"},
            status=status.HTTP_403_FORBIDDEN,
        )

    token = secrets.token_hex(32)
    project.share_link_token = token
    project.save(update_fields=["share_link_token"])

    return Response(
        {
            "share_link_token": token,
            "share_url": f"/project/{project_id}?token={token}",
        },
        status=status.HTTP_201_CREATED,
    )


