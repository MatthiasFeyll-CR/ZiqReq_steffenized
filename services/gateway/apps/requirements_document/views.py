import json
import logging
import os
import uuid

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response

from apps.projects.authentication import MiddlewareAuthentication
from apps.projects.models import Attachment, Project, ProjectCollaborator

from .models import RequirementsDocumentDraft
from .serializers import (
    RequirementsDocumentDraftPatchSerializer,
    RequirementsDocumentDraftResponseSerializer,
    RequirementsGenerateSerializer,
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


def _get_storage_backend():
    from storage.factory import get_storage_backend

    return get_storage_backend()


def _fetch_attachment_files(project_id, attachment_ids: list[str]) -> list[dict]:
    """Fetch attachment file data from storage for the given IDs.

    Returns list of dicts with filename, content_type, file_data.
    Skips attachments that are deleted, not found, or fail to download.
    """
    if not attachment_ids:
        return []

    valid_ids = []
    for aid in attachment_ids:
        try:
            uuid.UUID(aid)
            valid_ids.append(aid)
        except ValueError:
            logger.warning("Invalid attachment UUID skipped: %s", aid)
            continue

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


def _check_access(user, project) -> Response | None:
    """Return 403 response if user lacks access, or None if access is granted."""
    is_owner = project.owner_id == user.id
    is_collaborator = ProjectCollaborator.objects.filter(
        project_id=project.id, user_id=user.id
    ).exists()

    if not (is_owner or is_collaborator):
        return Response(
            {"error": "ACCESS_DENIED", "message": "You do not have access to this project"},
            status=status.HTTP_403_FORBIDDEN,
        )
    return None


@api_view(["GET", "PATCH"])
@authentication_classes([MiddlewareAuthentication])
def requirements_document_draft(request: Request, project_id: str) -> Response:
    """Route /api/projects/:id/requirements/ — GET returns draft, PATCH updates it."""
    if request.method == "PATCH":
        return _patch_requirements_draft(request, project_id)
    return _get_requirements_draft(request, project_id)


def _get_requirements_draft(request: Request, project_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    project, error = _get_project_or_error(project_id)
    if error:
        return error

    draft, _created = RequirementsDocumentDraft.objects.get_or_create(
        project_id=project.id,
        defaults={
            "item_locks": {},
            "allow_information_gaps": False,
            "readiness_evaluation": {},
        },
    )

    serializer = RequirementsDocumentDraftResponseSerializer(draft)
    return Response(serializer.data)


def _patch_requirements_draft(request: Request, project_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    project, error = _get_project_or_error(project_id)
    if error:
        return error

    access_error = _check_access(user, project)
    if access_error:
        return access_error

    serializer = RequirementsDocumentDraftPatchSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    draft, _created = RequirementsDocumentDraft.objects.get_or_create(
        project_id=project.id,
        defaults={
            "item_locks": {},
            "allow_information_gaps": False,
            "readiness_evaluation": {},
        },
    )

    validated = serializer.validated_data
    update_fields = ["updated_at"]

    if "item_locks" in validated:
        current_locks = draft.item_locks or {}
        current_locks.update(validated["item_locks"])
        draft.item_locks = current_locks
        update_fields.append("item_locks")

    if "allow_information_gaps" in validated:
        draft.allow_information_gaps = validated["allow_information_gaps"]
        update_fields.append("allow_information_gaps")

    if "title" in validated:
        draft.title = validated["title"]
        update_fields.append("title")

    if "short_description" in validated:
        draft.short_description = validated["short_description"]
        update_fields.append("short_description")

    draft.save(update_fields=update_fields)

    response_serializer = RequirementsDocumentDraftResponseSerializer(draft)
    return Response(response_serializer.data)


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def requirements_generate(request: Request, project_id: str) -> Response:
    """POST /api/projects/:id/requirements/generate — trigger async generation via AI gRPC."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    project, error = _get_project_or_error(project_id)
    if error:
        return error

    access_error = _check_access(user, project)
    if access_error:
        return access_error

    if project.state != "open":
        return Response(
            {
                "error": "INVALID_STATE",
                "message": "Requirements generation is only available for projects in 'open' state.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = RequirementsGenerateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    validated = serializer.validated_data
    mode = validated["mode"]

    try:
        ai_client = _create_ai_client()
        result = ai_client.trigger_brd_generation(
            project_id=str(project.id),
            mode=mode,
            section_name="",
        )
    except Exception:
        logger.exception("gRPC call to AI service failed for project %s", project_id)
        return Response(
            {"error": "SERVICE_UNAVAILABLE", "message": "AI service is currently unavailable."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            group_name = f"project_{project.id}"
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "requirements_generating",
                    "project_id": str(project.id),
                    "payload": {"project_id": str(project.id), "mode": mode},
                },
            )
    except Exception:
        logger.exception("Failed to broadcast requirements_generating for project %s", project_id)

    return Response(
        {
            "status": "accepted",
            "generation_id": result.get("generation_id", ""),
        },
        status=status.HTTP_202_ACCEPTED,
    )


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def requirements_preview_pdf(request: Request, project_id: str) -> Response | HttpResponse:
    """GET /api/projects/:id/requirements/pdf/preview — Generate PDF preview from current draft."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    project, error = _get_project_or_error(project_id)
    if error:
        return error

    access_error = _check_access(user, project)
    if access_error:
        return access_error

    try:
        draft = RequirementsDocumentDraft.objects.get(project_id=project.id)
    except RequirementsDocumentDraft.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "No requirements draft found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    has_content = bool(draft.title or draft.short_description or draft.structure)
    if not has_content:
        return Response(
            {"error": "NO_CONTENT", "message": "Requirements draft has no content to preview"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    structure_json = json.dumps(draft.structure) if draft.structure else "[]"

    # Fetch attachment files if requested (max 10)
    attachment_ids_param = request.query_params.get("attachment_ids", "")
    attachment_ids = [aid.strip() for aid in attachment_ids_param.split(",") if aid.strip()]
    if len(attachment_ids) > 10:
        return Response(
            {"error": "VALIDATION_ERROR", "message": "Maximum 10 attachments per PDF"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    attachments = _fetch_attachment_files(project.id, attachment_ids)

    try:
        pdf_client = _create_pdf_client()
        result = pdf_client.generate_pdf(
            project_id=str(project.id),
            project_type=getattr(project, "project_type", "software"),
            title=draft.title or project.title or "",
            short_description=draft.short_description or "",
            structure_json=structure_json,
            attachments=attachments if attachments else None,
        )
    except Exception:
        logger.exception("PDF preview generation failed for project %s", project_id)
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
        headers={"Content-Disposition": f'inline; filename="requirements-preview-{project.id}.pdf"'},
    )


# Keep old view names as aliases for backwards compat during transition
brd_draft = requirements_document_draft
brd_generate = requirements_generate
brd_preview_pdf = requirements_preview_pdf
