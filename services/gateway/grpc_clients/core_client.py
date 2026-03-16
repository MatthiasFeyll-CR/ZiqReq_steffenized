"""Core service client — direct database access.

All methods query the shared PostgreSQL database directly via Django ORM
instead of making gRPC calls, since all services share the same database.
"""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class CoreClient:
    """Client for Core service data — uses direct DB access."""

    def __init__(self, address: str = "localhost:50051") -> None:
        self.address = address

    def get_idea_context(
        self,
        idea_id: str,
        recent_message_limit: int = 20,
        include_board: bool = True,
        include_brd_draft: bool = False,
    ) -> dict[str, Any]:
        from apps.ideas.models import ChatMessage, Idea

        try:
            idea = Idea.objects.get(id=idea_id, deleted_at__isnull=True)
        except Idea.DoesNotExist:
            return {}

        metadata = {
            "idea_id": str(idea.id),
            "title": idea.title or "",
            "title_manually_edited": idea.title_manually_edited,
            "state": idea.state,
            "agent_mode": idea.agent_mode,
            "owner_display_name": "",
        }

        recent_messages = []
        msgs = ChatMessage.objects.filter(idea_id=idea_id).order_by("-created_at")[:recent_message_limit]
        for msg in reversed(list(msgs)):
            recent_messages.append({
                "id": str(msg.id),
                "sender_type": msg.sender_type,
                "sender_id": str(msg.sender_id) if msg.sender_id else None,
                "ai_agent": msg.ai_agent,
                "content": msg.content,
                "message_type": msg.message_type,
                "created_at": msg.created_at.isoformat() if msg.created_at else "",
            })

        board = {"nodes": [], "connections": []}
        if include_board:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id, node_type, title, body, position_x, position_y, "
                    "width, height, parent_id, is_locked, created_by, created_at "
                    "FROM board_nodes WHERE idea_id = %s ORDER BY created_at",
                    [idea_id],
                )
                for row in cursor.fetchall():
                    board["nodes"].append({
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
                cursor.execute(
                    "SELECT id, source_node_id, target_node_id, label, created_at "
                    "FROM board_connections WHERE idea_id = %s ORDER BY created_at",
                    [idea_id],
                )
                for row in cursor.fetchall():
                    board["connections"].append({
                        "id": str(row[0]),
                        "source_node_id": str(row[1]),
                        "target_node_id": str(row[2]),
                        "label": row[3] or "",
                        "created_at": row[4].isoformat() if row[4] else "",
                    })

        brd_draft = None
        if include_brd_draft:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT section_title, section_short_description, section_current_workflow, "
                    "section_affected_department, section_core_capabilities, section_success_criteria, "
                    "section_locks, updated_at FROM brd_drafts WHERE idea_id = %s",
                    [idea_id],
                )
                row = cursor.fetchone()
                if row:
                    brd_draft = {
                        "idea_id": idea_id,
                        "sections": {
                            "title": row[0] or "",
                            "short_description": row[1] or "",
                            "current_workflow": row[2] or "",
                            "affected_department": row[3] or "",
                            "core_capabilities": row[4] or "",
                            "success_criteria": row[5] or "",
                        },
                        "locked_sections": row[6] or {},
                        "updated_at": row[7].isoformat() if row[7] else "",
                    }

        return {
            "metadata": metadata,
            "recent_messages": recent_messages,
            "board": board,
            "brd_draft": brd_draft,
            "active_users": [],
        }

    def get_full_chat_history(self, idea_id: str) -> dict[str, Any]:
        from apps.ideas.models import ChatMessage

        messages = []
        for msg in ChatMessage.objects.filter(idea_id=idea_id).order_by("created_at"):
            messages.append({
                "id": str(msg.id),
                "sender_type": msg.sender_type,
                "sender_id": str(msg.sender_id) if msg.sender_id else None,
                "ai_agent": msg.ai_agent,
                "content": msg.content,
                "message_type": msg.message_type,
                "created_at": msg.created_at.isoformat() if msg.created_at else "",
            })
        return {"messages": messages}

    def get_rate_limit_status(self, idea_id: str) -> dict[str, Any]:
        from apps.ideas.models import ChatMessage

        # Count user messages created after the last AI message (unprocessed messages)
        last_ai_message = (
            ChatMessage.objects.filter(idea_id=idea_id, sender_type="ai")
            .order_by("-created_at")
            .values("created_at")
            .first()
        )

        qs = ChatMessage.objects.filter(idea_id=idea_id, sender_type="user")
        if last_ai_message:
            qs = qs.filter(created_at__gt=last_ai_message["created_at"])

        current_count = qs.count()

        # Read cap from admin_parameters (chat_message_cap, default 5)
        cap = 5
        try:
            from apps.admin_config.services import get_parameter
            cap = get_parameter("chat_message_cap", default=5, cast=int)
        except Exception:
            pass

        return {
            "current_count": current_count,
            "cap": cap,
            "is_locked": current_count >= cap,
        }

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
        from django.db import connection

        import uuid

        reaction_id = str(uuid.uuid4())
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO ai_reactions (id, message_id, reaction_type, created_at) "
                "VALUES (%s, %s, %s, NOW()) "
                "ON CONFLICT (message_id) DO UPDATE SET reaction_type = EXCLUDED.reaction_type",
                [reaction_id, message_id, reaction_type],
            )
        logger.info("Persisted AI reaction %s on message %s", reaction_id, message_id)
        return {"reaction_id": reaction_id}

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

    def update_brd_draft(
        self,
        idea_id: str,
        sections: dict[str, str],
        readiness_evaluation_json: str = "",
    ) -> dict[str, Any]:
        from apps.brd.models import BrdDraft

        draft, _created = BrdDraft.objects.get_or_create(
            idea_id=idea_id,
            defaults={
                "section_locks": {},
                "allow_information_gaps": False,
                "readiness_evaluation": {},
            },
        )

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
                locks = draft.section_locks or {}
                if not locks.get(key, False):
                    setattr(draft, field, sections[key])
                    update_fields.append(field)

        if readiness_evaluation_json:
            try:
                draft.readiness_evaluation = json.loads(readiness_evaluation_json) if isinstance(readiness_evaluation_json, str) else readiness_evaluation_json
            except (json.JSONDecodeError, TypeError):
                draft.readiness_evaluation = {}
            update_fields.append("readiness_evaluation")

        draft.save(update_fields=update_fields)
        logger.info("Updated BRD draft for idea %s", idea_id)
        return {"success": True}

    def persist_board_mutations(
        self, idea_id: str, mutations: list[dict[str, Any]]
    ) -> dict[str, Any]:
        from apps.board.models import BoardConnection, BoardNode

        applied = 0
        for mut in mutations:
            mut_type = mut.get("action") or mut.get("type", "")
            try:
                if mut_type == "create_node":
                    BoardNode.objects.create(
                        id=mut.get("node_id"),
                        idea_id=idea_id,
                        node_type=mut.get("node_type", "box"),
                        title=mut.get("title", "") or mut.get("content", ""),
                        body=mut.get("body", ""),
                        position_x=mut.get("position_x") or mut.get("x_position", 0),
                        position_y=mut.get("position_y") or mut.get("y_position", 0),
                        width=mut.get("width") or 250,
                        height=mut.get("height"),
                        parent_id=mut.get("parent_id") or None,
                        is_locked=mut.get("is_locked", False),
                        created_by=mut.get("created_by", "ai"),
                    )
                    applied += 1
                elif mut_type == "update_node":
                    node_id = mut.get("node_id")
                    updates: dict[str, Any] = {}
                    if "title" in mut:
                        updates["title"] = mut["title"]
                    elif "content" in mut:
                        updates["title"] = mut["content"]
                    if "body" in mut:
                        updates["body"] = mut["body"]
                    if "node_type" in mut:
                        updates["node_type"] = mut["node_type"]
                    if "position_x" in mut:
                        updates["position_x"] = mut["position_x"]
                    elif "x_position" in mut:
                        updates["position_x"] = mut["x_position"]
                    if "position_y" in mut:
                        updates["position_y"] = mut["position_y"]
                    elif "y_position" in mut:
                        updates["position_y"] = mut["y_position"]
                    if "width" in mut:
                        updates["width"] = mut["width"]
                    if "height" in mut:
                        updates["height"] = mut["height"]
                    if "parent_id" in mut:
                        updates["parent_id"] = mut["parent_id"] or None
                    if "is_locked" in mut:
                        updates["is_locked"] = mut["is_locked"]
                    if updates:
                        updates["ai_modified_indicator"] = True
                        BoardNode.objects.filter(id=node_id, idea_id=idea_id).update(**updates)
                    applied += 1
                elif mut_type == "move_node":
                    node_id = mut.get("node_id")
                    move_updates: dict[str, Any] = {"ai_modified_indicator": True}
                    if "position_x" in mut:
                        move_updates["position_x"] = mut["position_x"]
                    if "position_y" in mut:
                        move_updates["position_y"] = mut["position_y"]
                    if "new_parent_id" in mut:
                        move_updates["parent_id"] = mut["new_parent_id"] or None
                    BoardNode.objects.filter(id=node_id, idea_id=idea_id).update(**move_updates)
                    applied += 1
                elif mut_type == "delete_node":
                    BoardNode.objects.filter(id=mut.get("node_id"), idea_id=idea_id).delete()
                    applied += 1
                elif mut_type == "create_connection":
                    BoardConnection.objects.create(
                        idea_id=idea_id,
                        source_node_id=mut.get("source_node_id"),
                        target_node_id=mut.get("target_node_id"),
                        label=mut.get("label", ""),
                    )
                    applied += 1
                elif mut_type == "update_connection":
                    conn_updates: dict[str, Any] = {}
                    if "label" in mut:
                        conn_updates["label"] = mut["label"]
                    if "source_node_id" in mut:
                        conn_updates["source_node_id"] = mut["source_node_id"]
                    if "target_node_id" in mut:
                        conn_updates["target_node_id"] = mut["target_node_id"]
                    if conn_updates:
                        BoardConnection.objects.filter(
                            id=mut.get("node_id"), idea_id=idea_id
                        ).update(**conn_updates)
                    applied += 1
                elif mut_type == "delete_connection":
                    BoardConnection.objects.filter(
                        id=mut.get("node_id"), idea_id=idea_id
                    ).delete()
                    applied += 1
                else:
                    logger.warning("Unknown board mutation type: %s", mut_type)
            except Exception:
                logger.exception("Failed to apply board mutation %s", mut_type)

        logger.info("Applied %d/%d board mutations for idea %s", applied, len(mutations), idea_id)
        return {"success": True, "mutations_applied": applied}
