"""Context window assembly from gRPC data.

Assembles the context dict that the Facilitator agent needs:
  - idea metadata (title, state, agent_mode, title_manually_edited)
  - recent messages (last N from admin param)
  - board state (nodes + connections)
  - chat summary (from chat_context_summaries if exists)
  - facilitator bucket content
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ContextAssembler:
    """Build the input_data dict for FacilitatorAgent.process() from raw gRPC response."""

    def assemble(self, idea_id: str, idea_context_response: dict[str, Any]) -> dict[str, Any]:
        """Assemble context from GetIdeaContext gRPC response.

        Args:
            idea_id: The idea UUID string.
            idea_context_response: Raw dict from CoreClient.get_idea_context().

        Returns:
            Dict ready to pass to FacilitatorAgent.process().
        """
        idea = idea_context_response.get("idea", {})
        recent_messages = idea_context_response.get("recent_messages", [])
        board_state = idea_context_response.get("board_state", {})
        chat_summary = idea_context_response.get("chat_summary")
        facilitator_bucket = idea_context_response.get("facilitator_bucket_content", "")

        assembled = {
            "idea_id": idea_id,
            "idea_context": {
                "title": idea.get("title", ""),
                "state": idea.get("state", "brainstorming"),
                "agent_mode": idea.get("agent_mode", "interactive"),
                "title_manually_edited": idea.get("title_manually_edited", False),
            },
            "recent_messages": recent_messages,
            "board_state": board_state,
            "chat_summary": chat_summary,
            "facilitator_bucket_content": facilitator_bucket,
            "delegation_results": None,
            "extension_results": None,
        }

        logger.info(
            "Assembled context for idea %s: %d messages, summary=%s",
            idea_id,
            len(recent_messages),
            "yes" if chat_summary else "no",
        )
        return assembled
