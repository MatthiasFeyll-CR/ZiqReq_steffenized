import logging
import re
import uuid

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response

from apps.authentication.models import User
from apps.projects.authentication import MiddlewareAuthentication
from apps.projects.models import Project, ProjectCollaborator

from .models import CommentReaction, CommentReadStatus, ProjectComment
from .serializers import CommentCreateSerializer, CommentUpdateSerializer, ReactionSerializer

logger = logging.getLogger(__name__)

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200


def _require_auth(request: Request):
    user = request.user
    if user is None or not getattr(user, "id", None):
        return None
    return user


def _unauthorized_response() -> Response:
    return Response(
        {"error": "UNAUTHORIZED", "message": "Authentication required"},
        status=status.HTTP_401_UNAUTHORIZED,
    )


def _check_project_access(project_id: str, user_id, request=None) -> tuple:
    """Return (project, has_access, is_owner_or_collaborator) or (None, False, False).

    Any authenticated user who can reach the project (owner, co-owner, collaborator,
    or share-link viewer) has full comment access (create/edit own/delete own).
    is_privileged is True only for owner/co-owner/collaborator (they can delete
    foreign comments).
    """
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return None, False, False

    is_owner = project.owner_id == user_id
    is_collaborator = ProjectCollaborator.objects.filter(
        project_id=project.id, user_id=user_id
    ).exists()

    has_access = is_owner or is_collaborator

    # Share-link users: the ShareLinkMiddleware validates the token and either
    # adds 'share_link_viewer' to user.roles or sets request.share_link_viewer.
    if not has_access and request is not None:
        user = getattr(request, "user", None) or getattr(request, "user_obj", None)
        roles = getattr(user, "roles", None) or []
        if "share_link_viewer" in roles:
            has_access = True
        elif getattr(request, "share_link_viewer", False):
            has_access = True

    is_privileged = is_owner or is_collaborator
    return project, has_access, is_privileged


def _broadcast_ws_event(group_name: str, event_type: str, payload: dict) -> None:
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                group_name,
                {"type": event_type, "payload": payload},
            )
    except Exception:
        logger.exception("Failed to broadcast WS event %s to %s", event_type, group_name)


def _publish_notification(**kwargs) -> None:
    from events.publisher import publish_notification_event
    publish_notification_event(**kwargs)


def _broadcast_user_notification(
    user_id: str,
    *,
    event_type: str,
    title: str,
    body: str,
    reference_id: str = "",
    reference_type: str = "",
) -> None:
    try:
        channel_layer = get_channel_layer()
        if channel_layer is None:
            return
        group_name = f"user_{user_id}"
        payload = {
            "event_type": event_type,
            "title": title,
            "body": body,
            "reference_id": reference_id,
            "reference_type": reference_type,
        }
        async_to_sync(channel_layer.group_send)(
            group_name,
            {"type": "notification", "payload": payload},
        )
    except Exception:
        logger.exception("Failed to broadcast notification to user %s", user_id)


def _serialize_comment(comment: ProjectComment, user_map: dict, current_user_id=None) -> dict:
    """Serialize a single comment with author info and reactions."""
    author = user_map.get(comment.author_id) if comment.author_id else None

    reactions_qs = CommentReaction.objects.filter(comment_id=comment.id)
    # Group reactions by emoji with user lists
    reaction_map: dict[str, list[str]] = {}
    for r in reactions_qs:
        reaction_map.setdefault(r.emoji, []).append(str(r.user_id))

    reactions = [
        {"emoji": emoji, "users": users, "count": len(users)}
        for emoji, users in reaction_map.items()
    ]

    return {
        "id": str(comment.id),
        "project_id": str(comment.project_id),
        "author": {
            "id": str(author.id),
            "display_name": author.display_name,
        } if author else None,
        "parent_id": str(comment.parent_id) if comment.parent_id else None,
        "content": comment.content,
        "is_system_event": comment.is_system_event,
        "system_event_type": comment.system_event_type,
        "reactions": reactions,
        "created_at": comment.created_at.isoformat(),
        "updated_at": comment.updated_at.isoformat(),
        "is_edited": comment.updated_at != comment.created_at and not comment.is_system_event,
        "deleted_at": comment.deleted_at.isoformat() if comment.deleted_at else None,
    }


def _extract_mentions(content: str) -> list[str]:
    """Extract @username mentions from content."""
    return re.findall(r"@(\w[\w.\-]*)", content)


