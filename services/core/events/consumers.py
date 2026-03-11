"""Consume events from other services."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def handle_merge_synthesizer_complete(payload: dict[str, Any]) -> dict[str, Any]:
    """Handle merge_synthesizer.complete event.

    Invokes the merge execution service to create the merged idea.

    Args:
        payload: Event payload with merge_request_id, requesting_idea_id,
                 target_idea_id, synthesis_message, board_instructions.

    Returns:
        Dict with resulting_idea_id.
    """
    from apps.similarity.merge_service import execute_merge

    merge_request_id: str = payload["merge_request_id"]
    requesting_idea_id: str = payload["requesting_idea_id"]
    target_idea_id: str = payload["target_idea_id"]
    synthesis_message: str = payload["synthesis_message"]
    board_instructions: list[dict[str, Any]] = payload.get("board_instructions", [])

    logger.info(
        "[merge_consumer] Processing merge_synthesizer.complete for MR %s",
        merge_request_id,
    )

    result = execute_merge(
        merge_request_id=merge_request_id,
        requesting_idea_id=requesting_idea_id,
        target_idea_id=target_idea_id,
        synthesis_message=synthesis_message,
        board_instructions=board_instructions,
    )

    logger.info(
        "[merge_consumer] Merge complete for MR %s -> %s",
        merge_request_id,
        result["resulting_idea_id"],
    )

    return result
