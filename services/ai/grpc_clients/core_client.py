"""Core service client — direct database access (AI service side).

All methods query the shared PostgreSQL database directly instead of
making gRPC calls, since all services share the same database.
"""

from __future__ import annotations

import logging
import uuid as uuid_mod
from typing import Any

logger = logging.getLogger(__name__)


class MutationError(Exception):
    """Raised when a single mutation cannot be applied."""


class CoreClient:
    """Client for Core service data — uses direct DB access (AI service side)."""

    def __init__(self, address: str = "localhost:50051") -> None:
        self.address = address

    def get_project_context(
        self,
        project_id: str,
        recent_message_limit: int = 20,
        include_brd_draft: bool = False,
    ) -> dict[str, Any]:
        from django.db import connection

        # Load project metadata
        project = {}
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, state, owner_id FROM projects WHERE id = %s AND deleted_at IS NULL",
                [project_id],
            )
            row = cursor.fetchone()
            if row:
                project = {
                    "id": str(row[0]),
                    "title": row[1] or "",
                    "state": row[2] or "open",
                    "owner_id": str(row[3]) if row[3] else "",
                }

        # Load recent chat messages
        recent_messages: list[dict[str, Any]] = []
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, sender_type, sender_id, ai_agent, content, message_type, created_at "
                "FROM chat_messages WHERE project_id = %s ORDER BY created_at DESC LIMIT %s",
                [project_id, recent_message_limit],
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
                "WHERE project_id = %s ORDER BY created_at DESC LIMIT 1",
                [project_id],
            )
            row = cursor.fetchone()
            if row:
                chat_summary = {
                    "summary_text": row[0],
                    "compression_iteration": row[1],
                }

        return {
            "project": project,
            "recent_messages": recent_messages,
            "chat_summary": chat_summary,
        }

    def get_full_chat_history(self, project_id: str) -> dict[str, Any]:
        from django.db import connection

        messages: list[dict[str, Any]] = []
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, sender_type, sender_id, ai_agent, content, message_type, created_at "
                "FROM chat_messages WHERE project_id = %s ORDER BY created_at",
                [project_id],
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

    def get_rate_limit_status(self, project_id: str) -> dict[str, Any]:
        from django.db import connection

        # Count user messages created after the last AI message (unprocessed messages)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM chat_messages "
                "WHERE project_id = %s AND sender_type = 'user' "
                "AND created_at > COALESCE("
                "  (SELECT MAX(created_at) FROM chat_messages "
                "   WHERE project_id = %s AND sender_type = 'ai'), "
                "  '1970-01-01'::timestamptz"
                ")",
                [project_id, project_id],
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

    # ── Requirements operations ──

    def get_requirements_state(self, project_id: str) -> dict[str, Any]:
        """Fetch the current requirements draft for a project."""
        import json

        from django.db import connection as db_conn

        with db_conn.cursor() as cursor:
            cursor.execute(
                "SELECT title, short_description, structure, item_locks, "
                "allow_information_gaps, readiness_evaluation, updated_at "
                "FROM requirements_document_drafts WHERE project_id = %s",
                [project_id],
            )
            row = cursor.fetchone()
            if row:
                structure = row[2] or []
                if isinstance(structure, str):
                    structure = json.loads(structure)
                item_locks = row[3] or {}
                if isinstance(item_locks, str):
                    item_locks = json.loads(item_locks)
                readiness = row[5] or {}
                if isinstance(readiness, str):
                    readiness = json.loads(readiness)
                return {
                    "project_id": project_id,
                    "title": row[0] or "",
                    "short_description": row[1] or "",
                    "structure": structure,
                    "item_locks": item_locks,
                    "allow_information_gaps": row[4],
                    "readiness_evaluation": readiness,
                    "updated_at": row[6].isoformat() if row[6] else "",
                }
        return {
            "project_id": project_id,
            "title": "",
            "short_description": "",
            "structure": [],
            "item_locks": {},
            "allow_information_gaps": False,
            "readiness_evaluation": {},
            "updated_at": "",
        }

    def update_requirements_structure(
        self,
        project_id: str,
        structure: list,
        readiness_evaluation: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create or update requirements draft structure for a project."""
        import json

        from django.db import connection as db_conn

        structure_json = json.dumps(structure)
        readiness_json = json.dumps(readiness_evaluation) if readiness_evaluation else None

        try:
            with db_conn.cursor() as cursor:
                set_parts = ["structure = %s", "updated_at = NOW()"]
                values: list[Any] = [structure_json]

                if readiness_json is not None:
                    set_parts.append("readiness_evaluation = %s")
                    values.append(readiness_json)

                cursor.execute(
                    f"UPDATE requirements_document_drafts SET {', '.join(set_parts)} WHERE project_id = %s",
                    values + [project_id],
                )
                if cursor.rowcount == 0:
                    # Insert new draft
                    cursor.execute(
                        "INSERT INTO requirements_document_drafts "
                        "(id, project_id, title, short_description, structure, item_locks, "
                        "allow_information_gaps, readiness_evaluation, created_at, updated_at) "
                        "VALUES (gen_random_uuid(), %s, '', '', %s, '{}', false, %s, NOW(), NOW())",
                        [project_id, structure_json, readiness_json or "{}"],
                    )
            logger.info("Updated requirements structure for project %s", project_id)
            return {"success": True}
        except Exception:
            logger.exception("Failed to update requirements structure for project %s", project_id)
            return {"success": False}

    def apply_requirements_mutations(
        self,
        project_id: str,
        mutations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Apply incremental mutations to a project's requirements structure.

        Args:
            project_id: The project UUID string.
            mutations: List of {operation, data} dicts (already validated by Facilitator plugin).

        Returns:
            Dict with accepted, mutation_count, and mutations_applied fields.
        """
        import json

        from django.db import connection as db_conn

        # Fetch current state
        state = self.get_requirements_state(project_id)
        structure = list(state.get("structure", []))
        item_locks = state.get("item_locks", {})
        project_type = self._get_project_type(project_id)

        results: list[dict[str, Any]] = []
        for mutation in mutations:
            operation = mutation.get("operation", "")
            data = mutation.get("data", {})
            try:
                structure = _apply_single_mutation(
                    structure, operation, data, item_locks, project_type,
                )
                results.append({"operation": operation, "status": "success", "error": ""})
            except MutationError as e:
                results.append({"operation": operation, "status": "failed", "error": str(e)})

        # Persist updated structure
        success_count = sum(1 for r in results if r["status"] == "success")
        if success_count > 0:
            structure_json = json.dumps(structure)
            try:
                with db_conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE requirements_document_drafts "
                        "SET structure = %s, updated_at = NOW() WHERE project_id = %s",
                        [structure_json, project_id],
                    )
                    if cursor.rowcount == 0:
                        cursor.execute(
                            "INSERT INTO requirements_document_drafts "
                            "(id, project_id, title, short_description, structure, item_locks, "
                            "allow_information_gaps, readiness_evaluation, created_at, updated_at) "
                            "VALUES (gen_random_uuid(), %s, '', '', %s, '{}', false, '{}', NOW(), NOW())",
                            [project_id, structure_json],
                        )
            except Exception:
                logger.exception(
                    "Failed to persist mutations for project %s", project_id,
                )
                return {
                    "accepted": False,
                    "mutation_count": 0,
                    "mutations_applied": [
                        {"operation": m["operation"], "status": "failed", "error": "persistence_error"}
                        for m in mutations
                    ],
                }

        return {
            "accepted": success_count > 0,
            "mutation_count": success_count,
            "mutations_applied": results,
        }

    def _get_project_type(self, project_id: str) -> str:
        """Fetch project_type for a given project."""
        from django.db import connection as db_conn

        with db_conn.cursor() as cursor:
            cursor.execute(
                "SELECT project_type FROM projects WHERE id = %s AND deleted_at IS NULL",
                [project_id],
            )
            row = cursor.fetchone()
            if row:
                return row[0] or "software"
        return "software"

    # ── BRD operations ──

    def get_brd_draft(self, project_id: str) -> dict[str, Any]:
        """Fetch the current BRD draft for a project."""
        from django.db import connection as db_conn

        with db_conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, section_locks, allow_information_gaps "
                "FROM brd_drafts WHERE project_id = %s",
                [project_id],
            )
            row = cursor.fetchone()
            if row:
                locks = row[1] or {}
                if isinstance(locks, str):
                    import json
                    locks = json.loads(locks)
                return {
                    "id": str(row[0]),
                    "project_id": project_id,
                    "section_locks": locks,
                    "allow_information_gaps": row[2],
                }
        return {
            "id": None,
            "project_id": project_id,
            "section_locks": {},
            "allow_information_gaps": False,
        }

    def upsert_brd_draft(
        self,
        project_id: str,
        sections: dict[str, Any],
        readiness_evaluation: dict[str, str],
    ) -> dict[str, Any]:
        """Create or update a BRD draft for a project."""
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
                        f"UPDATE brd_drafts SET {', '.join(set_parts)} WHERE project_id = %s",
                        values + [project_id],
                    )
                    if cursor.rowcount == 0:
                        # Insert new draft with section content
                        insert_fields = ["id", "project_id", "section_locks",
                                         "allow_information_gaps", "readiness_evaluation",
                                         "created_at", "updated_at"]
                        insert_values: list[Any] = [project_id, "{}", False, readiness_json]
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
            logger.info("Upserted BRD draft for project %s", project_id)
            return {"success": True}
        except Exception:
            logger.exception("Failed to upsert BRD draft for project %s", project_id)
            return {"success": False}

    # ── Context compression ──

    def upsert_context_summary(
        self,
        project_id: str,
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
                    "(id, project_id, summary_text, messages_covered_up_to_id, "
                    "compression_iteration, context_window_usage_at_compression, created_at) "
                    "VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, NOW())",
                    [project_id, summary_text, messages_covered_up_to_id,
                     compression_iteration, context_window_usage],
                )
            logger.info("Persisted context summary for project %s (iteration %d)", project_id, compression_iteration)
            return {"success": True}
        except Exception:
            logger.exception("Failed to persist context summary for project %s", project_id)
            return {"success": False}


