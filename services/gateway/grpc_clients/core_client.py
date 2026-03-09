"""gRPC client for Core service.

Provides typed methods for all CoreService RPCs.
Full implementations will connect to the gRPC channel in later milestones.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class CoreClient:
    """gRPC client for Core service."""

    def __init__(self, address: str = "localhost:50051") -> None:
        self.address = address

    def get_idea_context(
        self,
        idea_id: str,
        recent_message_limit: int = 20,
        include_board: bool = True,
        include_brd_draft: bool = False,
    ) -> dict[str, Any]:
        logger.warning("CoreClient.get_idea_context stub called")
        return {}

    def get_full_chat_history(self, idea_id: str) -> dict[str, Any]:
        logger.warning("CoreClient.get_full_chat_history stub called")
        return {"messages": []}

    def persist_ai_chat_message(
        self,
        idea_id: str,
        content: str,
        message_type: str = "regular",
        language: str = "de",
        processing_id: str = "",
    ) -> dict[str, Any]:
        logger.warning("CoreClient.persist_ai_chat_message stub called")
        return {"message_id": "", "created_at": ""}

    def persist_ai_reaction(
        self, idea_id: str, message_id: str, reaction_type: str
    ) -> dict[str, Any]:
        logger.warning("CoreClient.persist_ai_reaction stub called")
        return {"reaction_id": ""}

    def update_idea_title(
        self, idea_id: str, new_title: str
    ) -> dict[str, Any]:
        logger.warning("CoreClient.update_idea_title stub called")
        return {"success": True}

    def persist_board_mutations(
        self, idea_id: str, mutations: list[dict[str, Any]]
    ) -> dict[str, Any]:
        logger.warning("CoreClient.persist_board_mutations stub called")
        return {"success": True, "mutations_applied": 0}

    def update_brd_draft(
        self,
        idea_id: str,
        sections: dict[str, str],
        readiness_evaluation_json: str = "",
    ) -> dict[str, Any]:
        logger.warning("CoreClient.update_brd_draft stub called")
        return {"success": True}

    def update_idea_keywords(
        self, idea_id: str, keywords: list[str]
    ) -> dict[str, Any]:
        logger.warning("CoreClient.update_idea_keywords stub called")
        return {"success": True}

    def get_ideas_by_state(self) -> dict[str, Any]:
        logger.warning("CoreClient.get_ideas_by_state stub called")
        return {"counts": []}

    def get_user_stats(self, user_id: str) -> dict[str, Any]:
        logger.warning("CoreClient.get_user_stats stub called")
        return {"idea_count": 0, "review_count": 0, "contribution_count": 0}

    def get_rate_limit_status(self, idea_id: str) -> dict[str, Any]:
        logger.warning("CoreClient.get_rate_limit_status stub called")
        return {"current_count": 0, "cap": 100, "is_locked": False}
