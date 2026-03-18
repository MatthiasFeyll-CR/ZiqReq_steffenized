"""Celery tasks: soft delete cleanup."""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="projects.soft_delete_cleanup")
def soft_delete_cleanup() -> dict:
    """Permanently delete projects that have been in trash beyond the countdown."""
    from datetime import timedelta

    from django.utils import timezone

    from apps.admin_config.services import get_parameter
    from apps.projects.models import Project

    countdown_days: int = get_parameter("soft_delete_countdown", default=30, cast=int)
    cutoff = timezone.now() - timedelta(days=countdown_days)

    expired_projects = Project.objects.filter(
        deleted_at__isnull=False,
        deleted_at__lt=cutoff,
    )
    project_ids = list(expired_projects.values_list("id", flat=True))
    count = len(project_ids)

    if count:
        # Related tables use bare UUIDFields (not Django ForeignKeys),
        # so we must delete associated records manually.
        from apps.brd.models import BrdDraft, BrdVersion
        from apps.chat.models import AiReaction, ChatMessage, UserReaction
        from apps.collaboration.models import CollaborationInvitation
        from apps.projects.models import Attachment
        from apps.review.models import ReviewAssignment, ReviewTimelineEntry

        # Collect attachment storage keys before CASCADE delete removes the records
        attachment_keys = list(
            Attachment.objects.filter(project_id__in=project_ids).values_list("storage_key", flat=True)
        )

        # Dispatch storage file cleanup BEFORE deleting DB records
        # so keys are recoverable on next run if dispatch fails
        if attachment_keys:
            _dispatch_storage_cleanup(attachment_keys)

        # Delete reactions linked to chat messages for these projects
        message_ids = list(
            ChatMessage.objects.filter(project_id__in=project_ids).values_list("id", flat=True)
        )
        if message_ids:
            AiReaction.objects.filter(message_id__in=message_ids).delete()
            UserReaction.objects.filter(message_id__in=message_ids).delete()

        ChatMessage.objects.filter(project_id__in=project_ids).delete()
        BrdDraft.objects.filter(project_id__in=project_ids).delete()
        BrdVersion.objects.filter(project_id__in=project_ids).delete()
        CollaborationInvitation.objects.filter(project_id__in=project_ids).delete()
        ReviewAssignment.objects.filter(project_id__in=project_ids).delete()
        ReviewTimelineEntry.objects.filter(project_id__in=project_ids).delete()

        # Delete the projects themselves (ProjectCollaborator has a real FK CASCADE)
        expired_projects.delete()

        logger.info("Permanently deleted %d projects past %d-day soft delete countdown", count, countdown_days)
    else:
        logger.info("No expired soft-deleted projects found (countdown: %d days)", countdown_days)

    return {"deleted_count": count, "countdown_days": countdown_days}


def _dispatch_storage_cleanup(storage_keys: list[str]) -> None:
    """Dispatch storage file deletion to gateway celery worker."""
    try:
        from celery import Celery
        from django.conf import settings

        app = Celery("gateway", broker=settings.CELERY_BROKER_URL)
        app.send_task(
            "attachments.bulk_delete_storage",
            kwargs={"storage_keys": storage_keys},
            queue="gateway",
        )
        logger.info("Dispatched storage cleanup for %d files", len(storage_keys))
    except Exception:
        logger.warning("Failed to dispatch storage cleanup for %d files", len(storage_keys))
