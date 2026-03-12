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
        from django.db import connection

        # Load idea metadata
        idea = {}
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, state, owner_id FROM ideas WHERE id = %s AND deleted_at IS NULL",
                [idea_id],
            )
            row = cursor.fetchone()
            if row:
                idea = {
                    "id": str(row[0]),
                    "title": row[1] or "",
                    "state": row[2] or "brainstorming",
                    "owner_id": str(row[3]) if row[3] else "",
                }

        # Load recent chat messages
        recent_messages: list[dict[str, Any]] = []
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, sender_type, sender_id, ai_agent, content, message_type, created_at "
                "FROM chat_messages WHERE idea_id = %s ORDER BY created_at DESC LIMIT %s",
                [idea_id, recent_message_limit],
            )
            rows = cursor.fetchall()
            for row in reversed(rows):  # oldest first
                recent_messages.append({
                    "id": str(row[0]),
                    "sender_type": row[1],
                    "sender_id": str(row[2]) if row[2] else None,
                    "ai_agent": row[3],
                    "content": row[4],
                    "message_type": row[5],
                    "created_at": row[6].isoformat() if row[6] else "",
                    "sender_name": row[3] if row[1] == "ai" else "User",
                })

        # Load chat summary if exists
        chat_summary = None
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT summary_text, compression_iteration FROM chat_context_summaries "
                "WHERE idea_id = %s ORDER BY created_at DESC LIMIT 1",
                [idea_id],
            )
            row = cursor.fetchone()
            if row:
                chat_summary = {
                    "summary_text": row[0],
                    "compression_iteration": row[1],
                }

        return {
            "idea": idea,
            "recent_messages": recent_messages,
            "board_state": {"nodes": [], "connections": []},
            "chat_summary": chat_summary,
        }

    def get_full_chat_history(self, idea_id: str) -> dict[str, Any]:
        logger.warning("AI CoreClient.get_full_chat_history stub called")
        return {"messages": []}

    def get_admin_parameter(self, key: str) -> dict[str, Any]:
        """Fetch a single admin parameter by key."""
        logger.warning("AI CoreClient.get_admin_parameter stub called for key=%s", key)
        return {"key": key, "value": ""}

    def get_rate_limit_status(self, idea_id: str) -> dict[str, Any]:
        logger.warning("AI CoreClient.get_rate_limit_status stub called")
        return {"current_count": 0, "cap": 100, "is_locked": False}

    # ── Board operations (stubs — gRPC wire-up in later milestones) ──

    def get_board_state(self, idea_id: str) -> dict[str, Any]:
        logger.warning("AI CoreClient.get_board_state stub called")
        return {"nodes": [], "connections": []}

    def create_board_node(
        self,
        idea_id: str,
        node_type: str,
        title: str,
        body: str = "",
        position_x: float = 0.0,
        position_y: float = 0.0,
        width: float | None = None,
        height: float | None = None,
        parent_id: str | None = None,
    ) -> dict[str, Any]:
        logger.warning("AI CoreClient.create_board_node stub called")
        import uuid

        return {"node_id": str(uuid.uuid4()), "created_at": None}

    def update_board_node(
        self,
        node_id: str,
        title: str | None = None,
        body: str | None = None,
    ) -> dict[str, Any]:
        logger.warning("AI CoreClient.update_board_node stub called")
        updated = [k for k in ("title", "body") if locals()[k] is not None]
        return {"updated_fields": updated}

    def delete_board_node(self, node_id: str) -> dict[str, Any]:
        logger.warning("AI CoreClient.delete_board_node stub called")
        return {"success": True, "detached_children": []}

    def move_board_node(
        self,
        node_id: str,
        position_x: float,
        position_y: float,
        new_parent_id: str | None = None,
    ) -> dict[str, Any]:
        logger.warning("AI CoreClient.move_board_node stub called")
        return {"parent_changed": new_parent_id is not None}

    def resize_board_group(
        self,
        node_id: str,
        width: float,
        height: float,
    ) -> dict[str, Any]:
        logger.warning("AI CoreClient.resize_board_group stub called")
        return {"success": True}

    def create_board_connection(
        self,
        idea_id: str,
        source_node_id: str,
        target_node_id: str,
        label: str = "",
    ) -> dict[str, Any]:
        logger.warning("AI CoreClient.create_board_connection stub called")
        import uuid

        return {"connection_id": str(uuid.uuid4())}

    def update_board_connection(
        self,
        connection_id: str,
        label: str,
    ) -> dict[str, Any]:
        logger.warning("AI CoreClient.update_board_connection stub called")
        return {"success": True}

    def delete_board_connection(self, connection_id: str) -> dict[str, Any]:
        logger.warning("AI CoreClient.delete_board_connection stub called")
        return {"success": True}

    # ── Keywords & embeddings (stubs — gRPC wire-up in later milestones) ──

    def upsert_keywords(
        self,
        idea_id: str,
        keywords: list[str],
    ) -> dict[str, Any]:
        logger.warning("AI CoreClient.upsert_keywords stub called")
        return {"success": True}

    def upsert_idea_embedding(
        self,
        idea_id: str,
        embedding: list[float],
        source_text_hash: str,
    ) -> dict[str, Any]:
        logger.warning("AI CoreClient.upsert_idea_embedding stub called")
        return {"success": True}

    # ── BRD operations (stubs — gRPC wire-up in later milestones) ──

    def get_brd_draft(self, idea_id: str) -> dict[str, Any]:
        """Fetch the current BRD draft for an idea.

        Returns dict with section_locks (dict) and allow_information_gaps (bool).
        """
        logger.warning("AI CoreClient.get_brd_draft stub called for idea_id=%s", idea_id)
        return {
            "id": None,
            "idea_id": idea_id,
            "section_locks": {},
            "allow_information_gaps": False,
        }

    def upsert_brd_draft(
        self,
        idea_id: str,
        sections: dict[str, Any],
        readiness_evaluation: dict[str, str],
    ) -> dict[str, Any]:
        """Create or update a BRD draft for an idea."""
        logger.warning("AI CoreClient.upsert_brd_draft stub called for idea_id=%s", idea_id)
        return {"success": True}

    # ── Context compression (stubs — gRPC wire-up in later milestones) ──

    def upsert_context_summary(
        self,
        idea_id: str,
        summary_text: str,
        messages_covered_up_to_id: str,
        compression_iteration: int,
        context_window_usage: float,
    ) -> dict[str, Any]:
        logger.warning("AI CoreClient.upsert_context_summary stub called")
        return {"success": True}
