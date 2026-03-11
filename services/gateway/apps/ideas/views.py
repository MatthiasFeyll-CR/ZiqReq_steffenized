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
from .models import ChatContextSummary, ChatMessage, Idea, IdeaCollaborator
from .serializers import (
    IdeaCreateSerializer,
    IdeaDetailSerializer,
    IdeaPatchSerializer,
    MergeRequestConsentSerializer,
    MergeRequestCreateSerializer,
    MergeRequestSerializer,
    SimilarIdeaSerializer,
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
    data = detail_serializer.data

    # Attach merge_request_pending if an active merge request targets this idea
    from apps.similarity.models import MergeRequest as MergeRequestModel

    pending_mr = (
        MergeRequestModel.objects.filter(target_idea_id=idea.id, status="pending")
        .order_by("-created_at")
        .first()
    )
    if pending_mr:
        requesting_owner = User.objects.filter(id=pending_mr.requested_by).first()
        requesting_idea = Idea.objects.filter(id=pending_mr.requesting_idea_id).first()
        data["merge_request_pending"] = {
            "id": str(pending_mr.id),
            "requesting_idea_id": str(pending_mr.requesting_idea_id),
            "requesting_owner_name": requesting_owner.display_name if requesting_owner else "",
            "requesting_idea_title": requesting_idea.title if requesting_idea else "",
        }
    else:
        data["merge_request_pending"] = None

    # Attach merged_idea_ref / appended_idea_ref for old ideas
    if idea.closed_by_merge_id:
        ref_idea = Idea.objects.filter(id=idea.closed_by_merge_id, deleted_at__isnull=True).first()
        data["merged_idea_ref"] = {
            "id": str(ref_idea.id),
            "title": ref_idea.title,
            "url": f"/idea/{ref_idea.id}",
        } if ref_idea else None
    else:
        data["merged_idea_ref"] = None

    if idea.closed_by_append_id:
        ref_idea = Idea.objects.filter(id=idea.closed_by_append_id, deleted_at__isnull=True).first()
        data["appended_idea_ref"] = {
            "id": str(ref_idea.id),
            "title": ref_idea.title,
            "url": f"/idea/{ref_idea.id}",
        } if ref_idea else None
    else:
        data["appended_idea_ref"] = None

    return Response(data)


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

    if "visibility" in request.data:
        return Response(
            {"error": "BAD_REQUEST", "message": "Visibility cannot be manually set"},
            status=status.HTTP_400_BAD_REQUEST,
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


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def context_window(request: Request, idea_id: str) -> Response:
    """GET /api/ideas/:id/context-window — context window usage for AI indicator."""
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

    # Count all messages for this idea
    message_count = ChatMessage.objects.filter(idea_id=idea_id).count()

    # Get latest compression summary (table may not exist yet if AI service hasn't run migrations)
    latest_summary = None
    try:
        latest_summary = (
            ChatContextSummary.objects.filter(idea_id=idea_id)
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
            idea_id=idea_id,
            created_at__gt=latest_summary.created_at,
        )
    else:
        recent_messages = ChatMessage.objects.filter(idea_id=idea_id)

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
def generate_share_link(request: Request, idea_id: str) -> Response:
    """POST /api/ideas/:id/share-link — Generate read-only share link token (owner only)."""
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

    if idea.owner_id != user.id:
        return Response(
            {"error": "FORBIDDEN", "message": "Only the idea owner can generate share links"},
            status=status.HTTP_403_FORBIDDEN,
        )

    token = secrets.token_hex(32)
    idea.share_link_token = token
    idea.save(update_fields=["share_link_token"])

    return Response(
        {
            "share_link_token": token,
            "share_url": f"/idea/{idea_id}?token={token}",
        },
        status=status.HTTP_201_CREATED,
    )


SIMILAR_DEFAULT_PAGE_SIZE = 10
SIMILAR_MAX_PAGE_SIZE = 50

_NEAR_THRESHOLD_SQL = """
    SELECT
        b.idea_id AS other_idea_id,
        1 - (a.embedding <=> b.embedding) AS similarity_score
    FROM idea_embeddings a
    JOIN idea_embeddings b ON a.idea_id <> b.idea_id
    JOIN ideas ib ON ib.id = b.idea_id
        AND ib.deleted_at IS NULL
    WHERE a.idea_id = %s
        AND (1 - (a.embedding <=> b.embedding)) >= 0.65
        AND (1 - (a.embedding <=> b.embedding)) < 0.75
    ORDER BY similarity_score DESC
"""


def _get_near_threshold_matches(idea_id: uuid.UUID) -> list[dict]:
    """Query pgvector for near-threshold cosine similarity matches (0.65–0.75)."""
    from django.db import connection, transaction

    matches: list[dict] = []
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(_NEAR_THRESHOLD_SQL, [str(idea_id)])
                for row in cursor.fetchall():
                    matches.append(
                        {
                            "idea_id": row[0],
                            "similarity_type": "near_threshold",
                            "similarity_score": round(float(row[1]), 4),
                        }
                    )
    except Exception:
        # pgvector / idea_embeddings table may not be available
        pass
    return matches


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def get_similar_ideas(request: Request, idea_id: str) -> Response:
    """GET /api/ideas/:id/similar — declined merges + near-threshold vector matches."""
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

    # Permission check: owner, co-owner, collaborator, or assigned reviewer
    is_owner = idea.owner_id == user.id
    is_co_owner = idea.co_owner_id == user.id
    is_collaborator = IdeaCollaborator.objects.filter(idea_id=idea.id, user_id=user.id).exists()

    from apps.review.models import ReviewAssignment

    is_reviewer = ReviewAssignment.objects.filter(
        idea_id=idea.id, reviewer_id=user.id, unassigned_at__isnull=True
    ).exists()

    if not (is_owner or is_co_owner or is_collaborator or is_reviewer):
        return Response(
            {"error": "ACCESS_DENIED", "message": "You do not have access to this idea"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Pagination
    page = max(int(request.query_params.get("page", 1)), 1)
    page_size = min(
        int(request.query_params.get("page_size", SIMILAR_DEFAULT_PAGE_SIZE)),
        SIMILAR_MAX_PAGE_SIZE,
    )

    results = []

    # 1. Declined merges where this idea is involved
    from apps.similarity.models import MergeRequest

    declined_merges = MergeRequest.objects.filter(
        status="declined",
    ).filter(Q(requesting_idea_id=idea.id) | Q(target_idea_id=idea.id))

    for mr in declined_merges:
        other_idea_id = mr.target_idea_id if mr.requesting_idea_id == idea.id else mr.requesting_idea_id
        results.append(
            {
                "idea_id": other_idea_id,
                "similarity_type": "declined_merge",
                "similarity_score": None,
            }
        )

    # 2. Near-threshold vector matches (cosine similarity 0.65–0.75)
    near_threshold_matches = _get_near_threshold_matches(idea.id)
    for match in near_threshold_matches:
        if not any(r["idea_id"] == match["idea_id"] for r in results):
            results.append(match)

    # Deduplicate by idea_id (keep first occurrence)
    seen = set()
    unique_results = []
    for r in results:
        if r["idea_id"] not in seen:
            seen.add(r["idea_id"])
            unique_results.append(r)
    results = unique_results

    # Fetch idea details for all results
    other_idea_ids = [r["idea_id"] for r in results]
    other_ideas = {i.id: i for i in Idea.objects.filter(id__in=other_idea_ids, deleted_at__isnull=True)}

    # Fetch keywords for other ideas
    from apps.similarity.models import IdeaKeywords

    keywords_map = {
        kw.idea_id: kw.keywords
        for kw in IdeaKeywords.objects.filter(idea_id__in=other_idea_ids)
    }

    # Build final results
    final_results = []
    for r in results:
        other_idea = other_ideas.get(r["idea_id"])
        if other_idea is None:
            continue
        final_results.append(
            {
                "id": other_idea.id,
                "title": other_idea.title,
                "keywords": keywords_map.get(r["idea_id"], []),
                "similarity_type": r["similarity_type"],
                "similarity_score": r["similarity_score"],
            }
        )

    # Paginate
    total_count = len(final_results)
    offset = (page - 1) * page_size
    page_results = final_results[offset : offset + page_size]

    serializer = SimilarIdeaSerializer(page_results, many=True)

    next_page = page + 1 if offset + page_size < total_count else None
    previous_page = page - 1 if page > 1 else None

    return Response(
        {
            "results": serializer.data,
            "count": total_count,
            "next": next_page,
            "previous": previous_page,
        }
    )


def _publish_event(event_type: str, payload: dict) -> None:
    """Lazy-import wrapper to avoid module-collection ordering issues in tests."""
    from events.publisher import publish_event

    publish_event(event_type, payload)


def _publish_notification(**kwargs) -> None:
    """Lazy-import wrapper for notification events."""
    from events.publisher import publish_notification_event

    publish_notification_event(**kwargs)


def _broadcast_ws_event(group_name: str, event_type: str, payload: dict) -> None:
    """Broadcast a WebSocket event to a channel group."""
    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                group_name,
                {"type": event_type, "payload": payload},
            )
    except Exception:
        logger.exception("Failed to broadcast WS event %s to %s", event_type, group_name)


def _get_idea_or_404(idea_id: str):
    """Validate UUID and return Idea or a 404 Response."""
    try:
        uuid.UUID(idea_id)
    except ValueError:
        return None, Response(
            {"error": "NOT_FOUND", "message": "Idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    try:
        idea = Idea.objects.get(id=idea_id)
    except Idea.DoesNotExist:
        return None, Response(
            {"error": "NOT_FOUND", "message": "Idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    return idea, None


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def create_merge_request(request: Request, idea_id: str) -> Response:
    """POST /api/ideas/:id/merge-request — Create a merge request."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    requesting_idea, err = _get_idea_or_404(idea_id)
    if err:
        return err

    # Only the idea owner can create a merge request
    if requesting_idea.owner_id != user.id:
        return Response(
            {"error": "ACCESS_DENIED", "message": "Only the idea owner can create a merge request"},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = MergeRequestCreateSerializer(data=request.data)
    if not serializer.is_valid():
        # Surface INVALID_UUID for URL parsing failures
        errors = serializer.errors
        if "target_idea_url" in errors and errors["target_idea_url"] == ["INVALID_UUID"]:
            return Response(
                {"error": "INVALID_UUID", "message": "Could not extract a valid UUID from the URL"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    target_idea_id = serializer.validated_data["target_idea_id"]
    is_manual = serializer.validated_data.get("_manual_request", False)

    # Validate target UUID format
    try:
        uuid.UUID(str(target_idea_id))
    except ValueError:
        return Response(
            {"error": "INVALID_UUID", "message": "Malformed UUID"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate target idea exists
    try:
        target_idea = Idea.objects.get(id=target_idea_id, deleted_at__isnull=True)
    except Idea.DoesNotExist:
        return Response(
            {"error": "TARGET_NOT_FOUND", "message": "Target idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Cannot merge with self
    if requesting_idea.id == target_idea.id:
        return Response(
            {"error": "CANNOT_MERGE_SELF", "message": "Cannot create merge request with the same idea"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate target state
    if target_idea.state not in ("open", "in_review", "rejected"):
        return Response(
            {"error": "INVALID_STATE", "message": "Target idea is in an incompatible state"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    from apps.similarity.models import MergeRequest as MergeRequestModel

    # Check for existing active merge request for this pair (either direction)
    existing = MergeRequestModel.objects.filter(
        status="pending",
    ).filter(
        Q(requesting_idea_id=requesting_idea.id, target_idea_id=target_idea.id)
        | Q(requesting_idea_id=target_idea.id, target_idea_id=requesting_idea.id)
    ).exists()

    if existing:
        return Response(
            {"error": "BAD_REQUEST", "message": "A merge request already exists for this pair"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Auto-detect merge_type based on target state
    from apps.review.models import ReviewAssignment

    if target_idea.state == "in_review":
        merge_type = "append"
        # Append requires at least one active reviewer assignment
        active_reviewers = ReviewAssignment.objects.filter(
            idea_id=target_idea.id, unassigned_at__isnull=True
        )
        if not active_reviewers.exists():
            return Response(
                {"error": "REVIEWER_REQUIRED", "message": "Target idea has no assigned reviewers"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        reviewer_consent = "pending"
        reviewer_ids = list(active_reviewers.values_list("reviewer_id", flat=True))
    else:
        merge_type = "merge"
        reviewer_consent = "not_required"
        reviewer_ids = []

    merge_request = MergeRequestModel.objects.create(
        requesting_idea_id=requesting_idea.id,
        target_idea_id=target_idea.id,
        merge_type=merge_type,
        requested_by=user.id,
        status="pending",
        requesting_owner_consent="accepted",
        target_owner_consent="pending",
        reviewer_consent=reviewer_consent,
        manual_request=is_manual,
    )

    # Publish event based on merge type
    if merge_type == "append":
        event_type = "notification.similarity.append_request_created"
        payload = {
            "merge_request_id": str(merge_request.id),
            "requesting_idea_id": str(requesting_idea.id),
            "target_idea_id": str(target_idea.id),
            "requesting_owner_id": str(requesting_idea.owner_id),
            "target_owner_id": str(target_idea.owner_id),
            "reviewer_ids": [str(rid) for rid in reviewer_ids],
        }
    else:
        event_type = "notification.similarity.merge_request_created"
        payload = {
            "merge_request_id": str(merge_request.id),
            "requesting_idea_id": str(requesting_idea.id),
            "target_idea_id": str(target_idea.id),
            "requesting_owner_id": str(requesting_idea.owner_id),
            "target_owner_id": str(target_idea.owner_id),
        }
    _publish_event(event_type, payload)

    # Broadcast WebSocket event to target idea group
    _broadcast_ws_event(
        f"idea_{target_idea.id}",
        "merge_request",
        {
            "merge_request_id": str(merge_request.id),
            "merge_type": merge_type,
            "requesting_idea_id": str(requesting_idea.id),
            "target_idea_id": str(target_idea.id),
            "status": "pending",
        },
    )

    result = MergeRequestSerializer(merge_request).data
    return Response(result, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def consent_merge_request(request: Request, merge_request_id: str) -> Response:
    """POST /api/merge-requests/:id/consent — Accept or decline a merge request."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        uuid.UUID(merge_request_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Merge request not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    from apps.similarity.models import MergeRequest as MergeRequestModel

    try:
        merge_request = MergeRequestModel.objects.get(id=merge_request_id)
    except MergeRequestModel.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Merge request not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if merge_request.status != "pending":
        return Response(
            {"error": "BAD_REQUEST", "message": "Merge request is not pending"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Only target idea owner can consent
    try:
        target_idea = Idea.objects.get(id=merge_request.target_idea_id)
    except Idea.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Target idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Determine if user is target owner or assigned reviewer
    is_target_owner = target_idea.owner_id == user.id

    from apps.review.models import ReviewAssignment

    is_reviewer = ReviewAssignment.objects.filter(
        idea_id=target_idea.id, reviewer_id=user.id, unassigned_at__isnull=True
    ).exists()

    if not (is_target_owner or (is_reviewer and merge_request.merge_type == "append")):
        return Response(
            {"error": "FORBIDDEN", "message": "Only the target idea owner or assigned reviewer can consent"},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = MergeRequestConsentSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    consent = serializer.validated_data["consent"]

    if consent == "accept":
        if is_target_owner:
            merge_request.target_owner_consent = "accepted"
        if is_reviewer and merge_request.merge_type == "append":
            merge_request.reviewer_consent = "accepted"

        # Check if all required consents are in
        all_accepted = (
            merge_request.requesting_owner_consent == "accepted"
            and merge_request.target_owner_consent == "accepted"
        )
        if merge_request.merge_type == "append":
            all_accepted = all_accepted and merge_request.reviewer_consent == "accepted"

        if all_accepted:
            merge_request.status = "accepted"
            merge_request.resolved_at = timezone.now()
        merge_request.save()

        if merge_request.status == "accepted":
            if merge_request.merge_type == "append":
                _publish_event(
                    "notification.similarity.append_accepted",
                    {
                        "merge_request_id": str(merge_request.id),
                        "requesting_idea_id": str(merge_request.requesting_idea_id),
                        "target_idea_id": str(merge_request.target_idea_id),
                    },
                )
            else:
                _publish_event(
                    "notification.similarity.merge_request_accepted",
                    {
                        "merge_request_id": str(merge_request.id),
                        "requesting_idea_id": str(merge_request.requesting_idea_id),
                        "target_idea_id": str(merge_request.target_idea_id),
                    },
                )
    else:
        merge_request.status = "declined"
        merge_request.resolved_at = timezone.now()
        if is_target_owner:
            merge_request.target_owner_consent = "declined"
        if is_reviewer and merge_request.merge_type == "append":
            merge_request.reviewer_consent = "declined"
        merge_request.save()

        if merge_request.merge_type == "append":
            _publish_event(
                "notification.similarity.append_declined",
                {
                    "merge_request_id": str(merge_request.id),
                    "requesting_idea_id": str(merge_request.requesting_idea_id),
                    "target_idea_id": str(merge_request.target_idea_id),
                },
            )
        else:
            _publish_event(
                "notification.similarity.merge_request_declined",
                {
                    "merge_request_id": str(merge_request.id),
                    "requesting_idea_id": str(merge_request.requesting_idea_id),
                    "target_idea_id": str(merge_request.target_idea_id),
                },
            )

    # Broadcast WebSocket event for merge request status change
    ws_payload = {
        "merge_request_id": str(merge_request.id),
        "merge_type": merge_request.merge_type,
        "requesting_idea_id": str(merge_request.requesting_idea_id),
        "target_idea_id": str(merge_request.target_idea_id),
        "status": merge_request.status,
    }
    # Notify both idea groups
    _broadcast_ws_event(
        f"idea_{merge_request.requesting_idea_id}",
        "merge_request",
        ws_payload,
    )
    _broadcast_ws_event(
        f"idea_{merge_request.target_idea_id}",
        "merge_request",
        ws_payload,
    )

    result = MergeRequestSerializer(merge_request).data
    return Response(result, status=status.HTTP_200_OK)
