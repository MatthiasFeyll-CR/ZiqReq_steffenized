"""Celery tasks: soft delete cleanup."""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="ideas.soft_delete_cleanup")
def soft_delete_cleanup() -> dict:
    """Permanently delete ideas that have been in trash beyond the countdown."""
    from datetime import timedelta

    from django.utils import timezone

    from apps.admin_config.services import get_parameter
    from apps.ideas.models import Idea

    countdown_days: int = get_parameter("soft_delete_countdown", default=30, cast=int)
    cutoff = timezone.now() - timedelta(days=countdown_days)

    expired_ideas = Idea.objects.filter(
        deleted_at__isnull=False,
        deleted_at__lt=cutoff,
    )
    idea_ids = list(expired_ideas.values_list("id", flat=True))
    count = len(idea_ids)

    if count:
        # Related tables use bare UUIDFields (not Django ForeignKeys),
        # so we must delete associated records manually.
        from apps.brd.models import BrdDraft, BrdVersion
        from apps.chat.models import AiReaction, ChatMessage, UserReaction
        from apps.collaboration.models import CollaborationInvitation
        from apps.review.models import ReviewAssignment, ReviewTimelineEntry

        # Delete reactions linked to chat messages for these ideas
        message_ids = list(
            ChatMessage.objects.filter(idea_id__in=idea_ids).values_list("id", flat=True)
        )
        if message_ids:
            AiReaction.objects.filter(message_id__in=message_ids).delete()
            UserReaction.objects.filter(message_id__in=message_ids).delete()

        ChatMessage.objects.filter(idea_id__in=idea_ids).delete()
        BrdDraft.objects.filter(idea_id__in=idea_ids).delete()
        BrdVersion.objects.filter(idea_id__in=idea_ids).delete()
        CollaborationInvitation.objects.filter(idea_id__in=idea_ids).delete()
        ReviewAssignment.objects.filter(idea_id__in=idea_ids).delete()
        ReviewTimelineEntry.objects.filter(idea_id__in=idea_ids).delete()

        # Delete the ideas themselves (IdeaCollaborator has a real FK CASCADE)
        expired_ideas.delete()

        logger.info("Permanently deleted %d ideas past %d-day soft delete countdown", count, countdown_days)
    else:
        logger.info("No expired soft-deleted ideas found (countdown: %d days)", countdown_days)

    return {"deleted_count": count, "countdown_days": countdown_days}
