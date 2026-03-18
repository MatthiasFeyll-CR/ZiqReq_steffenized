import logging
import uuid

from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response

from apps.authentication.models import User
from apps.projects.authentication import MiddlewareAuthentication
from apps.projects.models import Attachment, Project
from apps.requirements_document.models import BrdDraft

from .models import BrdVersion, ReviewAssignment, ReviewTimelineEntry
from .serializers import ReviewActionCommentSerializer, SubmitProjectSerializer, TimelineCommentSerializer

logger = logging.getLogger(__name__)


def _publish_notification(**kwargs) -> None:
    """Lazy-import wrapper to avoid module-collection ordering issues in tests."""
    from events.publisher import publish_notification_event

    publish_notification_event(**kwargs)


def _create_pdf_client():
    """Create a PdfClient instance (lazy import to avoid namespace collisions)."""
    from grpc_clients.pdf_client import PdfClient

    return PdfClient()


def _get_storage_backend():
    from storage.factory import get_storage_backend

    return get_storage_backend()


def _fetch_attachment_files(project_id, attachment_ids: list) -> list[dict]:
    """Fetch attachment file data from storage for the given IDs."""
    if not attachment_ids:
        return []

    valid_ids = []
    for aid in attachment_ids:
        try:
            uuid.UUID(str(aid))
            valid_ids.append(aid)
        except ValueError:
            logger.warning("Invalid attachment UUID skipped: %s", aid)
            continue

    if not valid_ids:
        return []

    attachments = Attachment.objects.filter(
        id__in=valid_ids,
        project_id=project_id,
        deleted_at__isnull=True,
    )

    backend = _get_storage_backend()
    result = []
    for att in attachments:
        try:
            file_data, _ = backend.download_file(att.storage_key)
            result.append({
                "filename": att.filename,
                "content_type": att.content_type,
                "file_data": file_data,
            })
        except Exception:
            logger.warning("Failed to download attachment %s for PDF merge", att.id)
    return result


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


