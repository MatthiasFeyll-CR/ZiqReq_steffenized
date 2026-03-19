"""Celery tasks for attachment cleanup."""

import logging
import os

import redis as redis_lib
from celery import shared_task

logger = logging.getLogger(__name__)

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")


def _write_last_run(task_name: str) -> None:
    """Best-effort write of last-run timestamp to Redis."""
    try:
        from django.utils import timezone

        r = redis_lib.from_url(REDIS_URL, socket_timeout=5)
        r.set(f"jobs:last_run:{task_name}", timezone.now().isoformat())
    except Exception:
        logger.warning("Failed to write last_run timestamp for %s", task_name)


@shared_task(name="attachments.orphan_cleanup")
def orphan_cleanup(param_overrides: dict | None = None) -> dict:
    """Soft-delete orphaned attachments (uploaded but never linked to a message) past TTL."""
    from datetime import timedelta

    from django.utils import timezone

    from apps.admin_config.services import get_parameter
    from apps.projects.models import Attachment

    overrides = param_overrides or {}
    ttl_hours: int = int(overrides["orphan_attachment_ttl_hours"]) if "orphan_attachment_ttl_hours" in overrides else get_parameter("orphan_attachment_ttl_hours", default=96, cast=int)
    cutoff = timezone.now() - timedelta(hours=ttl_hours)

    orphaned = Attachment.objects.filter(
        message_id__isnull=True,
        deleted_at__isnull=True,
        created_at__lt=cutoff,
    )
    count = orphaned.update(deleted_at=timezone.now())

    if count:
        logger.info("Soft-deleted %d orphaned attachments (TTL: %dh)", count, ttl_hours)
    else:
        logger.info("No orphaned attachments found past %dh TTL", ttl_hours)

    result = {"soft_deleted_count": count, "ttl_hours": ttl_hours}
    _write_last_run("attachments.orphan_cleanup")
    return result


@shared_task(name="attachments.storage_cleanup")
def storage_cleanup(param_overrides: dict | None = None) -> dict:
    """Hard-delete expired soft-deleted attachments and their storage files."""
    from datetime import timedelta

    from django.db import transaction
    from django.utils import timezone

    from apps.admin_config.services import get_parameter
    from apps.projects.models import Attachment

    overrides = param_overrides or {}
    retention_hours: int = int(overrides["soft_delete_retention_hours"]) if "soft_delete_retention_hours" in overrides else get_parameter("soft_delete_retention_hours", default=720, cast=int)
    cutoff = timezone.now() - timedelta(hours=retention_hours)

    with transaction.atomic():
        expired = Attachment.objects.select_for_update().filter(
            deleted_at__isnull=False,
            deleted_at__lt=cutoff,
        )
        storage_keys = list(expired.values_list("storage_key", flat=True))
        count = len(storage_keys)

        if count:
            expired.delete()

    # Delete storage files outside transaction (best-effort, DB records already gone)
    if count:
        _delete_storage_files(storage_keys)
        logger.info("Hard-deleted %d expired attachments and storage files", count)
    else:
        logger.info("No expired soft-deleted attachments to clean up")

    result = {"hard_deleted_count": count, "retention_hours": retention_hours}
    _write_last_run("attachments.storage_cleanup")
    return result


@shared_task(name="attachments.bulk_delete_storage")
def bulk_delete_storage(storage_keys: list[str]) -> dict:
    """Delete a list of storage files from MinIO (dispatched by core on project hard-delete).

    Only deletes keys that exist in the attachments table to prevent unauthorized deletion.
    """
    from apps.projects.models import Attachment

    valid_keys = set(
        Attachment.objects.filter(storage_key__in=storage_keys).values_list("storage_key", flat=True)
    )
    if len(valid_keys) < len(storage_keys):
        logger.warning(
            "bulk_delete_storage: %d/%d keys not found in DB, skipping",
            len(storage_keys) - len(valid_keys),
            len(storage_keys),
        )
    deleted = _delete_storage_files(list(valid_keys)) if valid_keys else 0
    return {"requested": len(storage_keys), "valid": len(valid_keys), "deleted": deleted}


def _delete_storage_files(storage_keys: list[str]) -> int:
    """Best-effort deletion of storage files. Returns count of successful deletions."""
    from storage.factory import get_storage_backend

    backend = get_storage_backend()
    deleted = 0
    for key in storage_keys:
        try:
            backend.delete_file(key)
            deleted += 1
        except Exception:
            logger.warning("Failed to delete storage file: %s", key, exc_info=True)
    return deleted
