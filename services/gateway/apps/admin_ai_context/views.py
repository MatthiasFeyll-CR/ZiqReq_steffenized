import logging

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response

from apps.ideas.authentication import MiddlewareAuthentication

from .models import ContextAgentBucket, FacilitatorContextBucket
from .serializers import ContextAgentBucketSerializer, FacilitatorContextSerializer

logger = logging.getLogger(__name__)


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


@api_view(["GET", "PATCH"])
@authentication_classes([MiddlewareAuthentication])
def facilitator_context(request: Request) -> Response:
    """GET/PATCH /api/admin/ai-context/facilitator"""
    denied = _require_admin(request)
    if denied:
        return denied

    bucket, _created = FacilitatorContextBucket.objects.get_or_create(
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
    """GET/PATCH /api/admin/ai-context/company"""
    denied = _require_admin(request)
    if denied:
        return denied

    bucket, _created = ContextAgentBucket.objects.get_or_create(
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

    return Response(ContextAgentBucketSerializer(bucket).data)