def _get_project_or_error(project_id: str):
    """Validate project_id UUID and return (project, None) or (None, error_response)."""
    try:
        uuid.UUID(project_id)
    except ValueError:
        return None, Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return None, Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    return project, None


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def submit_project(request: Request, project_id: str) -> Response:
    """POST /api/projects/:id/submit — Submit project for review."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    project, error = _get_project_or_error(project_id)
    if error:
        return error

    # Access control: only owner
    if project.owner_id != user.id:
        return Response(
            {"error": "ACCESS_DENIED", "message": "Only owner can submit"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # State validation: only 'open' and 'rejected' projects can be submitted
    if project.state not in ("open", "rejected"):
        return Response(
            {"error": "INVALID_STATE", "message": "Only open or rejected projects can be submitted for review"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = SubmitProjectSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    validated = serializer.validated_data
    message = validated.get("message", "")
    reviewer_ids = validated.get("reviewer_ids", [])
    attachment_ids = validated.get("attachment_ids", [])
    if len(attachment_ids) > 10:
        return Response(
            {"error": "VALIDATION_ERROR", "message": "Maximum 10 attachments per PDF"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Get BRD draft for snapshot
    try:
        draft = BrdDraft.objects.get(project_id=project.id)
    except BrdDraft.DoesNotExist:
        draft = None

    # Calculate next version number
    max_version = BrdVersion.objects.filter(project_id=project.id).aggregate(
        max_v=Max("version_number")
    )["max_v"]
    next_version = (max_version or 0) + 1

    # Fetch attachment files for PDF merge
    pdf_attachments = _fetch_attachment_files(project.id, attachment_ids)

    # Generate PDF
    try:
        import json as _json

        pdf_client = _create_pdf_client()
        structure_json = "[]"
        title = project.title or ""
        short_description = ""
        if draft:
            structure_json = _json.dumps(draft.structure) if draft.structure else "[]"
            title = draft.title or project.title or ""
            short_description = draft.short_description or ""
        pdf_client.generate_pdf(
            project_id=str(project.id),
            project_type=getattr(project, "project_type", "software"),
            title=title,
            short_description=short_description,
            structure_json=structure_json,
            attachments=pdf_attachments if pdf_attachments else None,
        )
    except Exception:
        logger.exception("PDF generation failed for project %s", project_id)
        return Response(
            {"error": "PDF_GENERATION_FAILED", "message": "PDF generation service is unavailable"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    # Store PDF
    pdf_file_path = f"projects/{project.id}/brd/v{next_version}.pdf"

    old_state = project.state

    # Check if this is a resubmission (previous version exists)
    previous_version = BrdVersion.objects.filter(project_id=project.id).order_by("-version_number").first()

    # Atomic transaction for all writes
    with transaction.atomic():
        # 1. Create immutable BRD version
        brd_version = BrdVersion.objects.create(
            project_id=project.id,
            version_number=next_version,
            title=draft.title if draft else None,
            short_description=draft.short_description if draft else None,
            structure=draft.structure if draft else [],
            pdf_file_path=pdf_file_path,
        )

        # 2. Update project state
        project.state = "in_review"
        project.save(update_fields=["state", "updated_at"])

        # 3. Create reviewer assignments
        for reviewer_id in reviewer_ids:
            ReviewAssignment.objects.create(
                project_id=project.id,
                reviewer_id=reviewer_id,
                assigned_by="submitter",
            )

        # 4. Create state_change timeline entry
        ReviewTimelineEntry.objects.create(
            project_id=project.id,
            entry_type="state_change",
            author_id=user.id,
            content="Submitted for review",
            old_state=old_state,
            new_state="in_review",
        )

        # 5. Create comment timeline entry (if message provided)
        if message:
            ReviewTimelineEntry.objects.create(
                project_id=project.id,
                entry_type="comment",
                author_id=user.id,
                content=message,
            )

        # 6. Create resubmission timeline entry (if previous version exists)
        if previous_version:
            ReviewTimelineEntry.objects.create(
                project_id=project.id,
                entry_type="resubmission",
                author_id=user.id,
                old_version_id=previous_version.id,
                new_version_id=brd_version.id,
            )

    pdf_url = f"/api/projects/{project.id}/brd/versions/{next_version}/pdf"

    # System event for comment timeline
    try:
        from apps.comments.system_events import on_state_changed
        on_state_changed(str(project.id), old_state, "in_review")
    except Exception:
        logger.exception("Failed to create state_changed system event on submit")

    # Notify assigned reviewers about submission
    for reviewer_id in reviewer_ids:
        _publish_notification(
            routing_key="notification.review.submitted",
            user_id=str(reviewer_id),
            event_type="project_submitted",
            title="Project Submitted for Review",
            body=f'"{project.title}" was submitted for review by {user.display_name}',
            reference_id=str(project.id),
            reference_type="project",
        )

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
def assign_review(request: Request, project_id: str) -> Response:
    """POST /api/reviews/:id/assign — Self-assign as reviewer."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    role_error = _require_reviewer(user)
    if role_error:
        return role_error

    project, error = _get_project_or_error(project_id)
    if error:
        return error

    # State validation: only 'in_review' projects can be assigned
    if project.state != "in_review":
        return Response(
            {"error": "INVALID_STATE", "message": "Only projects in review can be assigned"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Conflict of interest: reviewer cannot assign to own project
    if user.id == project.owner_id:
        return Response(
            {"error": "CONFLICT_OF_INTEREST", "message": "Cannot review your own project"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Duplicate check: active assignment (unassigned_at IS NULL)
    if ReviewAssignment.objects.filter(
        project_id=project.id, reviewer_id=user.id, unassigned_at__isnull=True
    ).exists():
        return Response(
            {"error": "ALREADY_ASSIGNED", "message": "Already assigned to this project"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    ReviewAssignment.objects.create(
        project_id=project.id,
        reviewer_id=user.id,
        assigned_by="self",
    )

    return Response({"message": "Assigned successfully"})


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def unassign_review(request: Request, project_id: str) -> Response:
    """POST /api/reviews/:id/unassign — Self-unassign as reviewer."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    role_error = _require_reviewer(user)
    if role_error:
        return role_error

    project, error = _get_project_or_error(project_id)
    if error:
        return error

    # Find active assignment
    try:
        assignment = ReviewAssignment.objects.get(
            project_id=project.id, reviewer_id=user.id, unassigned_at__isnull=True
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


def _handle_review_action(request: Request, project_id: str, action: str) -> Response:
    """Shared logic for accept/reject/drop/undo review actions."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    role_error = _require_reviewer(user)
    if role_error:
        return role_error

    project, error = _get_project_or_error(project_id)
    if error:
        return error

    # State validation
    valid_states = _REVIEW_ACTION_VALID_STATES[action]
    if project.state not in valid_states:
        return Response(
            {"error": "INVALID_STATE", "message": f"Cannot {action} project in state '{project.state}'"},
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

    old_state = project.state
    new_state = _REVIEW_ACTION_TARGET_STATE[action]

    with transaction.atomic():
        project.state = new_state
        project.save(update_fields=["state", "updated_at"])

        content = comment or f"Project {action}ed"
        ReviewTimelineEntry.objects.create(
            project_id=project.id,
            entry_type="state_change",
            author_id=user.id,
            content=content,
            old_state=old_state,
            new_state=new_state,
        )

    # System event for comment timeline
    try:
        from apps.comments.system_events import on_state_changed
        on_state_changed(str(project.id), old_state, new_state)
    except Exception:
        logger.exception("Failed to create state_changed system event")

    # Notify project owner of state change
    _publish_notification(
        routing_key="notification.review.state_changed",
        user_id=str(project.owner_id),
        event_type="review_state_changed",
        title=f"Project {action.capitalize()}ed",
        body=f'"{project.title}" was {action}ed by {user.display_name}',
        reference_id=str(project.id),
        reference_type="project",
    )
    return Response({"state": new_state})


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def accept_review(request: Request, project_id: str) -> Response:
    """POST /api/projects/:id/review/accept — Reviewer accepts project."""
    return _handle_review_action(request, project_id, "accept")


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def reject_review(request: Request, project_id: str) -> Response:
    """POST /api/projects/:id/review/reject — Reviewer rejects project."""
    return _handle_review_action(request, project_id, "reject")


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def drop_review(request: Request, project_id: str) -> Response:
    """POST /api/projects/:id/review/drop — Reviewer drops project."""
    return _handle_review_action(request, project_id, "drop")


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def undo_review(request: Request, project_id: str) -> Response:
    """POST /api/projects/:id/review/undo — Undo review action."""
    return _handle_review_action(request, project_id, "undo")


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def list_reviews(request: Request) -> Response:
    """GET /api/reviews — Categorized review lists for Reviewer role."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    role_error = _require_reviewer(user)
    if role_error:
        return role_error

    # Fetch all non-open projects (open projects are not in review workflow)
    projects = list(
        Project.objects.filter(
            state__in=["in_review", "accepted", "rejected", "dropped"],
            deleted_at__isnull=True,
        )
    )

    # Batch-load active assignments for all projects
    project_ids = [i.id for i in projects]
    active_assignments = ReviewAssignment.objects.filter(
        project_id__in=project_ids, unassigned_at__isnull=True
    )

    # Build assignment map: project_id -> list of reviewer_ids
    assignments_by_project: dict[uuid.UUID, list[uuid.UUID]] = {}
    for a in active_assignments:
        assignments_by_project.setdefault(a.project_id, []).append(a.reviewer_id)

    # Batch-load owner and reviewer user info
    all_user_ids: set[uuid.UUID] = {i.owner_id for i in projects}
    for reviewer_ids in assignments_by_project.values():
        all_user_ids.update(reviewer_ids)
    users_map: dict[uuid.UUID, User] = {}
    if all_user_ids:
        users_map = {u.id: u for u in User.objects.filter(id__in=all_user_ids)}

    # Categorize projects
    assigned_to_me: list[dict] = []
    unassigned: list[dict] = []
    accepted: list[dict] = []
    rejected: list[dict] = []
    dropped: list[dict] = []

    for project in projects:
        project_reviewers = assignments_by_project.get(project.id, [])
        reviewer_info = [
            {"id": str(rid), "display_name": users_map[rid].display_name}
            for rid in project_reviewers
            if rid in users_map
        ]
        owner = users_map.get(project.owner_id)
        item = {
            "id": str(project.id),
            "title": project.title,
            "state": project.state,
            "owner_id": str(project.owner_id),
            "owner_name": owner.display_name if owner else "",
            "submitted_at": project.updated_at.isoformat() if project.updated_at else None,
            "reviewers": reviewer_info,
        }

        if project.state == "in_review":
            if user.id in project_reviewers:
                assigned_to_me.append(item)
            elif not project_reviewers:
                unassigned.append(item)
        elif project.state == "accepted":
            accepted.append(item)
        elif project.state == "rejected":
            rejected.append(item)
        elif project.state == "dropped":
            dropped.append(item)

    return Response({
        "assigned_to_me": assigned_to_me,
        "unassigned": unassigned,
        "accepted": accepted,
        "rejected": rejected,
        "dropped": dropped,
    })


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def get_project_reviewers(request: Request, project_id: str) -> Response:
    """GET /api/projects/:id/review/reviewers — Get active reviewers for a project."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    project, error = _get_project_or_error(project_id)
    if error:
        return error

    assignments = ReviewAssignment.objects.filter(project_id=project.id, unassigned_at__isnull=True)
    reviewer_ids = [a.reviewer_id for a in assignments]
    users_map: dict[uuid.UUID, User] = {}
    if reviewer_ids:
        users_map = {u.id: u for u in User.objects.filter(id__in=reviewer_ids)}

    reviewers = [
        {"id": str(rid), "display_name": users_map[rid].display_name}
        for rid in reviewer_ids
        if rid in users_map
    ]
    return Response({"reviewers": reviewers})


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def list_reviewer_users(request: Request) -> Response:
    """GET /api/reviews/reviewers — List users with reviewer role."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    reviewers = User.objects.filter(roles__contains=["reviewer"]).order_by("display_name")
    data = [
        {"id": str(r.id), "display_name": r.display_name, "email": r.email}
        for r in reviewers
    ]
    return Response(data)


def _serialize_timeline_entry(entry: ReviewTimelineEntry, author_map: dict) -> dict:
    """Serialize a single timeline entry to dict."""
    author = None
    if entry.author_id and entry.author_id in author_map:
        u = author_map[entry.author_id]
        author = {"id": str(u.id), "display_name": u.display_name}

    return {
        "id": str(entry.id),
        "entry_type": entry.entry_type,
        "author": author,
        "content": entry.content,
        "parent_entry_id": str(entry.parent_entry_id) if entry.parent_entry_id else None,
        "old_state": entry.old_state,
        "new_state": entry.new_state,
        "old_version_id": str(entry.old_version_id) if entry.old_version_id else None,
        "new_version_id": str(entry.new_version_id) if entry.new_version_id else None,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
    }


@api_view(["GET", "POST"])
@authentication_classes([MiddlewareAuthentication])
def review_timeline(request: Request, project_id: str) -> Response:
    """GET/POST /api/projects/:id/review/timeline — Get or add timeline entries."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    project, error = _get_project_or_error(project_id)
    if error:
        return error

    if request.method == "GET":
        return _get_timeline(project)
    else:
        return _post_timeline_comment(request, project, user)


def _get_timeline(project: Project) -> Response:
    """Return chronological list of timeline entries for the project."""
    entries = ReviewTimelineEntry.objects.filter(project_id=project.id).order_by("created_at")

    # Batch-load authors
    author_ids = {e.author_id for e in entries if e.author_id}
    author_map = {}
    if author_ids:
        authors = User.objects.filter(id__in=author_ids)
        author_map = {u.id: u for u in authors}

    data = [_serialize_timeline_entry(e, author_map) for e in entries]
    return Response(data)


def _post_timeline_comment(request: Request, project: Project, user) -> Response:
    """Create a comment entry on the timeline."""
    serializer = TimelineCommentSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"error": "VALIDATION_ERROR", "message": "Content is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    content = serializer.validated_data["content"]
    parent_entry_id = serializer.validated_data.get("parent_entry_id")

    # Validate parent_entry_id if provided
    if parent_entry_id:
        try:
            ReviewTimelineEntry.objects.get(id=parent_entry_id, project_id=project.id)
        except ReviewTimelineEntry.DoesNotExist:
            return Response(
                {"error": "NOT_FOUND", "message": "Parent entry not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    entry = ReviewTimelineEntry.objects.create(
        project_id=project.id,
        entry_type="comment",
        author_id=user.id,
        content=content,
        parent_entry_id=parent_entry_id,
    )

    # Notify project owner of new review comment (unless they posted it)
    if project.owner_id != user.id:
        _publish_notification(
            routing_key="notification.review.comment",
            user_id=str(project.owner_id),
            event_type="review_comment",
            title="New Review Comment",
            body=f'{user.display_name} commented on "{project.title}"',
            reference_id=str(project.id),
            reference_type="project",
        )
    author_map = {user.id: user}
    data = _serialize_timeline_entry(entry, author_map)
    return Response(data, status=status.HTTP_201_CREATED)
