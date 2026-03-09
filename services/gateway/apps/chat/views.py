import uuid

from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response

from apps.ideas.authentication import MiddlewareAuthentication
from apps.ideas.models import ChatMessage, Idea, IdeaCollaborator

from .serializers import ChatMessageCreateSerializer, ChatMessageResponseSerializer

DEFAULT_LIMIT = 50
MAX_LIMIT = 100


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


def _get_idea_or_error(idea_id: str):
    """Validate UUID and fetch idea. Returns (idea, None) or (None, Response)."""
    try:
        uuid.UUID(idea_id)
    except ValueError:
        return None, Response(
            {"error": "NOT_FOUND", "message": "Idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        idea = Idea.objects.get(id=idea_id, deleted_at__isnull=True)
    except Idea.DoesNotExist:
        return None, Response(
            {"error": "NOT_FOUND", "message": "Idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    return idea, None


def _check_access(user, idea) -> bool:
    """Check if user has access to idea (owner, co-owner, or collaborator)."""
    if idea.owner_id == user.id:
        return True
    if idea.co_owner_id == user.id:
        return True
    return IdeaCollaborator.objects.filter(
        idea_id=idea.id, user_id=user.id
    ).exists()


@api_view(["GET", "POST"])
@authentication_classes([MiddlewareAuthentication])
def chat_messages(request: Request, idea_id: str) -> Response:
    """Route /api/ideas/:id/chat — GET lists, POST creates."""
    if request.method == "POST":
        return _create_message(request, idea_id)
    return _list_messages(request, idea_id)


def _create_message(request: Request, idea_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    idea, error = _get_idea_or_error(idea_id)
    if error:
        return error

    if not _check_access(user, idea):
        return Response(
            {"error": "ACCESS_DENIED", "message": "You do not have access to this idea"},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = ChatMessageCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    message = ChatMessage.objects.create(
        idea_id=idea.id,
        sender_type="user",
        sender_id=user.id,
        content=serializer.validated_data["content"],
    )

    response_serializer = ChatMessageResponseSerializer(message)
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)


def _list_messages(request: Request, idea_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    idea, error = _get_idea_or_error(idea_id)
    if error:
        return error

    if not _check_access(user, idea):
        return Response(
            {"error": "ACCESS_DENIED", "message": "You do not have access to this idea"},
            status=status.HTTP_403_FORBIDDEN,
        )

    limit = min(int(request.query_params.get("limit", DEFAULT_LIMIT)), MAX_LIMIT)
    offset = max(int(request.query_params.get("offset", 0)), 0)

    qs = ChatMessage.objects.filter(idea_id=idea.id).order_by("created_at")
    total = qs.count()
    messages = list(qs[offset : offset + limit])

    response_serializer = ChatMessageResponseSerializer(messages, many=True)
    return Response(
        {
            "messages": response_serializer.data,
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    )
