"""Core service client — direct database access (AI service side).

All methods query the shared PostgreSQL database directly instead of
making gRPC calls, since all services share the same database.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class CoreClient:
    """Client for Core service data — uses direct DB access (AI service side)."""

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

        board_state = self.get_board_state(idea_id) if include_board else {"nodes": [], "connections": []}

        return {
            "idea": idea,
            "recent_messages": recent_messages,
            "board_state": board_state,
            "chat_summary": chat_summary,
        }

    def get_full_chat_history(self, idea_id: str) -> dict[str, Any]:
        from django.db import connection

        messages: list[dict[str, Any]] = []
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, sender_type, sender_id, ai_agent, content, message_type, created_at "
                "FROM chat_messages WHERE idea_id = %s ORDER BY created_at",
                [idea_id],
            )
            for row in cursor.fetchall():
                messages.append({
                    "id": str(row[0]),
                    "sender_type": row[1],
                    "sender_id": str(row[2]) if row[2] else None,
                    "ai_agent": row[3],
                    "content": row[4],
                    "message_type": row[5],
                    "created_at": row[6].isoformat() if row[6] else "",
                    "sender_name": row[3] if row[1] == "ai" else "User",
                })
        return {"messages": messages}

    def get_admin_parameter(self, key: str) -> dict[str, Any]:
        """Fetch a single admin parameter by key."""
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT value FROM admin_parameters WHERE key = %s",
                [key],
            )
            row = cursor.fetchone()
            if row:
                return {"key": key, "value": row[0]}
        return {"key": key, "value": ""}

    def get_rate_limit_status(self, idea_id: str) -> dict[str, Any]:
        from django.db import connection

        # Count user messages created after the last AI message (unprocessed messages)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM chat_messages "
                "WHERE idea_id = %s AND sender_type = 'user' "
                "AND created_at > COALESCE("
                "  (SELECT MAX(created_at) FROM chat_messages "
                "   WHERE idea_id = %s AND sender_type = 'ai'), "
                "  '1970-01-01'::timestamptz"
                ")",
                [idea_id, idea_id],
            )
            current_count = cursor.fetchone()[0]

        # Read cap from admin_parameters (chat_message_cap, default 5)
        cap = 5
        cap_result = self.get_admin_parameter("chat_message_cap")
        if cap_result["value"]:
            try:
                cap = int(cap_result["value"])
            except (ValueError, TypeError):
                pass

        return {
            "current_count": current_count,
            "cap": cap,
            "is_locked": current_count >= cap,
        }

    # ── Board operations ──

    def get_board_state(self, idea_id: str) -> dict[str, Any]:
        from django.db import connection

        nodes: list[dict[str, Any]] = []
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, node_type, title, body, position_x, position_y, "
                "width, height, parent_id, is_locked, created_by, created_at "
                "FROM board_nodes WHERE idea_id = %s ORDER BY created_at",
                [idea_id],
            )
            for row in cursor.fetchall():
                nodes.append({
                    "id": str(row[0]),
                    "node_type": row[1],
                    "title": row[2] or "",
                    "body": row[3] or "",
                    "position_x": row[4],
                    "position_y": row[5],
                    "width": row[6],
                    "height": row[7],
                    "parent_id": str(row[8]) if row[8] else None,
                    "is_locked": row[9],
                    "created_by": row[10],
                    "created_at": row[11].isoformat() if row[11] else "",
                })

        connections: list[dict[str, Any]] = []
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, source_node_id, target_node_id, label, created_at "
                "FROM board_connections WHERE idea_id = %s ORDER BY created_at",
                [idea_id],
            )
            for row in cursor.fetchall():
                connections.append({
                    "id": str(row[0]),
                    "source_node_id": str(row[1]),
                    "target_node_id": str(row[2]),
                    "label": row[3] or "",
                    "created_at": row[4].isoformat() if row[4] else "",
                })

        return {"nodes": nodes, "connections": connections}

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
        import uuid as _uuid

        from django.db import connection

        node_id = str(_uuid.uuid4())
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO board_nodes "
                "(id, idea_id, node_type, title, body, position_x, position_y, "
                "width, height, parent_id, is_locked, created_by, ai_modified_indicator, "
                "created_at, updated_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, false, 'ai', false, NOW(), NOW()) "
                "RETURNING created_at",
                [node_id, idea_id, node_type, title, body, position_x, position_y,
                 width, height, parent_id],
            )
            row = cursor.fetchone()
            created_at = row[0].isoformat() if row else None

        logger.info("Created board node %s for idea %s", node_id, idea_id)
        return {
            "node_id": node_id,
            "id": node_id,
            "idea_id": idea_id,
            "node_type": node_type,
            "title": title,
            "body": body,
            "position_x": position_x,
            "position_y": position_y,
            "width": width,
            "height": height,
            "parent_id": parent_id,
            "is_locked": False,
            "created_by": "ai",
            "created_at": created_at,
        }

    def update_board_node(
        self,
        node_id: str,
        title: str | None = None,
        body: str | None = None,
    ) -> dict[str, Any]:
        from django.db import connection

        updates = []
        params: list[Any] = []
        if title is not None:
            updates.append("title = %s")
            params.append(title)
        if body is not None:
            updates.append("body = %s")
            params.append(body)

        if not updates:
            return {"node_id": node_id, "title": None, "body": None}

        updates.append("updated_at = NOW()")
        params.append(node_id)

        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE board_nodes SET {', '.join(updates)} WHERE id = %s",
                params,
            )

        logger.info("Updated board node %s fields: %s", node_id,
                     [k for k, v in [("title", title), ("body", body)] if v is not None])
        return {"node_id": node_id, "title": title, "body": body}

    def delete_board_node(self, node_id: str) -> dict[str, Any]:
        from django.db import connection

        # Detach children first
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE board_nodes SET parent_id = NULL, updated_at = NOW() "
                "WHERE parent_id = %s RETURNING id",
                [node_id],
            )
            detached = [str(r[0]) for r in cursor.fetchall()]

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM board_nodes WHERE id = %s", [node_id])

        logger.info("Deleted board node %s, detached children: %s", node_id, detached)
        return {"success": True, "detached_children": detached}

    def move_board_node(
        self,
        node_id: str,
        position_x: float,
        position_y: float,
        new_parent_id: str | None = None,
    ) -> dict[str, Any]:
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE board_nodes SET position_x = %s, position_y = %s, "
                "parent_id = %s, updated_at = NOW() WHERE id = %s",
                [position_x, position_y, new_parent_id, node_id],
            )

        logger.info("Moved board node %s to (%.1f, %.1f)", node_id, position_x, position_y)
        return {
            "node_id": node_id,
            "parent_changed": new_parent_id is not None,
            "position_x": position_x,
            "position_y": position_y,
            "new_parent_id": new_parent_id,
        }

    def resize_board_group(
        self,
        node_id: str,
        width: float,
        height: float,
    ) -> dict[str, Any]:
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE board_nodes SET width = %s, height = %s, updated_at = NOW() "
                "WHERE id = %s",
                [width, height, node_id],
            )

        logger.info("Resized board group %s to %.1fx%.1f", node_id, width, height)
        return {"success": True, "node_id": node_id, "width": width, "height": height}

    def create_board_connection(
        self,
        idea_id: str,
        source_node_id: str,
        target_node_id: str,
        label: str = "",
    ) -> dict[str, Any]:
        import uuid as _uuid

        from django.db import connection

        conn_id = str(_uuid.uuid4())
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO board_connections "
                "(id, idea_id, source_node_id, target_node_id, label, created_at, updated_at) "
                "VALUES (%s, %s, %s, %s, %s, NOW(), NOW())",
                [conn_id, idea_id, source_node_id, target_node_id, label],
            )

        logger.info("Created board connection %s for idea %s", conn_id, idea_id)
        return {
            "connection_id": conn_id,
            "id": conn_id,
            "source_node_id": source_node_id,
            "target_node_id": target_node_id,
            "label": label,
        }

    def update_board_connection(
        self,
        connection_id: str,
        label: str,
    ) -> dict[str, Any]:
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE board_connections SET label = %s, updated_at = NOW() WHERE id = %s",
                [label, connection_id],
            )

        logger.info("Updated board connection %s", connection_id)
        return {"success": True}

    def delete_board_connection(self, connection_id: str) -> dict[str, Any]:
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM board_connections WHERE id = %s", [connection_id])

        logger.info("Deleted board connection %s", connection_id)
        return {"success": True}

    # ── Keywords & embeddings ──

    def upsert_keywords(
        self,
        idea_id: str,
        keywords: list[str],
    ) -> dict[str, Any]:
        """Persist keywords for an idea (insert or update)."""
        from django.db import connection as db_conn

        try:
            with db_conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO idea_keywords (id, idea_id, keywords, last_updated_at) "
                    "VALUES (gen_random_uuid(), %s, %s, NOW()) "
                    "ON CONFLICT (idea_id) DO UPDATE SET keywords = EXCLUDED.keywords, "
                    "last_updated_at = NOW()",
                    [idea_id, keywords],
                )
            logger.info("Upserted %d keywords for idea %s", len(keywords), idea_id)
            return {"success": True}
        except Exception:
            logger.exception("Failed to upsert keywords for idea %s", idea_id)
            return {"success": False}

    def upsert_idea_embedding(
        self,
        idea_id: str,
        embedding: list[float],
        source_text_hash: str,
    ) -> dict[str, Any]:
        """Persist idea embedding vector (insert or update)."""
        from django.db import connection as db_conn

        try:
            with db_conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO idea_embeddings (id, idea_id, embedding, source_text_hash, updated_at) "
                    "VALUES (gen_random_uuid(), %s, %s, %s, NOW()) "
                    "ON CONFLICT (idea_id) DO UPDATE SET embedding = EXCLUDED.embedding, "
                    "source_text_hash = EXCLUDED.source_text_hash, updated_at = NOW()",
                    [idea_id, embedding, source_text_hash],
                )
            logger.info("Upserted embedding for idea %s", idea_id)
            return {"success": True}
        except Exception:
            logger.exception("Failed to upsert embedding for idea %s", idea_id)
            return {"success": False}

    # ── BRD operations ──

    def get_brd_draft(self, idea_id: str) -> dict[str, Any]:
        """Fetch the current BRD draft for an idea."""
        from django.db import connection as db_conn

        with db_conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, section_locks, allow_information_gaps "
                "FROM brd_drafts WHERE idea_id = %s",
                [idea_id],
            )
            row = cursor.fetchone()
            if row:
                locks = row[1] or {}
                if isinstance(locks, str):
                    import json
                    locks = json.loads(locks)
                return {
                    "id": str(row[0]),
                    "idea_id": idea_id,
                    "section_locks": locks,
                    "allow_information_gaps": row[2],
                }
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
        import json

        from django.db import connection as db_conn

        field_map = {
            "title": "section_title",
            "short_description": "section_short_description",
            "current_workflow": "section_current_workflow",
            "affected_department": "section_affected_department",
            "core_capabilities": "section_core_capabilities",
            "success_criteria": "section_success_criteria",
        }

        # Build the SET clause for upserted fields
        set_parts = []
        values: list[Any] = []
        for key, field in field_map.items():
            if key in sections:
                set_parts.append(f"{field} = %s")
                values.append(sections[key])

        readiness_json = json.dumps(readiness_evaluation) if readiness_evaluation else "{}"
        set_parts.append("readiness_evaluation = %s")
        values.append(readiness_json)
        set_parts.append("updated_at = NOW()")

        try:
            with db_conn.cursor() as cursor:
                # Try update first
                if set_parts:
                    cursor.execute(
                        f"UPDATE brd_drafts SET {', '.join(set_parts)} WHERE idea_id = %s",
                        values + [idea_id],
                    )
                    if cursor.rowcount == 0:
                        # Insert new draft with section content
                        insert_fields = ["id", "idea_id", "section_locks",
                                         "allow_information_gaps", "readiness_evaluation",
                                         "created_at", "updated_at"]
                        insert_values: list[Any] = [idea_id, "{}", False, readiness_json]
                        for key, field in field_map.items():
                            if key in sections:
                                insert_fields.append(field)
                                insert_values.append(sections[key])
                        placeholders = ", ".join([
                            "gen_random_uuid()", "%s", "%s", "%s", "%s", "NOW()", "NOW()"
                        ] + ["%s"] * (len(insert_fields) - 7))
                        cursor.execute(
                            f"INSERT INTO brd_drafts ({', '.join(insert_fields)}) "
                            f"VALUES ({placeholders})",
                            insert_values,
                        )
            logger.info("Upserted BRD draft for idea %s", idea_id)
            return {"success": True}
        except Exception:
            logger.exception("Failed to upsert BRD draft for idea %s", idea_id)
            return {"success": False}

    # ── Context compression ──

    def upsert_context_summary(
        self,
        idea_id: str,
        summary_text: str,
        messages_covered_up_to_id: str,
        compression_iteration: int,
        context_window_usage: float,
    ) -> dict[str, Any]:
        """Persist a context compression summary."""
        from django.db import connection as db_conn

        try:
            with db_conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO chat_context_summaries "
                    "(id, idea_id, summary_text, messages_covered_up_to_id, "
                    "compression_iteration, context_window_usage_at_compression, created_at) "
                    "VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, NOW())",
                    [idea_id, summary_text, messages_covered_up_to_id,
                     compression_iteration, context_window_usage],
                )
            logger.info("Persisted context summary for idea %s (iteration %d)", idea_id, compression_iteration)
            return {"success": True}
        except Exception:
            logger.exception("Failed to persist context summary for idea %s", idea_id)
            return {"success": False}
