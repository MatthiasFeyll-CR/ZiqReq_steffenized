"""Consume similarity.detected events from message broker.

Invokes the Deep Comparison Agent and publishes ai.similarity.confirmed
events when genuine similarity is confirmed.
"""

from __future__ import annotations

import logging
from typing import Any

from agents.deep_comparison.agent import CONFIDENCE_THRESHOLD, DeepComparisonAgent
from grpc_clients.core_client import CoreClient

logger = logging.getLogger(__name__)


async def handle_similarity_detected(payload: dict[str, Any]) -> dict[str, Any]:
    """Handle a similarity.detected event.

    Fetches idea summaries for both ideas, invokes the Deep Comparison Agent,
    and publishes ai.similarity.confirmed if the agent confirms similarity
    with confidence >= 0.7.

    Args:
        payload: Event payload with requesting_idea_id, target_idea_id,
                 and keyword_overlap_count or similarity_score.

    Returns:
        Dict with agent result and whether a confirmed event was published.
    """
    from events.publishers import publish_event

    requesting_idea_id: str = payload["requesting_idea_id"]
    target_idea_id: str = payload["target_idea_id"]

    logger.info(
        "[similarity_consumer] Processing similarity.detected for %s <-> %s",
        requesting_idea_id,
        target_idea_id,
    )

    core_client = CoreClient()

    idea_a_context = core_client.get_idea_context(requesting_idea_id)
    idea_b_context = core_client.get_idea_context(target_idea_id)

    idea_a = idea_a_context.get("idea", {})
    idea_b = idea_b_context.get("idea", {})

    input_data = {
        "idea_a_title": idea_a.get("title", ""),
        "idea_a_keywords": idea_a.get("keywords", []),
        "idea_a_chat_summary": idea_a_context.get("chat_summary", "") or "",
        "idea_a_board_summary": _format_board_summary(
            idea_a_context.get("board_state", {})
        ),
        "idea_b_title": idea_b.get("title", ""),
        "idea_b_keywords": idea_b.get("keywords", []),
        "idea_b_chat_summary": idea_b_context.get("chat_summary", "") or "",
        "idea_b_board_summary": _format_board_summary(
            idea_b_context.get("board_state", {})
        ),
    }

    agent = DeepComparisonAgent()
    result = await agent.process(input_data)

    confirmed = False
    if result.get("is_similar") and result.get("confidence", 0) >= CONFIDENCE_THRESHOLD:
        await publish_event(
            event_type="ai.similarity.confirmed",
            payload={
                "requesting_idea_id": requesting_idea_id,
                "target_idea_id": target_idea_id,
                "requesting_idea_state": idea_a.get("state", "open"),
                "target_idea_state": idea_b.get("state", "open"),
                "confidence": result["confidence"],
                "overlap_areas": result.get("overlap_areas", []),
            },
        )
        confirmed = True
        logger.info(
            "[similarity_consumer] Confirmed similarity: %s <-> %s (confidence=%.2f)",
            requesting_idea_id,
            target_idea_id,
            result["confidence"],
        )
    else:
        logger.info(
            "[similarity_consumer] Dismissed: %s <-> %s (is_similar=%s, confidence=%.2f)",
            requesting_idea_id,
            target_idea_id,
            result.get("is_similar"),
            result.get("confidence", 0),
        )

    return {"result": result, "confirmed": confirmed}


def _format_board_summary(board_state: dict[str, Any] | None) -> str:
    """Format board state into a text summary for the agent."""
    if not board_state:
        return ""
    nodes = board_state.get("nodes", [])
    if not nodes:
        return ""
    parts = []
    for node in nodes:
        title = node.get("title", "")
        body = node.get("body", "")
        if title:
            parts.append(f"- {title}: {body}" if body else f"- {title}")
    return "\n".join(parts)