def _notify_mentions(content: str, project: Project, author: User, comment_id: str) -> None:
    """Send notifications to @mentioned users."""
    mentioned_names = _extract_mentions(content)
    if not mentioned_names:
        return

    # Look up users by display_name (case-insensitive)
    mentioned_users = User.objects.filter(
        display_name__in=mentioned_names
    )

    for mentioned_user in mentioned_users:
        if mentioned_user.id == author.id:
            continue

        notif_kwargs = dict(
            event_type="comment_mention",
            title="You were mentioned in a comment",
            body=f"{author.display_name} mentioned you in a comment on \"{project.title}\"",
            reference_id=str(project.id),
            reference_type="project",
        )
        _publish_notification(
            routing_key="notification.comment.mention",
            user_id=str(mentioned_user.id),
            **notif_kwargs,
        )
        _broadcast_user_notification(str(mentioned_user.id), **notif_kwargs)


# ---- API Views ----


@api_view(["GET", "POST"])
@authentication_classes([MiddlewareAuthentication])
def comments_root(request: Request, project_id: str) -> Response:
    """GET lists comments, POST creates a comment."""
    if request.method == "POST":
        return _create_comment(request, project_id)
    return _list_comments(request, project_id)


def _list_comments(request: Request, project_id: str) -> Response:
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

    project, has_access, _ = _check_project_access(project_id, user.id, request)
    if project is None:
        return Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    if not has_access:
        return Response(
            {"error": "ACCESS_DENIED", "message": "You do not have access to this project"},
            status=status.HTTP_403_FORBIDDEN,
        )

    page = max(int(request.query_params.get("page", 1)), 1)
    page_size = min(
        int(request.query_params.get("page_size", DEFAULT_PAGE_SIZE)),
        MAX_PAGE_SIZE,
    )

    qs = ProjectComment.objects.filter(project_id=project_id).order_by("created_at")
    total_count = qs.count()
    offset = (page - 1) * page_size
    comments = list(qs[offset : offset + page_size])

    # Batch load authors
    author_ids = {c.author_id for c in comments if c.author_id}
    user_map = {u.id: u for u in User.objects.filter(id__in=author_ids)}

    results = [_serialize_comment(c, user_map, user.id) for c in comments]

    next_page = page + 1 if offset + page_size < total_count else None
    previous_page = page - 1 if page > 1 else None

    return Response({
        "results": results,
        "count": total_count,
        "next": next_page,
        "previous": previous_page,
    })


