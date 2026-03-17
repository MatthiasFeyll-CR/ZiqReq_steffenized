"""Context window assembly from gRPC data.

Assembles the context dict that the Facilitator agent needs:
  - project metadata (title, state, agent_mode, title_manually_edited)
  - recent messages (last N from admin param)
  - chat summary (from chat_context_summaries if exists)
  - facilitator bucket content
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ContextAssembler:
    """Build the input_data dict for FacilitatorAgent.process() from raw gRPC response."""

    def assemble(self, project_id: str, project_context_response: dict[str, Any]) -> dict[str, Any]:
        """Assemble context from GetProjectContext gRPC response.

        Args:
            project_id: The project UUID string.
            project_context_response: Raw dict from CoreClient.get_project_context().

        Returns:
            Dict ready to pass to FacilitatorAgent.process().
        """
        project = project_context_response.get("project", {})
        recent_messages = project_context_response.get("recent_messages", [])
        chat_summary = project_context_response.get("chat_summary")
        facilitator_bucket = project_context_response.get("facilitator_bucket_content", "")

        assembled = {
            "project_id": project_id,
            "project_context": {
                "title": project.get("title", ""),
                "state": project.get("state", "open"),
                "agent_mode": project.get("agent_mode", "interactive"),
                "title_manually_edited": project.get("title_manually_edited", False),
            },
            "recent_messages": recent_messages,
            "chat_summary": chat_summary,
            "facilitator_bucket_content": facilitator_bucket,
            "delegation_results": None,
            "extension_results": None,
        }

        logger.info(
            "Assembled context for project %s: %d messages, summary=%s",
            project_id,
            len(recent_messages),
            "yes" if chat_summary else "no",
        )
        return assembled
