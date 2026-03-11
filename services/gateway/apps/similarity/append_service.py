"""Append execution service — flags requesting idea and adds owner as collaborator on target.

Mirrors services/core/apps/similarity/append_service.py for test discoverability.

Consumes append.accepted events and atomically:
1. Sets requesting idea's closed_by_append_id to target idea (state stays 'open')
2. Adds requesting owner as collaborator on target idea
3. Updates merge_request: status='accepted', resolved_at=now()
4. Publishes append.complete event

No new idea is created. Target stays in_review.
"""

from __future__ import annotations

import logging
from typing import Any

from django.db import transaction
from django.utils import timezone as dj_timezone

logger = logging.getLogger(__name__)


def execute_append(
    merge_request_id: str,
    requesting_idea_id: str,
    target_idea_id: str,
) -> dict[str, Any]:
    """Execute an append: flag requesting idea and add owner as collaborator on target.

    Returns:
        Dict with target_idea_id, requesting_owner_id, and target_collaborator_ids.
    """
    from apps.ideas.models import Idea, IdeaCollaborator
    from apps.similarity.models import MergeRequest

    with transaction.atomic():
        # 1. Fetch both ideas
        requesting_idea = Idea.objects.get(id=requesting_idea_id, deleted_at__isnull=True)
        target_idea = Idea.objects.get(id=target_idea_id, deleted_at__isnull=True)

        # 2. Fetch and lock merge request
        merge_req = MergeRequest.objects.select_for_update().get(id=merge_request_id)

        # 3. Flag requesting idea: closed_by_append_id (state stays 'open')
        requesting_idea.closed_by_append_id = target_idea.id
        requesting_idea.save(update_fields=["closed_by_append_id"])

        # 4. Add requesting owner as collaborator on target idea
        IdeaCollaborator.objects.get_or_create(
            idea=target_idea,
            user_id=requesting_idea.owner_id,
        )

        # 5. Update merge_request: status='accepted', resolved_at=now()
        merge_req.status = "accepted"
        merge_req.resolved_at = dj_timezone.now()
        merge_req.save(update_fields=["status", "resolved_at"])

        # 6. Collect all collaborator ids on target for the event
        target_collaborator_ids = list(
            IdeaCollaborator.objects.filter(idea=target_idea).values_list(
                "user_id", flat=True
            )
        )

    # 7. Publish append.complete event (outside transaction)
    _publish_append_complete(
        merge_request_id=merge_request_id,
        requesting_idea_id=requesting_idea_id,
        target_idea_id=target_idea_id,
        requesting_owner_id=str(requesting_idea.owner_id),
        target_owner_id=str(target_idea.owner_id),
        target_collaborator_ids=[str(uid) for uid in target_collaborator_ids],
    )

    logger.info(
        "Append complete: MR %s — idea %s appended to %s",
        merge_request_id,
        requesting_idea_id,
        target_idea_id,
    )

    return {
        "target_idea_id": str(target_idea.id),
        "requesting_owner_id": str(requesting_idea.owner_id),
        "target_collaborator_ids": [str(uid) for uid in target_collaborator_ids],
    }


def _publish_append_complete(
    merge_request_id: str,
    requesting_idea_id: str,
    target_idea_id: str,
    requesting_owner_id: str,
    target_owner_id: str,
    target_collaborator_ids: list[str],
) -> None:
    """Publish append.complete event for notifications."""
    from events.publisher import publish_event

    publish_event(
        event_type="notification.similarity.append_complete",
        payload={
            "merge_request_id": merge_request_id,
            "requesting_idea_id": requesting_idea_id,
            "target_idea_id": target_idea_id,
            "requesting_owner_id": requesting_owner_id,
            "target_owner_id": target_owner_id,
            "target_collaborator_ids": target_collaborator_ids,
        },
    )

    # Broadcast WebSocket append_complete to target idea group
    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        channel_layer = get_channel_layer()
        if channel_layer:
            payload = {
                "merge_request_id": merge_request_id,
                "target_idea_id": target_idea_id,
                "requesting_idea_id": requesting_idea_id,
            }
            async_to_sync(channel_layer.group_send)(
                f"idea_{target_idea_id}",
                {"type": "append_complete", "payload": payload},
            )
    except Exception:
        logger.exception("Failed to broadcast WS append_complete")
