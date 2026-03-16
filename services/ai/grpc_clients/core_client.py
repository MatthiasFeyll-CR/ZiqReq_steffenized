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
