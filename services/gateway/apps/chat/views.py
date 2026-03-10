import logging
import uuid

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response

from apps.ideas.authentication import MiddlewareAuthentication
from apps.ideas.models import ChatMessage, Idea, IdeaCollaborator, UserReaction

from .serializers import (
    ChatMessageCreateSerializer,
    ChatMessageResponseSerializer,
    ReactionCreateSerializer,
    ReactionResponseSerializer,
)

logger = logging.getLogger(__name__)

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


def _broadcast_chat_message(message: ChatMessage, sender_user) -> None:
    """Broadcast a chat_message event to the idea's WebSocket group."""
    try:
        channel_layer = get_channel_layer()
        if channel_layer is None:
            return

        group_name = f"idea_{message.idea_id}"
        payload = {
            "id": str(message.id),
            "sender_type": message.sender_type,
            "sender": {
                "id": str(sender_user.id),
                "display_name": getattr(sender_user, "display_name", ""),
            },
            "ai_agent": message.ai_agent,
            "content": message.content,
            "message_type": message.message_type,
            "created_at": message.created_at.isoformat(),
        }
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "chat_message",
                "idea_id": str(message.idea_id),
                "payload": payload,
            },
        )
    except Exception:
        logger.exception("Failed to broadcast chat message %s", message.id)


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

    # Broadcast chat.message.created to WebSocket subscribers
    _broadcast_chat_message(message, user)

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


@api_view(["POST", "DELETE"])
@authentication_classes([MiddlewareAuthentication])
def message_reactions(
    request: Request, idea_id: str, message_id: str
) -> Response:
    """Route /api/ideas/:id/chat/:msgId/reactions — POST adds, DELETE removes."""
    if request.method == "POST":
        return _add_reaction(request, idea_id, message_id)
    return _remove_reaction(request, idea_id, message_id)


def _add_reaction(
    request: Request, idea_id: str, message_id: str
) -> Response:
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

    # Validate message_id UUID
    try:
        uuid.UUID(message_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Message not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Fetch the target message and verify it belongs to this idea
    try:
        message = ChatMessage.objects.get(id=message_id, idea_id=idea.id)
    except ChatMessage.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Message not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Cannot react to AI messages
    if message.sender_type == "ai":
        return Response(
            {"error": "CANNOT_REACT_TO_AI", "message": "Cannot react to AI messages"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Cannot react to own messages
    if message.sender_id == user.id:
        return Response(
            {"error": "CANNOT_REACT_TO_SELF", "message": "Cannot react to your own messages"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = ReactionCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Check for duplicate reaction
    if UserReaction.objects.filter(message_id=message.id, user_id=user.id).exists():
        return Response(
            {"error": "ALREADY_REACTED", "message": "You have already reacted to this message"},
            status=status.HTTP_409_CONFLICT,
        )

    reaction = UserReaction.objects.create(
        message_id=message.id,
        user_id=user.id,
        reaction_type=serializer.validated_data["reaction_type"],
    )

    response_serializer = ReactionResponseSerializer(reaction)
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)


def _remove_reaction(
    request: Request, idea_id: str, message_id: str
) -> Response:
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

    # Validate message_id UUID
    try:
        uuid.UUID(message_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Reaction not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        reaction = UserReaction.objects.get(message_id=message_id, user_id=user.id)
    except UserReaction.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Reaction not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    reaction.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
