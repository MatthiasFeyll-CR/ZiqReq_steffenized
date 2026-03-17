import json
import logging
import os

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response

from apps.projects.authentication import MiddlewareAuthentication

from .models import ContextAgentBucket, FacilitatorContextBucket
from .serializers import ContextAgentBucketSerializer, FacilitatorContextSerializer

logger = logging.getLogger(__name__)

VALID_CONTEXT_TYPES = {"global", "software", "non_software"}


def _get_ai_client():
    """Create an AiClient instance (lazy import to avoid namespace collisions)."""
    from grpc_clients.ai_client import AiClient

    address = os.environ.get("AI_GRPC_ADDRESS", "localhost:50052")
    return AiClient(address=address)


def _require_admin(request: Request) -> Response | None:
    """Return a 403 Response if the user is not an admin, else None."""
    user = getattr(request, "user", None)
    if user is None or not getattr(user, "id", None):
        return Response(
            {"error": "UNAUTHORIZED", "message": "Authentication required"},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    roles = getattr(user, "roles", []) or []
    if "admin" not in roles:
        return Response(
            {"error": "FORBIDDEN", "message": "Admin role required"},
            status=status.HTTP_403_FORBIDDEN,
        )
    return None


def _get_context_type(request: Request) -> str:
    """Extract and validate context_type from ?type= query param. Defaults to 'global'."""
    context_type = request.query_params.get("type", "global")
    if context_type not in VALID_CONTEXT_TYPES:
        return "global"
    return context_type


@api_view(["GET", "PATCH"])
@authentication_classes([MiddlewareAuthentication])
def facilitator_context(request: Request) -> Response:
    """GET/PATCH /api/admin/ai-context/facilitator?type={global|software|non_software}"""
    denied = _require_admin(request)
    if denied:
        return denied

    context_type = _get_context_type(request)

    bucket, _created = FacilitatorContextBucket.objects.get_or_create(
        context_type=context_type,
        defaults={"content": "", "updated_by": None},
    )

    if request.method == "PATCH":
        serializer = FacilitatorContextSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        bucket.content = serializer.validated_data["content"]
        bucket.updated_by = request.user.id
        bucket.updated_at = timezone.now()
        bucket.save(update_fields=["content", "updated_by", "updated_at"])

    return Response(FacilitatorContextSerializer(bucket).data)


@api_view(["GET", "PATCH"])
@authentication_classes([MiddlewareAuthentication])
def company_context(request: Request) -> Response:
    """GET/PATCH /api/admin/ai-context/company?type={global|software|non_software}"""
    denied = _require_admin(request)
    if denied:
        return denied

    context_type = _get_context_type(request)

    bucket, _created = ContextAgentBucket.objects.get_or_create(
        context_type=context_type,
        defaults={"sections": {}, "free_text": "", "updated_by": None},
    )

    if request.method == "PATCH":
        serializer = ContextAgentBucketSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        bucket.sections = serializer.validated_data.get("sections", bucket.sections)
        bucket.free_text = serializer.validated_data.get("free_text", bucket.free_text)
        bucket.updated_by = request.user.id
        bucket.updated_at = timezone.now()
        bucket.save(update_fields=["sections", "free_text", "updated_by", "updated_at"])

        # Trigger AI gRPC re-indexing
        try:
            ai_client = _get_ai_client()
            ai_client.update_context_agent_bucket(
                sections_json=json.dumps(bucket.sections),
                free_text=bucket.free_text,
                updated_by_id=str(bucket.updated_by),
            )
            logger.info("Context re-indexing triggered for bucket %s", bucket.id)
        except Exception:
            logger.exception("Failed to trigger context re-indexing via AI gRPC")
            return Response(
                {
                    "error": "REINDEX_FAILED",
                    "message": "Company context updated but re-indexing failed. Please retry.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return Response(ContextAgentBucketSerializer(bucket).data)
