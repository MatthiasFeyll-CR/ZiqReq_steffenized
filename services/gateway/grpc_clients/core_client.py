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
        from apps.ideas.models import ChatMessage

        message = ChatMessage.objects.create(
            idea_id=idea_id,
            sender_type="ai",
            sender_id=None,
            content=content,
            message_type=message_type,
            ai_agent="facilitator",
        )
        logger.info("Persisted AI chat message %s for idea %s", message.id, idea_id)
        return {
            "message_id": str(message.id),
            "created_at": message.created_at.isoformat(),
        }

    def persist_ai_reaction(
        self, idea_id: str, message_id: str, reaction_type: str
    ) -> dict[str, Any]:
        logger.warning("CoreClient.persist_ai_reaction stub called")
        return {"reaction_id": ""}

    def update_idea_title(
        self, idea_id: str, new_title: str
    ) -> dict[str, Any]:
        from apps.ideas.models import Idea

        updated = Idea.objects.filter(id=idea_id, deleted_at__isnull=True).update(
            title=new_title
        )
        if updated:
            logger.info("Updated title for idea %s", idea_id)
        else:
            logger.warning("Idea %s not found for title update", idea_id)
        return {"success": bool(updated)}

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
        import json
        from apps.brd.models import BrdDraft

        draft, _created = BrdDraft.objects.get_or_create(
            idea_id=idea_id,
            defaults={
                "section_locks": {},
                "allow_information_gaps": False,
                "readiness_evaluation": {},
            },
        )

        # Map section keys to model fields
        field_map = {
            "title": "section_title",
            "short_description": "section_short_description",
            "current_workflow": "section_current_workflow",
            "affected_department": "section_affected_department",
            "core_capabilities": "section_core_capabilities",
            "success_criteria": "section_success_criteria",
        }

        update_fields = ["updated_at"]
        for key, field in field_map.items():
            if key in sections:
                # Only update if the section is not locked
                locks = draft.section_locks or {}
                if not locks.get(key, False):
                    setattr(draft, field, sections[key])
                    update_fields.append(field)

        # Update readiness evaluation
        if readiness_evaluation_json:
            try:
                draft.readiness_evaluation = json.loads(readiness_evaluation_json) if isinstance(readiness_evaluation_json, str) else readiness_evaluation_json
            except (json.JSONDecodeError, TypeError):
                draft.readiness_evaluation = {}
            update_fields.append("readiness_evaluation")

        draft.save(update_fields=update_fields)
        logger.info("Updated BRD draft for idea %s", idea_id)
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
