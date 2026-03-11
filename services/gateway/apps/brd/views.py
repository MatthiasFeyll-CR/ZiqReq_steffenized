import uuid

from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response

from apps.ideas.authentication import MiddlewareAuthentication
from apps.ideas.models import Idea, IdeaCollaborator

from .models import BrdDraft
from .serializers import (
    SECTION_FIELDS,
    SECTION_LOCK_KEYS,
    BrdDraftPatchSerializer,
    BrdDraftResponseSerializer,
)


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


def _get_idea_or_error(idea_id: str):
    """Validate idea_id UUID and return (idea, None) or (None, error_response)."""
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


def _check_access(user, idea) -> Response | None:
    """Return 403 response if user lacks access, or None if access is granted."""
    is_owner = idea.owner_id == user.id
    is_co_owner = idea.co_owner_id == user.id
    is_collaborator = IdeaCollaborator.objects.filter(
        idea_id=idea.id, user_id=user.id
    ).exists()

    if not (is_owner or is_co_owner or is_collaborator):
        return Response(
            {"error": "ACCESS_DENIED", "message": "You do not have access to this idea"},
            status=status.HTTP_403_FORBIDDEN,
        )
    return None


@api_view(["GET", "PATCH"])
@authentication_classes([MiddlewareAuthentication])
def brd_draft(request: Request, idea_id: str) -> Response:
    """Route /api/ideas/:id/brd — GET returns draft, PATCH updates it."""
    if request.method == "PATCH":
        return _patch_brd_draft(request, idea_id)
    return _get_brd_draft(request, idea_id)


def _get_brd_draft(request: Request, idea_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    idea, error = _get_idea_or_error(idea_id)
    if error:
        return error

    access_error = _check_access(user, idea)
    if access_error:
        return access_error

    # Get or create empty draft
    draft, _created = BrdDraft.objects.get_or_create(
        idea_id=idea.id,
        defaults={
            "section_locks": {},
            "allow_information_gaps": False,
            "readiness_evaluation": {},
        },
    )

    serializer = BrdDraftResponseSerializer(draft)
    return Response(serializer.data)


def _patch_brd_draft(request: Request, idea_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    idea, error = _get_idea_or_error(idea_id)
    if error:
        return error

    access_error = _check_access(user, idea)
    if access_error:
        return access_error

    serializer = BrdDraftPatchSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Get or create draft
    draft, _created = BrdDraft.objects.get_or_create(
        idea_id=idea.id,
        defaults={
            "section_locks": {},
            "allow_information_gaps": False,
            "readiness_evaluation": {},
        },
    )

    validated = serializer.validated_data
    update_fields = ["updated_at"]

    # Apply section_locks if explicitly provided
    if "section_locks" in validated:
        current_locks = draft.section_locks or {}
        current_locks.update(validated["section_locks"])
        draft.section_locks = current_locks
        update_fields.append("section_locks")

    # Apply allow_information_gaps if provided
    if "allow_information_gaps" in validated:
        draft.allow_information_gaps = validated["allow_information_gaps"]
        update_fields.append("allow_information_gaps")

    # Apply section content updates + auto-lock on edit
    for field in SECTION_FIELDS:
        if field in validated:
            setattr(draft, field, validated[field])
            update_fields.append(field)

            # Auto-lock: when a section is manually edited, lock it
            lock_key = SECTION_LOCK_KEYS[field]
            current_locks = draft.section_locks or {}
            current_locks[lock_key] = True
            draft.section_locks = current_locks
            if "section_locks" not in update_fields:
                update_fields.append("section_locks")

    draft.save(update_fields=update_fields)

    response_serializer = BrdDraftResponseSerializer(draft)
    return Response(response_serializer.data)
