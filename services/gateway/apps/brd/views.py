import logging
import os
import uuid

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import FileResponse, HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response

from apps.ideas.authentication import MiddlewareAuthentication
from apps.ideas.models import Idea, IdeaCollaborator
from apps.review.models import BrdVersion

from .models import BrdDraft
from .serializers import (
    SECTION_FIELDS,
    SECTION_LOCK_KEYS,
    BrdDraftPatchSerializer,
    BrdDraftResponseSerializer,
    BrdGenerateSerializer,
)

logger = logging.getLogger(__name__)


def _create_ai_client():
    """Create an AiClient instance (lazy import to avoid namespace collisions)."""
    from grpc_clients.ai_client import AiClient

    address = os.environ.get("AI_GRPC_ADDRESS", "localhost:50052")
    return AiClient(address=address)


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

    # Any authenticated user can read BRD draft (read-only access)

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


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def brd_generate(request: Request, idea_id: str) -> Response:
    """POST /api/ideas/:id/brd/generate — trigger async BRD generation via AI gRPC."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    idea, error = _get_idea_or_error(idea_id)
    if error:
        return error

    access_error = _check_access(user, idea)
    if access_error:
        return access_error

    # Only open ideas can trigger BRD generation
    if idea.state != "open":
        return Response(
            {
                "error": "INVALID_STATE",
                "message": "BRD generation is only available for ideas in 'open' state.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = BrdGenerateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    validated = serializer.validated_data
    mode = validated["mode"]
    section_name = validated.get("section_name", "")

    # Invoke AI service via gRPC
    try:
        ai_client = _create_ai_client()
        result = ai_client.trigger_brd_generation(
            idea_id=str(idea.id),
            mode=mode,
            section_name=section_name,
        )
    except Exception:
        logger.exception("gRPC call to AI service failed for idea %s", idea_id)
        return Response(
            {"error": "SERVICE_UNAVAILABLE", "message": "AI service is currently unavailable."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    # Notify all connected clients that BRD generation has started
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            group_name = f"idea_{idea.id}"
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "brd_generating",
                    "idea_id": str(idea.id),
                    "payload": {"idea_id": str(idea.id), "mode": mode},
                },
            )
    except Exception:
        logger.exception("Failed to broadcast brd_generating for idea %s", idea_id)

    return Response(
        {
            "status": "accepted",
            "generation_id": result.get("generation_id", ""),
        },
        status=status.HTTP_202_ACCEPTED,
    )


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def brd_version_pdf(request: Request, idea_id: str, version: str) -> Response:
    """GET /api/ideas/:id/brd/versions/:version/pdf — Download BRD version PDF."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    idea, error = _get_idea_or_error(idea_id)
    if error:
        return error

    # Any authenticated user can download BRD PDF (read-only access)

    # Resolve "latest" to actual version number
    if version == "latest":
        brd_version = (
            BrdVersion.objects.filter(idea_id=idea.id)
            .order_by("-version_number")
            .first()
        )
    else:
        try:
            version_num = int(version)
        except ValueError:
            return Response(
                {"error": "NOT_FOUND", "message": "Invalid version"},
                status=status.HTTP_404_NOT_FOUND,
            )
        brd_version = BrdVersion.objects.filter(
            idea_id=idea.id, version_number=version_num
        ).first()

    if not brd_version:
        return Response(
            {"error": "NOT_FOUND", "message": "BRD version not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if not brd_version.pdf_file_path:
        return Response(
            {"error": "NOT_FOUND", "message": "PDF not available for this version"},
            status=status.HTTP_404_NOT_FOUND,
        )

    storage_root = os.environ.get("PDF_STORAGE_PATH", "/data/pdfs")
    full_path = os.path.join(storage_root, brd_version.pdf_file_path)

    if not os.path.isfile(full_path):
        return Response(
            {"error": "NOT_FOUND", "message": "PDF file not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    return FileResponse(
        open(full_path, "rb"),
        content_type="application/pdf",
        as_attachment=False,
        filename=f"brd-v{brd_version.version_number}.pdf",
    )


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def brd_preview_pdf(request: Request, idea_id: str) -> Response | HttpResponse:
    """GET /api/ideas/:id/brd/preview-pdf — Generate PDF preview from current draft."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    idea, error = _get_idea_or_error(idea_id)
    if error:
        return error

    try:
        draft = BrdDraft.objects.get(idea_id=idea.id)
    except BrdDraft.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "No BRD draft found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    has_content = any([
        draft.section_title,
        draft.section_short_description,
        draft.section_current_workflow,
        draft.section_affected_department,
        draft.section_core_capabilities,
        draft.section_success_criteria,
    ])
    if not has_content:
        return Response(
            {"error": "NO_CONTENT", "message": "BRD draft has no content to preview"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    sections = {
        "title": draft.section_title or "",
        "short_description": draft.section_short_description or "",
        "current_workflow": draft.section_current_workflow or "",
        "affected_department": draft.section_affected_department or "",
        "core_capabilities": draft.section_core_capabilities or "",
        "success_criteria": draft.section_success_criteria or "",
    }

    try:
        pdf_client = _create_pdf_client()
        result = pdf_client.generate_pdf(
            idea_id=str(idea.id),
            idea_title=idea.title or "",
            sections=sections,
        )
    except Exception:
        logger.exception("PDF preview generation failed for idea %s", idea_id)
        return Response(
            {"error": "PDF_GENERATION_FAILED", "message": "PDF generation service is unavailable"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    pdf_data = result.get("pdf_data", b"")
    if not pdf_data:
        return Response(
            {"error": "PDF_GENERATION_FAILED", "message": "PDF generation returned empty data"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return HttpResponse(
        pdf_data,
        content_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="brd-preview-{idea.id}.pdf"'},
    )
