import logging
import re
import uuid

from django.core.cache import cache
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response

from apps.projects.authentication import MiddlewareAuthentication
from apps.projects.models import Attachment, Project, ProjectCollaborator

from .serializers import AttachmentResponseSerializer

logger = logging.getLogger(__name__)

ALLOWED_CONTENT_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp",
    "application/pdf",
}
MAX_FILE_SIZE = 104857600  # 100MB
MAX_ATTACHMENTS_PER_PROJECT = 10
RATE_LIMIT_UPLOADS_PER_MINUTE = 10
PRESIGNED_URL_TTL = 900  # 15 minutes


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
    try:
        uuid.UUID(project_id)
    except ValueError:
        return None, Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    try:
        project = Project.objects.get(id=project_id, deleted_at__isnull=True)
    except Project.DoesNotExist:
        return None, Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    return project, None


def _check_access(user, project) -> bool:
    if project.owner_id == user.id:
        return True
    return ProjectCollaborator.objects.filter(
        project_id=project.id, user_id=user.id
    ).exists()


def _sanitize_filename(name: str) -> str:
    # Strip directory path
    name = name.rsplit("/", 1)[-1]
    name = name.rsplit("\\", 1)[-1]
    # Replace non-alphanumeric except .-_ with underscore
    name = re.sub(r"[^a-zA-Z0-9._-]", "_", name)
    # Collapse consecutive underscores
    name = re.sub(r"_+", "_", name)
    # Truncate to 255
    return name[:255]


def _check_rate_limit(user_id: str) -> bool:
    """Return True if rate limit exceeded."""
    cache_key = f"upload_rate:{user_id}"
    count = cache.get(cache_key, 0)
    if count >= RATE_LIMIT_UPLOADS_PER_MINUTE:
        return True
    cache.set(cache_key, count + 1, timeout=60)
    return False


def _get_storage_backend():
    from storage.factory import get_storage_backend
    return get_storage_backend()


@api_view(["GET", "POST"])
@authentication_classes([MiddlewareAuthentication])
@parser_classes([MultiPartParser])
def attachment_list(request: Request, project_id: str) -> Response:
    if request.method == "POST":
        return _upload_attachment(request, project_id)
    return _list_attachments(request, project_id)


def _upload_attachment(request: Request, project_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    project, error = _get_project_or_error(project_id)
    if error:
        return error

    if not _check_access(user, project):
        return Response(
            {"error": "ACCESS_DENIED", "message": "You do not have access to this project"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Rate limit
    if _check_rate_limit(str(user.id)):
        return Response(
            {"error": "RATE_LIMITED", "message": "Too many uploads. Please wait."},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    # Get file
    file = request.FILES.get("file")
    if not file:
        return Response(
            {"error": "VALIDATION_ERROR", "message": "No file provided"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        return Response(
            {"error": "VALIDATION_ERROR", "message": f"File type '{file.content_type}' is not allowed. Allowed types: png, jpeg, webp, pdf"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate file size
    if file.size > MAX_FILE_SIZE:
        return Response(
            {"error": "VALIDATION_ERROR", "message": "File size exceeds 100MB limit"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate project attachment count
    active_count = Attachment.active_count_for_project(project.id)
    if active_count >= MAX_ATTACHMENTS_PER_PROJECT:
        return Response(
            {"error": "VALIDATION_ERROR", "message": "Project has reached the maximum of 10 attachments"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Sanitize filename and generate storage key
    sanitized_name = _sanitize_filename(file.name or "unnamed")
    ext = sanitized_name.rsplit(".", 1)[-1] if "." in sanitized_name else ""
    file_uuid = uuid.uuid4()
    storage_key = f"attachments/{project.id}/{file_uuid}.{ext}" if ext else f"attachments/{project.id}/{file_uuid}"

    # Read file data
    file_data = file.read()

    # Upload to storage
    try:
        backend = _get_storage_backend()
        backend.upload_file(storage_key, file_data, file.content_type)
    except Exception:
        logger.exception("Failed to upload file to storage")
        return Response(
            {"error": "STORAGE_ERROR", "message": "Failed to upload file"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Create attachment record
    attachment = Attachment.objects.create(
        project=project,
        uploader_id=user.id,
        filename=sanitized_name,
        storage_key=storage_key,
        content_type=file.content_type,
        size_bytes=len(file_data),
    )

    serializer = AttachmentResponseSerializer(attachment)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def _list_attachments(request: Request, project_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    project, error = _get_project_or_error(project_id)
    if error:
        return error

    if not _check_access(user, project):
        return Response(
            {"error": "ACCESS_DENIED", "message": "You do not have access to this project"},
            status=status.HTTP_403_FORBIDDEN,
        )

    attachments = Attachment.objects.filter(
        project_id=project.id, deleted_at__isnull=True
    ).order_by("-created_at")

    serializer = AttachmentResponseSerializer(attachments, many=True)
    return Response(serializer.data)


@api_view(["DELETE"])
@authentication_classes([MiddlewareAuthentication])
def attachment_delete(request: Request, project_id: str, attachment_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    project, error = _get_project_or_error(project_id)
    if error:
        return error

    # Validate attachment UUID
    try:
        uuid.UUID(attachment_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Attachment not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        attachment = Attachment.objects.get(
            id=attachment_id, project_id=project.id, deleted_at__isnull=True
        )
    except Attachment.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Attachment not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Check access: must be uploader or project owner
    if attachment.uploader_id != user.id and project.owner_id != user.id:
        return Response(
            {"error": "ACCESS_DENIED", "message": "Only the uploader or project owner can delete this attachment"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Immutability rule: cannot delete attachment already linked to a message
    if attachment.message_id is not None:
        return Response(
            {"error": "IMMUTABLE", "message": "Cannot delete attachment already sent with message"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Soft delete
    attachment.deleted_at = timezone.now()
    attachment.save(update_fields=["deleted_at"])

    # Best-effort storage deletion
    try:
        backend = _get_storage_backend()
        backend.delete_file(attachment.storage_key)
    except Exception:
        logger.warning("Failed to delete file from storage: %s", attachment.storage_key)

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def attachment_url(request: Request, project_id: str, attachment_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    project, error = _get_project_or_error(project_id)
    if error:
        return error

    if not _check_access(user, project):
        return Response(
            {"error": "ACCESS_DENIED", "message": "You do not have access to this project"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Validate attachment UUID
    try:
        uuid.UUID(attachment_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Attachment not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        attachment = Attachment.objects.get(
            id=attachment_id, project_id=project.id, deleted_at__isnull=True
        )
    except Attachment.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Attachment not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        backend = _get_storage_backend()
        url = backend.get_presigned_url(
            attachment.storage_key,
            expires_seconds=PRESIGNED_URL_TTL,
            filename=attachment.filename,
        )
    except Exception:
        logger.exception("Failed to generate presigned URL for %s", attachment.storage_key)
        return Response(
            {"error": "STORAGE_ERROR", "message": "Failed to generate download URL"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response({"url": url})
