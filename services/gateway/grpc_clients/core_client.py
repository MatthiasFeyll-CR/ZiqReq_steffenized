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

    def get_project_context(
        self,
        project_id: str,
        recent_message_limit: int = 20,
        include_brd_draft: bool = False,
    ) -> dict[str, Any]:
        from apps.projects.models import ChatMessage, Project

        try:
            project = Project.objects.get(id=project_id, deleted_at__isnull=True)
        except Project.DoesNotExist:
            return {}

        metadata = {
            "project_id": str(project.id),
            "title": project.title or "",
            "title_manually_edited": project.title_manually_edited,
            "state": project.state,
            "agent_mode": project.agent_mode,
            "owner_display_name": "",
        }

        recent_messages = []
        msgs = ChatMessage.objects.filter(project_id=project_id).order_by("-created_at")[:recent_message_limit]
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

        brd_draft = None
        if include_brd_draft:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT section_title, section_short_description, section_current_workflow, "
                    "section_affected_department, section_core_capabilities, section_success_criteria, "
                    "section_locks, updated_at FROM brd_drafts WHERE project_id = %s",
                    [project_id],
                )
                row = cursor.fetchone()
                if row:
                    brd_draft = {
                        "project_id": project_id,
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
            "brd_draft": brd_draft,
            "active_users": [],
        }

    def get_full_chat_history(self, project_id: str) -> dict[str, Any]:
        from apps.projects.models import ChatMessage

        messages = []
        for msg in ChatMessage.objects.filter(project_id=project_id).order_by("created_at"):
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

    def get_rate_limit_status(self, project_id: str) -> dict[str, Any]:
        from apps.projects.models import ChatMessage

        # Count user messages created after the last AI message (unprocessed messages)
        last_ai_message = (
            ChatMessage.objects.filter(project_id=project_id, sender_type="ai")
            .order_by("-created_at")
            .values("created_at")
            .first()
        )

        qs = ChatMessage.objects.filter(project_id=project_id, sender_type="user")
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
        project_id: str,
        content: str,
        message_type: str = "regular",
        language: str = "de",
        processing_id: str = "",
    ) -> dict[str, Any]:
        from apps.projects.models import ChatMessage

        message = ChatMessage.objects.create(
            project_id=project_id,
            sender_type="ai",
            sender_id=None,
            content=content,
            message_type=message_type,
            ai_agent="facilitator",
        )
        logger.info("Persisted AI chat message %s for project %s", message.id, project_id)
        return {
            "message_id": str(message.id),
            "created_at": message.created_at.isoformat(),
        }

    def persist_ai_reaction(
        self, project_id: str, message_id: str, reaction_type: str
    ) -> dict[str, Any]:
        import uuid

        from django.db import connection

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

    def update_project_title(
        self, project_id: str, new_title: str
    ) -> dict[str, Any]:
        from apps.projects.models import Project

        updated = Project.objects.filter(id=project_id, deleted_at__isnull=True).update(
            title=new_title
        )
        if updated:
            logger.info("Updated title for project %s", project_id)
        else:
            logger.warning("Project %s not found for title update", project_id)
        return {"success": bool(updated)}

    def get_requirements_state(self, project_id: str) -> dict[str, Any]:
        """Fetch the current requirements draft for a project."""
        from apps.projects.models import RequirementsDocumentDraft

        try:
            draft = RequirementsDocumentDraft.objects.get(project_id=project_id)
            return {
                "project_id": project_id,
                "title": draft.title or "",
                "short_description": draft.short_description or "",
                "structure": draft.structure or [],
                "item_locks": draft.item_locks or {},
                "allow_information_gaps": draft.allow_information_gaps,
                "readiness_evaluation": draft.readiness_evaluation or {},
                "updated_at": draft.updated_at.isoformat() if draft.updated_at else "",
            }
        except RequirementsDocumentDraft.DoesNotExist:
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
        """Update the requirements draft structure for a project."""
        from apps.projects.models import RequirementsDocumentDraft

        draft, _created = RequirementsDocumentDraft.objects.get_or_create(
            project_id=project_id,
            defaults={
                "structure": [],
                "item_locks": {},
                "allow_information_gaps": False,
                "readiness_evaluation": {},
            },
        )

        update_fields = ["structure", "updated_at"]
        draft.structure = structure

        if readiness_evaluation is not None:
            draft.readiness_evaluation = readiness_evaluation
            update_fields.append("readiness_evaluation")

        draft.save(update_fields=update_fields)
        logger.info("Updated requirements structure for project %s", project_id)
        return {"success": True}

    def update_brd_draft(
        self,
        project_id: str,
        sections: dict[str, str],
        readiness_evaluation_json: str = "",
    ) -> dict[str, Any]:
        from apps.requirements_document.models import BrdDraft

        draft, _created = BrdDraft.objects.get_or_create(
            project_id=project_id,
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
                draft.readiness_evaluation = (
                    json.loads(readiness_evaluation_json)
                    if isinstance(readiness_evaluation_json, str)
                    else readiness_evaluation_json
                )
            except (json.JSONDecodeError, TypeError):
                draft.readiness_evaluation = {}
            update_fields.append("readiness_evaluation")

        draft.save(update_fields=update_fields)
        logger.info("Updated BRD draft for project %s", project_id)
        return {"success": True}

