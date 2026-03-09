"""gRPC client for Core service (used by AI service).

Provides typed methods for CoreService RPCs needed by the AI service.
Full implementations will connect to the gRPC channel in later milestones.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class CoreClient:
    """gRPC client for Core service (AI service side)."""

    def __init__(self, address: str = "localhost:50051") -> None:
        self.address = address

    def get_idea_context(
        self,
        idea_id: str,
        recent_message_limit: int = 20,
        include_board: bool = True,
        include_brd_draft: bool = False,
    ) -> dict[str, Any]:
        logger.warning("AI CoreClient.get_idea_context stub called")
        return {}

    def get_full_chat_history(self, idea_id: str) -> dict[str, Any]:
        logger.warning("AI CoreClient.get_full_chat_history stub called")
        return {"messages": []}

    def get_rate_limit_status(self, idea_id: str) -> dict[str, Any]:
        logger.warning("AI CoreClient.get_rate_limit_status stub called")
        return {"current_count": 0, "cap": 100, "is_locked": False}
