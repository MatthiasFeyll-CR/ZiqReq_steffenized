import logging
import re
import uuid

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response

from apps.admin_config.models import AdminParameter
from apps.ideas.authentication import MiddlewareAuthentication
from apps.ideas.models import ChatMessage, Idea, IdeaCollaborator, UserReaction

from .serializers import (
    ChatMessageCreateSerializer,
    ChatMessageResponseSerializer,
    ReactionCreateSerializer,
    ReactionResponseSerializer,
)

logger = logging.getLogger(__name__)


def _publish_notification(**kwargs) -> None:
    """Lazy-import wrapper to avoid module-collection ordering issues in tests."""
    from events.publisher import publish_notification_event

    publish_notification_event(**kwargs)


def _trigger_ai_processing(idea_id: str, message_id: str) -> None:
    """Trigger AI chat processing via the AI gRPC client."""
    import os
    from grpc_clients.ai_client import AiClient

    address = os.environ.get("AI_GRPC_ADDRESS", "localhost:50052")
    logger.info(
        "[DEBUG] Creating AiClient with address=%s for idea=%s",
        address, idea_id,
    )
    client = AiClient(address=address)
    result = client.trigger_chat_processing(idea_id=idea_id, message_id=message_id)
    logger.info("[DEBUG] AiClient.trigger_chat_processing returned: %s", result)


DEFAULT_LIMIT = 50
MAX_LIMIT = 100
DEFAULT_CHAT_MESSAGE_CAP = 5


def _get_chat_message_cap() -> int:
    """Read chat_message_cap admin param, fallback to default.

    Uses a savepoint so that a failed query (e.g., unmanaged table not existing
    in tests) doesn't abort the enclosing transaction.
    """
    from django.db import transaction

    try:
        with transaction.atomic():
            param = AdminParameter.objects.get(key="chat_message_cap")
            return int(param.value)
    except Exception:
        return DEFAULT_CHAT_MESSAGE_CAP


def get_unprocessed_message_count(idea_id: str) -> int:
    """Count user messages sent after the last AI response for an idea.

    This queries the database directly, avoiding cross-process state issues
    that occurred with the previous in-memory counter approach.
    """
    last_ai_message = (
        ChatMessage.objects.filter(idea_id=idea_id, sender_type="ai")
        .order_by("-created_at")
        .values("created_at")
        .first()
    )

    qs = ChatMessage.objects.filter(idea_id=idea_id, sender_type="user")
    if last_ai_message:
        qs = qs.filter(created_at__gt=last_ai_message["created_at"])

    return qs.count()


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


def _broadcast_rate_limit(idea_id: str) -> None:
    """Broadcast a rate_limit event to the idea's WebSocket group."""
    try:
        channel_layer = get_channel_layer()
        if channel_layer is None:
            return

        group_name = f"idea_{idea_id}"
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "rate_limit",
                "idea_id": idea_id,
                "payload": {"idea_id": idea_id},
            },
        )
    except Exception:
        logger.exception("Failed to broadcast rate limit for idea %s", idea_id)


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

    # Rate limit check: 429 when unprocessed user messages >= chat_message_cap
    idea_id_str = str(idea.id)
    cap = _get_chat_message_cap()
    current_count = get_unprocessed_message_count(idea_id_str)
    if current_count >= cap:
        # Broadcast rate_limit event via WebSocket
        _broadcast_rate_limit(idea_id_str)
        return Response(
            {
                "error": {
                    "code": "rate_limited",
                    "message": "Chat input is locked. Please wait for AI to complete processing.",
                }
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS,
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

    # Detect @mentions and publish notification events
    _publish_mention_notifications(message, user, idea)

    # Trigger AI processing for this message
    logger.info(
        "[DEBUG] Chat message created: id=%s, idea_id=%s, sender=%s. "
        "Attempting to trigger AI processing...",
        message.id, idea.id, user.id,
    )
    try:
        _trigger_ai_processing(str(idea.id), str(message.id))
        logger.info(
            "[DEBUG] AI processing trigger succeeded for idea=%s, message=%s",
            idea.id, message.id,
        )
    except Exception:
        logger.exception(
            "[DEBUG] AI processing trigger FAILED for idea=%s, message=%s",
            idea.id, message.id,
        )

    return Response(response_serializer.data, status=status.HTTP_201_CREATED)


_MENTION_PATTERN = re.compile(r"@user\[([0-9a-fA-F-]{36})\]")


def _publish_mention_notifications(message: ChatMessage, sender, idea: Idea) -> None:
    """Detect @user[<uuid>] mentions in message content and publish notification events."""
    matches = _MENTION_PATTERN.findall(message.content)
    seen: set[str] = set()
    for mentioned_id in matches:
        if mentioned_id in seen:
            continue
        seen.add(mentioned_id)
        # Don't notify the sender about their own mention
        if mentioned_id == str(sender.id):
            continue
        try:
            _publish_notification(
                routing_key="notification.chat.mention",
                user_id=mentioned_id,
                event_type="chat_mention",
                title="You were mentioned",
                body=f"{sender.display_name} mentioned you in \"{idea.title}\"",
                reference_id=str(idea.id),
                reference_type="idea",
            )
        except Exception:
            logger.exception(
                "Failed to publish mention notification for user %s", mentioned_id
            )


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