def _create_comment(request: Request, project_id: str) -> Response:
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

    project, has_access, _ = _check_project_access(project_id, user.id, request)
    if project is None:
        return Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    if not has_access:
        return Response(
            {"error": "ACCESS_DENIED", "message": "You do not have access to this project"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Block comments on deleted projects
    if project.deleted_at is not None:
        return Response(
            {"error": "BAD_REQUEST", "message": "Cannot comment on a deleted project"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = CommentCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    parent_id = serializer.validated_data.get("parent_id")
    if parent_id:
        parent_exists = ProjectComment.objects.filter(
            id=parent_id, project_id=project_id, deleted_at__isnull=True
        ).exists()
        if not parent_exists:
            return Response(
                {"error": "NOT_FOUND", "message": "Parent comment not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    comment = ProjectComment.objects.create(
        project_id=project_id,
        author_id=user.id,
        parent_id=parent_id,
        content=serializer.validated_data["content"],
    )

    user_map = {user.id: user}
    data = _serialize_comment(comment, user_map, user.id)

    # Broadcast via WebSocket
    _broadcast_ws_event(
        f"project_{project_id}",
        "comment_created",
        data,
    )

    # Notify @mentioned users
    _notify_mentions(comment.content, project, user, str(comment.id))

    return Response(data, status=status.HTTP_201_CREATED)


@api_view(["PATCH", "DELETE"])
@authentication_classes([MiddlewareAuthentication])
def comment_detail(request: Request, project_id: str, comment_id: str) -> Response:
    """PATCH updates, DELETE soft-deletes a comment."""
    if request.method == "DELETE":
        return _delete_comment(request, project_id, comment_id)
    return _update_comment(request, project_id, comment_id)


def _update_comment(request: Request, project_id: str, comment_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        uuid.UUID(project_id)
        uuid.UUID(comment_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        comment = ProjectComment.objects.get(id=comment_id, project_id=project_id)
    except ProjectComment.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Comment not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if comment.is_system_event:
        return Response(
            {"error": "BAD_REQUEST", "message": "Cannot edit system events"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if comment.deleted_at is not None:
        return Response(
            {"error": "BAD_REQUEST", "message": "Cannot edit a deleted comment"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Only author can edit their own comments
    if comment.author_id != user.id:
        return Response(
            {"error": "FORBIDDEN", "message": "You can only edit your own comments"},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = CommentUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    comment.content = serializer.validated_data["content"]
    comment.save(update_fields=["content", "updated_at"])

    author = User.objects.filter(id=comment.author_id).first()
    user_map = {author.id: author} if author else {}
    data = _serialize_comment(comment, user_map, user.id)

    _broadcast_ws_event(f"project_{project_id}", "comment_updated", data)

    # Re-check mentions for new content
    project = Project.objects.filter(id=project_id).first()
    if project:
        _notify_mentions(comment.content, project, user, str(comment.id))

    return Response(data)


def _delete_comment(request: Request, project_id: str, comment_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        uuid.UUID(project_id)
        uuid.UUID(comment_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        comment = ProjectComment.objects.get(id=comment_id, project_id=project_id)
    except ProjectComment.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Comment not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if comment.is_system_event:
        return Response(
            {"error": "BAD_REQUEST", "message": "Cannot delete system events"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if comment.deleted_at is not None:
        return Response(
            {"error": "BAD_REQUEST", "message": "Comment already deleted"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Author can delete their own; owner/co-owner/collaborator can delete any
    is_author = comment.author_id == user.id
    project, _, is_privileged = _check_project_access(project_id, user.id, request)
    if not is_author and not is_privileged:
        return Response(
            {"error": "FORBIDDEN", "message": "You cannot delete this comment"},
            status=status.HTTP_403_FORBIDDEN,
        )

    comment.deleted_at = timezone.now()
    comment.save(update_fields=["deleted_at", "updated_at"])

    _broadcast_ws_event(
        f"project_{project_id}",
        "comment_deleted",
        {"id": str(comment.id), "project_id": project_id},
    )

    return Response({"message": "Comment deleted"})


@api_view(["POST", "DELETE"])
@authentication_classes([MiddlewareAuthentication])
def comment_reaction(request: Request, project_id: str, comment_id: str) -> Response:
    """POST adds a reaction, DELETE removes it."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        uuid.UUID(project_id)
        uuid.UUID(comment_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Verify comment exists
    try:
        comment = ProjectComment.objects.get(id=comment_id, project_id=project_id, deleted_at__isnull=True)
    except ProjectComment.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Comment not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = ReactionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    emoji = serializer.validated_data["emoji"]

    if request.method == "POST":
        _, created = CommentReaction.objects.get_or_create(
            comment=comment,
            user_id=user.id,
            emoji=emoji,
        )
        action = "added"
    else:
        deleted_count, _ = CommentReaction.objects.filter(
            comment=comment,
            user_id=user.id,
            emoji=emoji,
        ).delete()
        if deleted_count == 0:
            return Response(
                {"error": "NOT_FOUND", "message": "Reaction not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        action = "removed"

    _broadcast_ws_event(
        f"project_{project_id}",
        "comment_reaction",
        {
            "comment_id": str(comment_id),
            "project_id": project_id,
            "emoji": emoji,
            "user_id": str(user.id),
            "action": action,
        },
    )

    return Response({"action": action, "emoji": emoji})


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def mark_comments_read(request: Request, project_id: str) -> Response:
    """POST /api/projects/:id/comments/mark-read — Update last-read timestamp."""
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

    now = timezone.now()
    CommentReadStatus.objects.update_or_create(
        project_id=project_id,
        user_id=user.id,
        defaults={"last_read_at": now},
    )

    return Response({"last_read_at": now.isoformat()})


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def unread_comment_count(request: Request, project_id: str) -> Response:
    """GET /api/projects/:id/comments/unread-count — Count comments since last read."""
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

    read_status = CommentReadStatus.objects.filter(
        project_id=project_id, user_id=user.id
    ).first()

    qs = ProjectComment.objects.filter(
        project_id=project_id,
        deleted_at__isnull=True,
        is_system_event=False,
    ).exclude(author_id=user.id)

    if read_status:
        qs = qs.filter(created_at__gt=read_status.last_read_at)

    count = qs.count()

    return Response({"unread_count": count})


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def search_projects_for_reference(request: Request) -> Response:
    """GET /api/projects/search-ref?q=<query> — Search projects by title for # references."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    query = request.query_params.get("q", "").strip()
    if not query or len(query) < 2:
        return Response({"results": []})

    projects = Project.objects.filter(
        title__icontains=query,
        deleted_at__isnull=True,
    ).order_by("-updated_at")[:10]

    results = [
        {"id": str(project.id), "title": project.title}
        for project in projects
    ]

    return Response({"results": results})
