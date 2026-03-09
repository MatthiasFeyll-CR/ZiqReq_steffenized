import uuid

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response

from apps.authentication.models import User

from .authentication import MiddlewareAuthentication
from .models import ChatMessage, Idea, IdeaCollaborator
from .serializers import IdeaCreateSerializer, IdeaDetailSerializer, IdeaPatchSerializer

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
def ideas_root(request: Request) -> Response:
    """Route /api/ideas/ — GET lists, POST creates."""
    if request.method == "POST":
        return _create_idea(request)
    return _list_ideas(request)


@api_view(["GET", "PATCH", "DELETE"])
@authentication_classes([MiddlewareAuthentication])
def ideas_detail(request: Request, idea_id: str) -> Response:
    """Route /api/ideas/:id — GET detail, PATCH update, DELETE soft-delete."""
    if request.method == "DELETE":
        return _delete_idea(request, idea_id)
    if request.method == "PATCH":
        return _patch_idea(request, idea_id)
    return _get_idea(request, idea_id)


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def restore_idea(request: Request, idea_id: str) -> Response:
    """POST /api/ideas/:id/restore — Restore from trash."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        uuid.UUID(idea_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        idea = Idea.objects.get(id=idea_id)
    except Idea.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if idea.owner_id != user.id and idea.co_owner_id != user.id:
        return Response(
            {"error": "ACCESS_DENIED", "message": "Only owner or co-owner can restore"},
            status=status.HTTP_403_FORBIDDEN,
        )

    idea.deleted_at = None
    idea.save(update_fields=["deleted_at", "updated_at"])

    return Response({"message": "Idea restored"})


# --- Internal handlers (called from router views above) ---


def _create_idea(request: Request) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    serializer = IdeaCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    first_message = serializer.validated_data["first_message"]

    idea = Idea.objects.create(owner_id=user.id)

    ChatMessage.objects.create(
        idea_id=idea.id,
        sender_type="user",
        sender_id=user.id,
        content=first_message,
    )

    user_map = {user.id: user}
    detail_serializer = IdeaDetailSerializer(idea, context={"user_map": user_map})
    return Response(detail_serializer.data, status=status.HTTP_201_CREATED)


def _list_ideas(request: Request) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    filter_param = request.query_params.get("filter")
    state_param = request.query_params.get("state")
    search_param = request.query_params.get("search")
    page = max(int(request.query_params.get("page", 1)), 1)
    page_size = min(int(request.query_params.get("page_size", DEFAULT_PAGE_SIZE)), MAX_PAGE_SIZE)

    if filter_param == "my_ideas":
        qs = Idea.objects.filter(owner_id=user.id, deleted_at__isnull=True)
    elif filter_param == "collaborating":
        collab_idea_ids = IdeaCollaborator.objects.filter(user_id=user.id).values_list("idea_id", flat=True)
        qs = Idea.objects.filter(id__in=collab_idea_ids, deleted_at__isnull=True)
    elif filter_param == "trash":
        qs = Idea.objects.filter(
            Q(owner_id=user.id) | Q(co_owner_id=user.id),
            deleted_at__isnull=False,
        )
    else:
        collab_idea_ids = IdeaCollaborator.objects.filter(user_id=user.id).values_list("idea_id", flat=True)
        qs = Idea.objects.filter(
            Q(owner_id=user.id) | Q(id__in=collab_idea_ids),
            deleted_at__isnull=True,
        )

    if state_param:
        qs = qs.filter(state=state_param)

    if search_param:
        qs = qs.filter(title__icontains=search_param)

    qs = qs.annotate(collab_count=Count("collaborators")).order_by("-updated_at")

    total_count = qs.count()
    offset = (page - 1) * page_size
    ideas = list(qs[offset : offset + page_size])

    owner_ids = {idea.owner_id for idea in ideas}
    users = User.objects.filter(id__in=owner_ids)
    user_map = {u.id: u for u in users}

    results = []
    for idea in ideas:
        role = "owner" if idea.owner_id == user.id else "collaborator"
        owner = user_map.get(idea.owner_id)
        results.append(
            {
                "id": str(idea.id),
                "title": idea.title,
                "state": idea.state,
                "visibility": idea.visibility,
                "role": role,
                "owner": {
                    "id": str(owner.id) if owner else str(idea.owner_id),
                    "display_name": owner.display_name if owner else "",
                },
                "collaborator_count": idea.collab_count,
                "updated_at": idea.updated_at.isoformat(),
                "deleted_at": idea.deleted_at.isoformat() if idea.deleted_at else None,
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


def _get_idea(request: Request, idea_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        uuid.UUID(idea_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        idea = Idea.objects.get(id=idea_id)
    except Idea.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    is_owner = idea.owner_id == user.id
    is_co_owner = idea.co_owner_id == user.id
    is_collaborator = IdeaCollaborator.objects.filter(idea_id=idea.id, user_id=user.id).exists()

    if not (is_owner or is_co_owner or is_collaborator):
        return Response(
            {"error": "ACCESS_DENIED", "message": "You do not have access to this idea"},
            status=status.HTTP_403_FORBIDDEN,
        )

    owner_ids = {idea.owner_id}
    if idea.co_owner_id:
        owner_ids.add(idea.co_owner_id)
    users = User.objects.filter(id__in=owner_ids)
    user_map = {u.id: u for u in users}

    detail_serializer = IdeaDetailSerializer(idea, context={"user_map": user_map})
    return Response(detail_serializer.data)


def _patch_idea(request: Request, idea_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        uuid.UUID(idea_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        idea = Idea.objects.get(id=idea_id)
    except Idea.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if idea.owner_id != user.id and idea.co_owner_id != user.id:
        return Response(
            {"error": "ACCESS_DENIED", "message": "Only owner or co-owner can update"},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = IdeaPatchSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    update_fields = ["updated_at"]
    if "title" in serializer.validated_data:
        idea.title = serializer.validated_data["title"]
        idea.title_manually_edited = True
        update_fields.extend(["title", "title_manually_edited"])
    if "agent_mode" in serializer.validated_data:
        idea.agent_mode = serializer.validated_data["agent_mode"]
        update_fields.append("agent_mode")

    idea.save(update_fields=update_fields)

    owner_ids = {idea.owner_id}
    if idea.co_owner_id:
        owner_ids.add(idea.co_owner_id)
    users = User.objects.filter(id__in=owner_ids)
    user_map = {u.id: u for u in users}

    detail_serializer = IdeaDetailSerializer(idea, context={"user_map": user_map})
    return Response(detail_serializer.data)


def _delete_idea(request: Request, idea_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        uuid.UUID(idea_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        idea = Idea.objects.get(id=idea_id)
    except Idea.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if idea.owner_id != user.id and idea.co_owner_id != user.id:
        return Response(
            {"error": "ACCESS_DENIED", "message": "Only owner or co-owner can delete"},
            status=status.HTTP_403_FORBIDDEN,
        )

    idea.deleted_at = timezone.now()
    idea.save(update_fields=["deleted_at", "updated_at"])

    return Response({"message": "Idea moved to trash"})
