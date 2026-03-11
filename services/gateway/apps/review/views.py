import logging
import uuid

from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response

from apps.brd.models import BrdDraft
from apps.ideas.authentication import MiddlewareAuthentication
from apps.ideas.models import Idea

from .models import BrdVersion, ReviewAssignment, ReviewTimelineEntry
from .serializers import ReviewActionCommentSerializer, SubmitIdeaSerializer

logger = logging.getLogger(__name__)

def _create_pdf_client():
    """Create a PdfClient instance (lazy import to avoid namespace collisions)."""
    from grpc_clients.pdf_client import PdfClient

    return PdfClient()


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


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def submit_idea(request: Request, idea_id: str) -> Response:
    """POST /api/ideas/:id/submit — Submit idea for review."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    idea, error = _get_idea_or_error(idea_id)
    if error:
        return error

    # Access control: only owner or co-owner
    if idea.owner_id != user.id and idea.co_owner_id != user.id:
        return Response(
            {"error": "ACCESS_DENIED", "message": "Only owner or co-owner can submit"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # State validation: only 'open' and 'rejected' ideas can be submitted
    if idea.state not in ("open", "rejected"):
        return Response(
            {"error": "INVALID_STATE", "message": "Only open or rejected ideas can be submitted for review"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = SubmitIdeaSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    validated = serializer.validated_data
    message = validated.get("message", "")
    reviewer_ids = validated.get("reviewer_ids", [])

    # Get BRD draft for snapshot
    try:
        draft = BrdDraft.objects.get(idea_id=idea.id)
    except BrdDraft.DoesNotExist:
        draft = None

    # Calculate next version number
    max_version = BrdVersion.objects.filter(idea_id=idea.id).aggregate(
        max_v=Max("version_number")
    )["max_v"]
    next_version = (max_version or 0) + 1

    # Generate PDF
    try:
        pdf_client = _create_pdf_client()
        sections = {}
        if draft:
            sections = {
                "title": draft.section_title or "",
                "short_description": draft.section_short_description or "",
                "current_workflow": draft.section_current_workflow or "",
                "affected_department": draft.section_affected_department or "",
                "core_capabilities": draft.section_core_capabilities or "",
                "success_criteria": draft.section_success_criteria or "",
            }
        pdf_client.generate_pdf(
            idea_id=str(idea.id),
            idea_title=idea.title or "",
            sections=sections,
        )
    except Exception:
        logger.exception("PDF generation failed for idea %s", idea_id)
        return Response(
            {"error": "PDF_GENERATION_FAILED", "message": "PDF generation service is unavailable"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    # Store PDF
    pdf_file_path = f"ideas/{idea.id}/brd/v{next_version}.pdf"

    old_state = idea.state

    # Check if this is a resubmission (previous version exists)
    previous_version = BrdVersion.objects.filter(idea_id=idea.id).order_by("-version_number").first()

    # Atomic transaction for all writes
    with transaction.atomic():
        # 1. Create immutable BRD version
        brd_version = BrdVersion.objects.create(
            idea_id=idea.id,
            version_number=next_version,
            section_title=draft.section_title if draft else None,
            section_short_description=draft.section_short_description if draft else None,
            section_current_workflow=draft.section_current_workflow if draft else None,
            section_affected_department=draft.section_affected_department if draft else None,
            section_core_capabilities=draft.section_core_capabilities if draft else None,
            section_success_criteria=draft.section_success_criteria if draft else None,
            pdf_file_path=pdf_file_path,
        )

        # 2. Update idea state
        idea.state = "in_review"
        idea.save(update_fields=["state", "updated_at"])

        # 3. Create reviewer assignments
        for reviewer_id in reviewer_ids:
            ReviewAssignment.objects.create(
                idea_id=idea.id,
                reviewer_id=reviewer_id,
                assigned_by="submitter",
            )

        # 4. Create state_change timeline entry
        ReviewTimelineEntry.objects.create(
            idea_id=idea.id,
            entry_type="state_change",
            author_id=user.id,
            content="Submitted for review",
            old_state=old_state,
            new_state="in_review",
        )

        # 5. Create comment timeline entry (if message provided)
        if message:
            ReviewTimelineEntry.objects.create(
                idea_id=idea.id,
                entry_type="comment",
                author_id=user.id,
                content=message,
            )

        # 6. Create resubmission timeline entry (if previous version exists)
        if previous_version:
            ReviewTimelineEntry.objects.create(
                idea_id=idea.id,
                entry_type="resubmission",
                author_id=user.id,
                old_version_id=previous_version.id,
                new_version_id=brd_version.id,
            )

    pdf_url = f"/api/ideas/{idea.id}/brd/versions/{next_version}/pdf"

    return Response({
        "version_number": next_version,
        "pdf_url": pdf_url,
        "state": "in_review",
    })


def _require_reviewer(user) -> Response | None:
    """Return an error response if user does not have the 'reviewer' role, else None."""
    roles = getattr(user, "roles", None) or []
    if "reviewer" not in roles:
        return Response(
            {"error": "FORBIDDEN", "message": "Reviewer role required"},
            status=status.HTTP_403_FORBIDDEN,
        )
    return None


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def assign_review(request: Request, idea_id: str) -> Response:
    """POST /api/reviews/:id/assign — Self-assign as reviewer."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    role_error = _require_reviewer(user)
    if role_error:
        return role_error

    idea, error = _get_idea_or_error(idea_id)
    if error:
        return error

    # State validation: only 'in_review' ideas can be assigned
    if idea.state != "in_review":
        return Response(
            {"error": "INVALID_STATE", "message": "Only ideas in review can be assigned"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Conflict of interest: reviewer cannot assign to own idea
    if user.id == idea.owner_id or user.id == idea.co_owner_id:
        return Response(
            {"error": "CONFLICT_OF_INTEREST", "message": "Cannot review your own idea"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Duplicate check: active assignment (unassigned_at IS NULL)
    if ReviewAssignment.objects.filter(
        idea_id=idea.id, reviewer_id=user.id, unassigned_at__isnull=True
    ).exists():
        return Response(
            {"error": "ALREADY_ASSIGNED", "message": "Already assigned to this idea"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    ReviewAssignment.objects.create(
        idea_id=idea.id,
        reviewer_id=user.id,
        assigned_by="self",
    )

    return Response({"message": "Assigned successfully"})


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def unassign_review(request: Request, idea_id: str) -> Response:
    """POST /api/reviews/:id/unassign — Self-unassign as reviewer."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    role_error = _require_reviewer(user)
    if role_error:
        return role_error

    idea, error = _get_idea_or_error(idea_id)
    if error:
        return error

    # Find active assignment
    try:
        assignment = ReviewAssignment.objects.get(
            idea_id=idea.id, reviewer_id=user.id, unassigned_at__isnull=True
        )
    except ReviewAssignment.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "No active assignment found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    assignment.unassigned_at = timezone.now()
    assignment.save(update_fields=["unassigned_at"])

    return Response({"message": "Unassigned successfully"})


# --- State transition maps for review actions ---

# Valid source states for each action
_REVIEW_ACTION_VALID_STATES: dict[str, list[str]] = {
    "accept": ["in_review"],
    "reject": ["in_review"],
    "drop": ["in_review"],
    "undo": ["accepted", "dropped", "rejected"],
}

# Target state for each action
_REVIEW_ACTION_TARGET_STATE: dict[str, str] = {
    "accept": "accepted",
    "reject": "rejected",
    "drop": "dropped",
    "undo": "in_review",
}

# Actions that require a mandatory comment
_COMMENT_REQUIRED_ACTIONS = {"reject", "drop", "undo"}


def _handle_review_action(request: Request, idea_id: str, action: str) -> Response:
    """Shared logic for accept/reject/drop/undo review actions."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    role_error = _require_reviewer(user)
    if role_error:
        return role_error

    idea, error = _get_idea_or_error(idea_id)
    if error:
        return error

    # State validation
    valid_states = _REVIEW_ACTION_VALID_STATES[action]
    if idea.state not in valid_states:
        return Response(
            {"error": "INVALID_STATE", "message": f"Cannot {action} idea in state '{idea.state}'"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Comment validation for actions that require it
    comment = None
    if action in _COMMENT_REQUIRED_ACTIONS:
        serializer = ReviewActionCommentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "COMMENT_REQUIRED", "message": "A comment is required for this action"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        comment = serializer.validated_data["comment"]

    old_state = idea.state
    new_state = _REVIEW_ACTION_TARGET_STATE[action]

    with transaction.atomic():
        idea.state = new_state
        idea.save(update_fields=["state", "updated_at"])

        content = comment or f"Idea {action}ed"
        ReviewTimelineEntry.objects.create(
            idea_id=idea.id,
            entry_type="state_change",
            author_id=user.id,
            content=content,
            old_state=old_state,
            new_state=new_state,
        )

    return Response({"state": new_state})


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def accept_review(request: Request, idea_id: str) -> Response:
    """POST /api/ideas/:id/review/accept — Reviewer accepts idea."""
    return _handle_review_action(request, idea_id, "accept")


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def reject_review(request: Request, idea_id: str) -> Response:
    """POST /api/ideas/:id/review/reject — Reviewer rejects idea."""
    return _handle_review_action(request, idea_id, "reject")


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def drop_review(request: Request, idea_id: str) -> Response:
    """POST /api/ideas/:id/review/drop — Reviewer drops idea."""
    return _handle_review_action(request, idea_id, "drop")


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def undo_review(request: Request, idea_id: str) -> Response:
    """POST /api/ideas/:id/review/undo — Undo review action."""
    return _handle_review_action(request, idea_id, "undo")