# ── Mutation application helpers ──

_SOFTWARE_OPS = frozenset({
    "add_epic", "update_epic", "remove_epic", "reorder_epics",
    "add_story", "update_story", "remove_story", "reorder_stories",
})
_NON_SOFTWARE_OPS = frozenset({
    "add_milestone", "update_milestone", "remove_milestone", "reorder_milestones",
    "add_package", "update_package", "remove_package", "reorder_packages",
})


def _apply_single_mutation(
    structure: list[dict[str, Any]],
    operation: str,
    data: dict[str, Any],
    item_locks: dict[str, Any],
    project_type: str,
) -> list[dict[str, Any]]:
    """Apply one mutation to the structure in-place and return the updated list.

    Raises MutationError on validation failure.
    """
    valid_ops = _SOFTWARE_OPS if project_type == "software" else _NON_SOFTWARE_OPS
    if operation not in valid_ops:
        raise MutationError(f"Operation '{operation}' not valid for {project_type} projects")

    # --- Parent-level add ---
    if operation in ("add_epic", "add_milestone"):
        item_type = "epic" if operation == "add_epic" else "milestone"
        new_item = {
            "id": str(uuid_mod.uuid4()),
            "type": item_type,
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "children": [],
        }
        structure.append(new_item)
        return structure

    # --- Parent-level update ---
    if operation in ("update_epic", "update_milestone"):
        id_key = "epic_id" if operation == "update_epic" else "milestone_id"
        item_id = data.get(id_key, "")
        if item_id in item_locks:
            raise MutationError(f"Item {item_id} is locked")
        parent = _find_item(structure, item_id)
        if parent is None:
            raise MutationError(f"Item {item_id} not found")
        if "title" in data:
            parent["title"] = data["title"]
        if "description" in data:
            parent["description"] = data["description"]
        return structure

    # --- Parent-level remove ---
    if operation in ("remove_epic", "remove_milestone"):
        id_key = "epic_id" if operation == "remove_epic" else "milestone_id"
        item_id = data.get(id_key, "")
        if item_id in item_locks:
            raise MutationError(f"Item {item_id} is locked")
        idx = _find_item_index(structure, item_id)
        if idx is None:
            raise MutationError(f"Item {item_id} not found")
        structure.pop(idx)
        return structure

    # --- Parent-level reorder ---
    if operation in ("reorder_epics", "reorder_milestones"):
        order = data.get("order", [])
        id_map = {item["id"]: item for item in structure}
        reordered = [id_map[oid] for oid in order if oid in id_map]
        remaining = [item for item in structure if item["id"] not in {o for o in order}]
        return reordered + remaining

    # --- Child-level add ---
    if operation in ("add_story", "add_package"):
        parent_key = "epic_id" if operation == "add_story" else "milestone_id"
        parent_id = data.get(parent_key, "")
        parent = _find_item(structure, parent_id)
        if parent is None:
            raise MutationError(f"Parent {parent_id} not found")
        child_type = "user_story" if operation == "add_story" else "work_package"
        child: dict[str, Any] = {
            "id": str(uuid_mod.uuid4()),
            "type": child_type,
            "title": data.get("title", ""),
            "description": data.get("description", ""),
        }
        if child_type == "user_story":
            child["acceptance_criteria"] = data.get("acceptance_criteria", "")
            child["priority"] = data.get("priority", "Medium")
        else:
            child["deliverables"] = data.get("deliverables", "")
            child["dependencies"] = data.get("dependencies", "")
        parent.setdefault("children", []).append(child)
        return structure

    # --- Child-level update ---
    if operation in ("update_story", "update_package"):
        id_key = "story_id" if operation == "update_story" else "package_id"
        child_id = data.get(id_key, "")
        if child_id in item_locks:
            raise MutationError(f"Item {child_id} is locked")
        child_item = _find_child(structure, child_id)
        if child_item is None:
            raise MutationError(f"Item {child_id} not found")
        for key in ("title", "description", "acceptance_criteria", "priority", "deliverables", "dependencies"):
            if key in data:
                child_item[key] = data[key]
        return structure

    # --- Child-level remove ---
    if operation in ("remove_story", "remove_package"):
        id_key = "story_id" if operation == "remove_story" else "package_id"
        child_id = data.get(id_key, "")
        if child_id in item_locks:
            raise MutationError(f"Item {child_id} is locked")
        for parent_item in structure:
            children = parent_item.get("children", [])
            for i, c in enumerate(children):
                if c.get("id") == child_id:
                    children.pop(i)
                    return structure
        raise MutationError(f"Item {child_id} not found")

    # --- Child-level reorder ---
    if operation in ("reorder_stories", "reorder_packages"):
        parent_key = "epic_id" if operation == "reorder_stories" else "milestone_id"
        parent_id = data.get(parent_key, "")
        parent = _find_item(structure, parent_id)
        if parent is None:
            raise MutationError(f"Parent {parent_id} not found")
        order = data.get("order", [])
        children = parent.get("children", [])
        id_map = {c["id"]: c for c in children}
        reordered = [id_map[oid] for oid in order if oid in id_map]
        remaining = [c for c in children if c["id"] not in {o for o in order}]
        parent["children"] = reordered + remaining
        return structure

    raise MutationError(f"Unhandled operation: {operation}")


def _find_item(structure: list[dict[str, Any]], item_id: str) -> dict[str, Any] | None:
    for item in structure:
        if item.get("id") == item_id:
            return item
    return None


def _find_item_index(structure: list[dict[str, Any]], item_id: str) -> int | None:
    for i, item in enumerate(structure):
        if item.get("id") == item_id:
            return i
    return None


def _find_child(structure: list[dict[str, Any]], child_id: str) -> dict[str, Any] | None:
    for parent_item in structure:
        for child in parent_item.get("children", []):
            if child.get("id") == child_id:
                return child
    return None
