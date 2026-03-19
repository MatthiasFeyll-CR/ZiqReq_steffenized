import json
import logging
import os

import redis as redis_lib
from celery import Celery
from celery.result import AsyncResult
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response

from apps.projects.authentication import MiddlewareAuthentication

from .models import AdminParameter
from .serializers import AdminParameterSerializer, AdminParameterUpdateSerializer

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Job registry — periodic Celery tasks exposed for manual triggering
# ---------------------------------------------------------------------------

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
BROKER_URL = os.environ.get("BROKER_URL", "amqp://guest:guest@rabbitmq:5672/")
RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

JOB_COOLDOWN_SECONDS = 60

JOB_REGISTRY: dict[str, dict] = {
    "projects.soft_delete_cleanup": {
        "name_key": "admin.jobs.softDeleteCleanup",
        "description_key": "admin.jobs.softDeleteCleanupDesc",
        "schedule_key": "admin.jobs.daily",
        "schedule_seconds": 86400,
        "queue": "celery",
        "override_params": [
            {"key": "soft_delete_countdown", "label_key": "admin.jobs.params.softDeleteCountdown", "type": "integer"},
        ],
    },
    "attachments.orphan_cleanup": {
        "name_key": "admin.jobs.orphanCleanup",
        "description_key": "admin.jobs.orphanCleanupDesc",
        "schedule_key": "admin.jobs.hourly",
        "schedule_seconds": 3600,
        "queue": "gateway",
        "override_params": [
            {"key": "orphan_attachment_ttl_hours", "label_key": "admin.jobs.params.orphanTtlHours", "type": "integer"},
        ],
    },
    "attachments.storage_cleanup": {
        "name_key": "admin.jobs.storageCleanup",
        "description_key": "admin.jobs.storageCleanupDesc",
        "schedule_key": "admin.jobs.hourly",
        "schedule_seconds": 3600,
        "queue": "gateway",
        "override_params": [
            {"key": "soft_delete_retention_hours", "label_key": "admin.jobs.params.retentionHours", "type": "integer"},
        ],
    },
}


def _get_redis() -> redis_lib.Redis:
    return redis_lib.from_url(REDIS_URL, socket_timeout=5)


def _get_celery_app() -> Celery:
    app = Celery(broker=BROKER_URL, backend=RESULT_BACKEND)
    return app


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


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def parameter_list(request: Request) -> Response:
    """GET /api/admin/parameters — list all parameters."""
    denied = _require_admin(request)
    if denied:
        return denied

    params = AdminParameter.objects.all().order_by("key")
    serializer = AdminParameterSerializer(params, many=True)
    return Response(serializer.data)


