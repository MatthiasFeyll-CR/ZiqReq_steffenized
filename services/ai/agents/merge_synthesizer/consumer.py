"""Consume merge_request.accepted events from message broker.

Invokes the Merge Synthesizer Agent and publishes merge_synthesizer.complete
events with the synthesis output.
"""

from __future__ import annotations

import logging
from typing import Any

from agents.merge_synthesizer.agent import MergeSynthesizerAgent
from grpc_clients.core_client import CoreClient

logger = logging.getLogger(__name__)


async def handle_merge_request_accepted(payload: dict[str, Any]) -> dict[str, Any]:
    """Handle a merge_request.accepted event.

    Fetches full context for both ideas, invokes the Merge Synthesizer Agent,
    and publishes merge_synthesizer.complete with the synthesis output.

    Args:
        payload: Event payload with merge_request_id, requesting_idea_id,
                 target_idea_id.

    Returns:
        Dict with agent result and whether a complete event was published.
    """
    from events.publishers import publish_event

    merge_request_id: str = payload["merge_request_id"]
    requesting_idea_id: str = payload["requesting_idea_id"]
    target_idea_id: str = payload["target_idea_id"]

    logger.info(
        "[merge_consumer] Processing merge_request.accepted for MR %s (%s <-> %s)",
        merge_request_id,
        requesting_idea_id,
        target_idea_id,
    )

    core_client = CoreClient()

    idea_a_context = core_client.get_idea_context(requesting_idea_id)
    idea_b_context = core_client.get_idea_context(target_idea_id)

    idea_a = idea_a_context.get("idea", {})
    idea_b = idea_b_context.get("idea", {})

    input_data = {
        "idea_a_owner_name": idea_a.get("owner_name", "Owner A"),
        "idea_a_title": idea_a.get("title", ""),
        "idea_a_summary": idea_a_context.get("chat_summary", "") or "",
        "idea_a_board_nodes": _extract_board_nodes(
            idea_a_context.get("board_state", {})
        ),
        "idea_b_owner_name": idea_b.get("owner_name", "Owner B"),
        "idea_b_title": idea_b.get("title", ""),
        "idea_b_summary": idea_b_context.get("chat_summary", "") or "",
        "idea_b_board_nodes": _extract_board_nodes(
            idea_b_context.get("board_state", {})
        ),
    }

    agent = MergeSynthesizerAgent()
    result = await agent.process(input_data)

    published = False
    if result.get("synthesis_message") and result.get("board_instructions"):
        await publish_event(
            event_type="merge_synthesizer.complete",
            payload={
                "merge_request_id": merge_request_id,
                "requesting_idea_id": requesting_idea_id,
                "target_idea_id": target_idea_id,
                "synthesis_message": result["synthesis_message"],
                "board_instructions": result["board_instructions"],
            },
        )
        published = True
        logger.info(
            "[merge_consumer] Published merge_synthesizer.complete for MR %s",
            merge_request_id,
        )
    else:
        logger.error(
            "[merge_consumer] Synthesis failed for MR %s — empty output",
            merge_request_id,
        )

    return {"result": result, "published": published}


def _extract_board_nodes(board_state: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Extract board nodes from board state for agent input."""
    if not board_state:
        return []
    return board_state.get("nodes", [])
