"""Merge execution service — creates merged idea with co-owners and transferred collaborators.

Mirrors services/core/apps/similarity/merge_service.py for test discoverability.

Consumes merge_synthesizer.complete events and atomically:
1. Creates a new merged idea with co-ownership
2. Inserts synthesis message as first AI chat message
3. Processes board instructions from Merge Synthesizer
4. Transfers all collaborators (deduplicated, excluding owners)
5. Updates original ideas with closed_by_merge_id
6. Updates merge_request with resulting_idea_id
7. Publishes merge.complete event
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from django.db import transaction
from django.utils import timezone as dj_timezone

logger = logging.getLogger(__name__)


def execute_merge(
    merge_request_id: str,
    requesting_idea_id: str,
    target_idea_id: str,
    synthesis_message: str,
    board_instructions: list[dict[str, Any]],
) -> dict[str, Any]:
    """Create a merged idea from two source ideas.

    This is the core merge execution logic. It runs atomically inside
    a database transaction.

    Returns:
        Dict with resulting_idea_id and collaborator_ids.
    """
    from apps.ideas.models import ChatMessage, Idea
    from apps.similarity.models import MergeRequest

    demoted_co_owner_ids: list[uuid.UUID] = []

    with transaction.atomic():
        # 1. Fetch both ideas
        idea_a = Idea.objects.get(id=requesting_idea_id, deleted_at__isnull=True)
        idea_b = Idea.objects.get(id=target_idea_id, deleted_at__isnull=True)

        # 2. Fetch merge request
        merge_req = MergeRequest.objects.select_for_update().get(id=merge_request_id)

        # 3. Determine triggering owners and demoted co-owners (recursive merge)
        # Triggering owners: requesting idea owner + target idea owner → co-owners
        triggering_owner_ids = {idea_a.owner_id, idea_b.owner_id}

        # Non-triggering co-owners get demoted to collaborators
        for co_owner_id in (idea_a.co_owner_id, idea_b.co_owner_id):
            if co_owner_id is not None and co_owner_id not in triggering_owner_ids:
                demoted_co_owner_ids.append(co_owner_id)

        # 4. Create new merged idea (max 2 owners enforced)
        merged_idea = Idea.objects.create(
            title=f"Merged: {idea_a.title} + {idea_b.title}",
            state="open",
            visibility="collaborating",
            owner_id=idea_a.owner_id,
            co_owner_id=idea_b.owner_id,
            merged_from_idea_1_id=idea_a.id,
            merged_from_idea_2_id=idea_b.id,
        )

        # 5. First chat message: synthesis_message from Merge Synthesizer
        ChatMessage.objects.create(
            idea_id=merged_idea.id,
            sender_type="ai",
            ai_agent="merge_synthesizer",
            content=synthesis_message,
        )

        # 6. Process board instructions — create board nodes
        _process_board_instructions(merged_idea.id, board_instructions)

        # 7. Transfer collaborators from both ideas (deduplicated, excluding new owners)
        owner_ids = triggering_owner_ids
        collaborator_ids = _transfer_collaborators(
            merged_idea.id, idea_a.id, idea_b.id, owner_ids
        )

        # 8. Add demoted co-owners as collaborators (deduplicated)
        if demoted_co_owner_ids:
            from apps.ideas.models import IdeaCollaborator

            IdeaCollaborator.objects.bulk_create(
                [
                    IdeaCollaborator(idea_id=merged_idea.id, user_id=uid)
                    for uid in demoted_co_owner_ids
                ],
                ignore_conflicts=True,
            )
            # Add demoted to collaborator list (deduplicated)
            existing = set(collaborator_ids)
            for uid in demoted_co_owner_ids:
                if uid not in existing:
                    collaborator_ids.append(uid)
                    existing.add(uid)

        # 9. Update original ideas: closed_by_merge_id
        Idea.objects.filter(id__in=[idea_a.id, idea_b.id]).update(
            closed_by_merge_id=merged_idea.id,
        )

        # 10. Update merge_request: status='accepted', resulting_idea_id, resolved_at
        merge_req.status = "accepted"
        merge_req.resulting_idea_id = merged_idea.id
        merge_req.resolved_at = dj_timezone.now()
        merge_req.save(
            update_fields=["status", "resulting_idea_id", "resolved_at"]
        )

    # 11. Publish merge.complete event (outside transaction)
    all_collaborator_ids = [str(uid) for uid in collaborator_ids]
    _publish_merge_complete(
        merge_request_id=merge_request_id,
        resulting_idea_id=str(merged_idea.id),
        original_idea_1_id=requesting_idea_id,
        original_idea_2_id=target_idea_id,
        all_collaborators=all_collaborator_ids,
        owner_ids=[str(uid) for uid in owner_ids],
        demoted_co_owners=[str(uid) for uid in demoted_co_owner_ids],
    )

    logger.info(
        "Merge complete: MR %s -> new idea %s",
        merge_request_id,
        merged_idea.id,
    )

    return {
        "resulting_idea_id": str(merged_idea.id),
        "collaborator_ids": all_collaborator_ids,
    }


def _process_board_instructions(
    idea_id: uuid.UUID, instructions: list[dict[str, Any]]
) -> list:
    """Process board instructions from Merge Synthesizer to create board nodes."""
    from apps.board.models import BoardNode

    created_nodes = []
    for instruction in instructions:
        intent = instruction.get("intent", "create_node")
        if intent in ("create_node", "add_node"):
            node = BoardNode.objects.create(
                idea_id=idea_id,
                node_type=instruction.get("node_type", "box"),
                title=instruction.get("suggested_title", ""),
                body=instruction.get("suggested_content", ""),
                created_by="ai",
                ai_modified_indicator=True,
            )
            created_nodes.append(node)
    return created_nodes


def _transfer_collaborators(
    merged_idea_id: uuid.UUID,
    idea_a_id: uuid.UUID,
    idea_b_id: uuid.UUID,
    owner_ids: set[uuid.UUID],
) -> list[uuid.UUID]:
    """Transfer collaborators from both ideas, deduplicated, excluding owners."""
    from apps.ideas.models import IdeaCollaborator

    # Get all collaborator user_ids from both ideas
    collab_a = set(
        IdeaCollaborator.objects.filter(idea_id=idea_a_id).values_list(
            "user_id", flat=True
        )
    )
    collab_b = set(
        IdeaCollaborator.objects.filter(idea_id=idea_b_id).values_list(
            "user_id", flat=True
        )
    )

    # Union, excluding owners (they become co-owners)
    all_collabs = (collab_a | collab_b) - owner_ids

    # Bulk create
    IdeaCollaborator.objects.bulk_create(
        [
            IdeaCollaborator(idea_id=merged_idea_id, user_id=uid)
            for uid in all_collabs
        ],
        ignore_conflicts=True,
    )

    return list(all_collabs)


def _publish_merge_complete(
    merge_request_id: str,
    resulting_idea_id: str,
    original_idea_1_id: str,
    original_idea_2_id: str,
    all_collaborators: list[str],
    owner_ids: list[str],
    demoted_co_owners: list[str] | None = None,
) -> None:
    """Publish merge.complete event for notifications."""
    from events.publisher import publish_event

    publish_event(
        event_type="notification.similarity.merge_complete",
        payload={
            "merge_request_id": merge_request_id,
            "resulting_idea_id": resulting_idea_id,
            "original_idea_1_id": original_idea_1_id,
            "original_idea_2_id": original_idea_2_id,
            "all_collaborators": all_collaborators,
            "owner_ids": owner_ids,
            "demoted_co_owners": demoted_co_owners or [],
        },
    )