@api_view(["PATCH"])
@authentication_classes([MiddlewareAuthentication])
def parameter_update(request: Request, key: str) -> Response:
    """PATCH /api/admin/parameters/:key — update parameter value."""
    denied = _require_admin(request)
    if denied:
        return denied

    try:
        param = AdminParameter.objects.get(key=key)
    except AdminParameter.DoesNotExist:
        return Response(
            {"error": "PARAMETER_NOT_FOUND", "message": f"Parameter '{key}' not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = AdminParameterUpdateSerializer(
        data=request.data, context={"parameter": param}
    )
    if not serializer.is_valid():
        return Response(
            {"error": "INVALID_VALUE", "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    param.value = serializer.validated_data["value"]
    param.updated_by = request.user.id
    param.updated_at = timezone.now()
    param.save(update_fields=["value", "updated_by", "updated_at"])

    return Response(AdminParameterSerializer(param).data)


DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def admin_attachments_list(request: Request) -> Response:
    """GET /api/admin/attachments — list all attachments with filter/search/pagination/stats."""
    denied = _require_admin(request)
    if denied:
        return denied

    from django.db.models import Count, Sum

    from apps.projects.models import Attachment, Project

    filter_param = request.query_params.get("filter", "all")
    search_param = request.query_params.get("search", "")
    page = max(int(request.query_params.get("page", 1)), 1)
    page_size = min(
        int(request.query_params.get("page_size", 35)),
        MAX_PAGE_SIZE,
    )

    qs = Attachment.objects.all()

    if filter_param == "active":
        qs = qs.filter(deleted_at__isnull=True)
    elif filter_param == "deleted":
        qs = qs.filter(deleted_at__isnull=False)

    if search_param:
        qs = qs.filter(Q(filename__icontains=search_param))

    qs = qs.order_by("-created_at")

    total_count = qs.count()
    offset = (page - 1) * page_size
    attachments = list(qs[offset : offset + page_size])

    # Get project names
    project_ids = {a.project_id for a in attachments}
    projects = Project.objects.filter(id__in=project_ids)
    project_map = {p.id: p for p in projects}

    # Stats (unfiltered)
    stats = Attachment.objects.aggregate(
        total_size=Sum("size_bytes"),
        total_count=Count("id"),
    )

    results = []
    for att in attachments:
        proj = project_map.get(att.project_id)
        results.append(
            {
                "id": str(att.id),
                "filename": att.filename,
                "content_type": att.content_type,
                "size_bytes": att.size_bytes,
                "extraction_status": att.extraction_status,
                "created_at": att.created_at.isoformat(),
                "deleted_at": att.deleted_at.isoformat() if att.deleted_at else None,
                "message_id": str(att.message_id) if att.message_id else None,
                "project": {
                    "id": str(att.project_id),
                    "title": proj.title if proj else "Unknown",
                },
            }
        )

    return Response(
        {
            "results": results,
            "count": total_count,
            "next": page + 1 if offset + page_size < total_count else None,
            "previous": page - 1 if page > 1 else None,
            "stats": {
                "total_size_bytes": stats["total_size"] or 0,
                "total_count": stats["total_count"] or 0,
            },
        }
    )


@api_view(["DELETE"])
@authentication_classes([MiddlewareAuthentication])
def admin_attachment_delete(request: Request, attachment_id: str) -> Response:
    """DELETE /api/admin/attachments/:id — hard-delete attachment (DB record + storage file)."""
    denied = _require_admin(request)
    if denied:
        return denied

    import uuid

    from apps.projects.models import Attachment

    try:
        uuid.UUID(attachment_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Attachment not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        attachment = Attachment.objects.get(id=attachment_id)
    except Attachment.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Attachment not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Delete storage file (best-effort)
    try:
        from storage.factory import get_storage_backend

        backend = get_storage_backend()
        backend.delete_file(attachment.storage_key)
    except Exception:
        logger.warning("Failed to delete storage file %s", attachment.storage_key)

    logger.info("Admin %s hard-deleted attachment %s (storage_key=%s)", request.user.id, attachment_id, attachment.storage_key)
    attachment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def admin_attachment_restore(request: Request, attachment_id: str) -> Response:
    """POST /api/admin/attachments/:id/restore/ — restore soft-deleted attachment."""
    denied = _require_admin(request)
    if denied:
        return denied

    import uuid

    from apps.attachments.serializers import AttachmentResponseSerializer
    from apps.projects.models import Attachment, Project

    try:
        uuid.UUID(attachment_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Attachment not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        attachment = Attachment.objects.get(id=attachment_id, deleted_at__isnull=False)
    except Attachment.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Attachment not found or not deleted"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Verify project still exists
    if not Project.objects.filter(id=attachment.project_id, deleted_at__isnull=True).exists():
        return Response(
            {"error": "PROJECT_DELETED", "message": "Cannot restore attachment for deleted project"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check storage file still exists
    from storage.factory import get_storage_backend

    backend = get_storage_backend()
    if not backend.file_exists(attachment.storage_key):
        return Response(
            {"error": "FILE_GONE", "message": "Storage file no longer exists"},
            status=status.HTTP_410_GONE,
        )

    attachment.deleted_at = None
    attachment.save(update_fields=["deleted_at"])
    logger.info("Admin %s restored attachment %s", request.user.id, attachment_id)
    return Response(AttachmentResponseSerializer(attachment).data)


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def admin_projects_list(request: Request) -> Response:
    """GET /api/admin/projects — list all projects with state and keywords (admin only)."""
    denied = _require_admin(request)
    if denied:
        return denied

    from apps.authentication.models import User
    from apps.projects.models import Project

    state_param = request.query_params.get("state")
    search_param = request.query_params.get("search")
    page = max(int(request.query_params.get("page", 1)), 1)
    page_size = min(
        int(request.query_params.get("page_size", DEFAULT_PAGE_SIZE)),
        MAX_PAGE_SIZE,
    )

    qs = Project.objects.filter(deleted_at__isnull=True)

    if state_param:
        qs = qs.filter(state=state_param)

    if search_param:
        qs = qs.filter(Q(title__icontains=search_param))

    qs = qs.order_by("-updated_at")

    total_count = qs.count()
    offset = (page - 1) * page_size
    projects = list(qs[offset : offset + page_size])

    # Fetch owners
    owner_ids = {project.owner_id for project in projects}
    users = User.objects.filter(id__in=owner_ids)
    user_map = {u.id: u for u in users}

    results = []
    for project in projects:
        owner = user_map.get(project.owner_id)
        results.append(
            {
                "id": str(project.id),
                "title": project.title,
                "state": project.state,
                "owner": {
                    "id": str(owner.id) if owner else str(project.owner_id),
                    "display_name": owner.display_name if owner else "",
                },
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat(),
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


# ---------------------------------------------------------------------------
# Jobs — list and manual trigger
# ---------------------------------------------------------------------------


def _job_state(r: redis_lib.Redis, task_name: str) -> dict:
    """Derive the current state of a job from Redis keys.

    Returns dict with keys: status, task_id, result, last_run, next_run, cooldown_remaining.
    """
    last_run_raw = r.get(f"jobs:last_run:{task_name}")
    last_run = last_run_raw.decode() if last_run_raw else None

    active_task_id_raw = r.get(f"jobs:active_task:{task_name}")
    active_task_id = active_task_id_raw.decode() if active_task_id_raw else None

    cooldown_ttl = r.ttl(f"jobs:cooldown:{task_name}")  # -2 = missing, -1 = no TTL

    job_status = "idle"
    result = None
    task_id = None

    if active_task_id:
        # Check Celery result
        celery_app = _get_celery_app()
        async_result = AsyncResult(active_task_id, app=celery_app)
        celery_status = async_result.status  # PENDING, STARTED, SUCCESS, FAILURE, etc.

        if celery_status in ("PENDING", "STARTED"):
            job_status = "running"
            task_id = active_task_id
        elif celery_status == "SUCCESS":
            result = async_result.result
            # Transition: clear running, set cooldown, update last_run, persist result
            now_iso = timezone.now().isoformat()
            pipe = r.pipeline()
            pipe.delete(f"jobs:active_task:{task_name}")
            pipe.setex(f"jobs:cooldown:{task_name}", JOB_COOLDOWN_SECONDS, "1")
            pipe.set(f"jobs:last_run:{task_name}", now_iso)
            pipe.setex(
                f"jobs:last_result:{task_name}",
                JOB_COOLDOWN_SECONDS,
                json.dumps(result, default=str),
            )
            pipe.execute()
            last_run = now_iso
            cooldown_ttl = JOB_COOLDOWN_SECONDS
            job_status = "cooldown"
            task_id = active_task_id
        elif celery_status in ("FAILURE", "REVOKED"):
            try:
                result = {"error": str(async_result.result)}
            except Exception:
                result = {"error": celery_status}
            pipe = r.pipeline()
            pipe.delete(f"jobs:active_task:{task_name}")
            pipe.setex(f"jobs:cooldown:{task_name}", JOB_COOLDOWN_SECONDS, "1")
            pipe.setex(
                f"jobs:last_result:{task_name}",
                JOB_COOLDOWN_SECONDS,
                json.dumps(result, default=str),
            )
            pipe.execute()
            cooldown_ttl = JOB_COOLDOWN_SECONDS
            job_status = "cooldown"
            task_id = active_task_id
    elif cooldown_ttl > 0:
        job_status = "cooldown"
        # Read persisted result from previous transition
        result_raw = r.get(f"jobs:last_result:{task_name}")
        if result_raw:
            try:
                result = json.loads(result_raw.decode())
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass

    # Calculate next run
    schedule_seconds = JOB_REGISTRY[task_name]["schedule_seconds"]
    next_run = None
    if last_run:
        from datetime import timedelta
        from django.utils.dateparse import parse_datetime

        parsed = parse_datetime(last_run)
        if parsed:
            next_run = (parsed + timedelta(seconds=schedule_seconds)).isoformat()

    return {
        "status": job_status,
        "task_id": task_id,
        "result": result,
        "last_run": last_run,
        "next_run": next_run,
        "cooldown_remaining": max(cooldown_ttl, 0),
    }


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def jobs_list(request: Request) -> Response:
    """GET /api/admin/jobs — list all periodic jobs with current state."""
    denied = _require_admin(request)
    if denied:
        return denied

    try:
        r = _get_redis()
    except Exception:
        return Response(
            {"error": "REDIS_UNAVAILABLE", "message": "Cannot connect to Redis"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    # Fetch current parameter values for override_params
    param_keys = set()
    for meta in JOB_REGISTRY.values():
        for p in meta.get("override_params", []):
            param_keys.add(p["key"])

    current_params = {}
    if param_keys:
        from .models import AdminParameter
        for ap in AdminParameter.objects.filter(key__in=param_keys):
            current_params[ap.key] = {
                "value": ap.value,
                "default_value": ap.default_value,
                "description": ap.description,
            }

    jobs = []
    for task_name, meta in JOB_REGISTRY.items():
        state = _job_state(r, task_name)
        override_params = []
        for p in meta.get("override_params", []):
            param_info = current_params.get(p["key"], {})
            override_params.append({
                "key": p["key"],
                "label_key": p["label_key"],
                "type": p["type"],
                "current_value": param_info.get("value", ""),
                "default_value": param_info.get("default_value", ""),
                "description": param_info.get("description", ""),
            })
        jobs.append({
            "task_name": task_name,
            "name_key": meta["name_key"],
            "description_key": meta["description_key"],
            "schedule_key": meta["schedule_key"],
            "queue": meta["queue"],
            "override_params": override_params,
            **state,
        })

    return Response(jobs)


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def job_trigger(request: Request, task_name: str) -> Response:
    """POST /api/admin/jobs/<task_name>/trigger — manually trigger a periodic job."""
    denied = _require_admin(request)
    if denied:
        return denied

    if task_name not in JOB_REGISTRY:
        return Response(
            {"error": "NOT_FOUND", "message": f"Unknown job: {task_name}"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        r = _get_redis()
    except Exception:
        return Response(
            {"error": "REDIS_UNAVAILABLE", "message": "Cannot connect to Redis"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    # Check if already running
    if r.exists(f"jobs:active_task:{task_name}"):
        return Response(
            {"error": "ALREADY_RUNNING", "message": "This job is already running"},
            status=status.HTTP_409_CONFLICT,
        )

    # Check cooldown
    if r.ttl(f"jobs:cooldown:{task_name}") > 0:
        remaining = r.ttl(f"jobs:cooldown:{task_name}")
        return Response(
            {"error": "COOLDOWN", "message": f"Please wait {remaining}s before re-triggering"},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    meta = JOB_REGISTRY[task_name]

    # Extract parameter overrides from request body
    allowed_override_keys = {p["key"] for p in meta.get("override_params", [])}
    overrides = {}
    raw_overrides = request.data.get("param_overrides", {}) if request.data else {}
    if isinstance(raw_overrides, dict):
        for k, v in raw_overrides.items():
            if k in allowed_override_keys:
                overrides[k] = v

    celery_app = _get_celery_app()
    kwargs = {"param_overrides": overrides} if overrides else {}
    async_result = celery_app.send_task(task_name, kwargs=kwargs, queue=meta["queue"])

    # Store active task id with 120s safety TTL (cleared when result is read)
    r.setex(f"jobs:active_task:{task_name}", 120, async_result.id)

    logger.info("Admin %s manually triggered job %s (task_id=%s)", request.user.id, task_name, async_result.id)

    return Response({
        "task_name": task_name,
        "task_id": async_result.id,
        "status": "running",
    })
