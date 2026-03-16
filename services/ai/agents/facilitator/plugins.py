"""Facilitator agent SK plugins (5 tools).

Each method is decorated with @kernel_function so SK registers it as a
callable tool for the Azure OpenAI function-calling loop.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from semantic_kernel.functions import kernel_function

from events.publishers import publish_event

logger = logging.getLogger(__name__)


def _error_response(code: str, message: str) -> dict[str, Any]:
    """Standard error format returned to the model."""
    return {"error": {"code": code, "message": message}}


class FacilitatorPlugin:
    """Tools for the Facilitator AI to interact with the project workspace."""

    def __init__(self, project_id: str, project_context: dict[str, Any] | None = None) -> None:
        self.project_id = project_id
        self.project_context = project_context or {}
        self.delegations: list[dict[str, Any]] = []
        self.chat_message_sent: bool = False

    @kernel_function(
        name="send_chat_message",
        description=(
            "Send a chat message to the project's conversation. Use this to respond to users, "
            "ask clarifying questions, or post delegation messages."
        ),
    )
    async def send_chat_message(
        self,
        content: str,
        message_type: str = "regular",
    ) -> dict[str, Any]:
        """Publish ai.chat_response.ready event."""
        if not content or not content.strip():
            return _error_response("validation_error", "Content must not be empty.")

        if message_type not in ("regular", "delegation"):
            message_type = "regular"

        await publish_event("ai.chat_response.ready", {
            "project_id": self.project_id,
            "content": content,
            "message_type": message_type,
            "sender_type": "ai",
            "ai_agent": "facilitator",
        })

        self.chat_message_sent = True
        return {"message_id": None, "created_at": None}

    @kernel_function(
        name="react_to_message",
        description=(
            "Place a reaction on a specific user message. Use thumbs_up to acknowledge "
            "a message without responding. Use heart to signal the answer fully clarified "
            "your question. Only react to USER messages, never to AI messages."
        ),
    )
    async def react_to_message(
        self,
        message_id: str,
        reaction_type: str,
    ) -> dict[str, Any]:
        """Publish ai.reaction.ready event."""
        if reaction_type not in ("thumbs_up", "thumbs_down", "heart"):
            return _error_response(
                "validation_error",
                f"Invalid reaction_type '{reaction_type}'. Must be thumbs_up, thumbs_down, or heart.",
            )

        # Validate target message is a user message (via context)
        recent_messages = self.project_context.get("recent_messages", [])
        target_msg = _find_message(recent_messages, message_id)

        if target_msg is None:
            return _error_response("invalid_message", f"Message {message_id} not found.")

        if target_msg.get("sender_type") != "user":
            return _error_response(
                "invalid_message",
                "Cannot react to AI messages. Only react to user messages.",
            )

        # Check for duplicate reaction
        if target_msg.get("has_ai_reaction"):
            return _error_response(
                "already_reacted",
                "AI already has a reaction on this message.",
            )

        await publish_event("ai.reaction.ready", {
            "project_id": self.project_id,
            "message_id": message_id,
            "reaction_type": reaction_type,
        })

        return {"success": True}

    @kernel_function(
        name="update_title",
        description=(
            "Update the project's title. Generate a short, concise title (under 60 characters) "
            "that reflects the current direction of the brainstorming."
        ),
    )
    async def update_title(self, title: str) -> dict[str, Any]:
        """Publish ai.title.updated event."""
        if self.project_context.get("title_manually_edited"):
            return _error_response(
                "title_locked",
                "The title was manually edited. AI title updates are disabled.",
            )

        # Truncate to 60 chars
        truncated = title[:60] if len(title) > 60 else title

        await publish_event("ai.title.updated", {
            "project_id": self.project_id,
            "title": truncated,
        })

        return {"success": True, "title": truncated}

    @kernel_function(
        name="delegate_to_context_agent",
        description=(
            "Delegate to the Context Agent to retrieve company-specific information "
            "from the knowledge base. Only call this when the user asks about "
            "company-specific systems, processes, or policies."
        ),
    )
    async def delegate_to_context_agent(self, query: str) -> dict[str, Any]:
        """Publish ai.delegation.started event (non-blocking)."""
        if not query or not query.strip():
            return _error_response("validation_error", "Query must not be empty.")

        # Validate that context_agent_bucket has content
        if not self._context_bucket_has_content():
            return _error_response(
                "no_context_available",
                "The knowledge base is empty. No company context has been configured.",
            )

        delegation_id = str(uuid.uuid4())
        self.delegations.append({
            "delegation_id": delegation_id,
            "delegation_type": "context_agent",
            "query": query,
        })

        await publish_event("ai.delegation.started", {
            "project_id": self.project_id,
            "delegation_type": "context_agent",
            "delegation_id": delegation_id,
            "query": query,
        })

        return {"delegation_id": delegation_id, "status": "queued"}

    @kernel_function(
        name="delegate_to_context_extension",
        description=(
            "Delegate to the Context Extension Agent to search the full, uncompressed "
            "chat history for referenced details."
        ),
    )
    async def delegate_to_context_extension(self, query: str) -> dict[str, Any]:
        """Publish ai.delegation.started event (non-blocking)."""
        if not query or not query.strip():
            return _error_response("validation_error", "Query must not be empty.")

        # Validate that compression has occurred for this project
        if not self._has_compressed_context():
            return _error_response(
                "no_compressed_context",
                "No compressed context exists for this project. All messages are already "
                "available in recent context — no need for context extension.",
            )

        delegation_id = str(uuid.uuid4())
        self.delegations.append({
            "delegation_id": delegation_id,
            "delegation_type": "context_extension",
            "query": query,
        })

        await publish_event("ai.delegation.started", {
            "project_id": self.project_id,
            "delegation_type": "context_extension",
            "delegation_id": delegation_id,
            "query": query,
        })

        return {"delegation_id": delegation_id, "status": "queued"}

    def _has_compressed_context(self) -> bool:
        """Check if chat_context_summaries exist for this project."""
        try:
            from apps.context.models import ChatContextSummary

            return ChatContextSummary.objects.filter(project_id=self.project_id).exists()
        except Exception:
            logger.warning("Failed to check chat_context_summaries — assuming none exist")
            return False

    def _context_bucket_has_content(self) -> bool:
        """Check if the context_agent_bucket singleton has any content."""
        try:
            from apps.context.models import ContextAgentBucket

            bucket = ContextAgentBucket.objects.first()
            if bucket is None:
                return False
            has_sections = bool(bucket.sections)
            has_free_text = bool(bucket.free_text and bucket.free_text.strip())
            return has_sections or has_free_text
        except Exception:
            logger.warning("Failed to check context_agent_bucket — assuming empty")
            return False


def _find_message(
    messages: list[dict[str, Any]], message_id: str
) -> dict[str, Any] | None:
    """Find a message by ID in the recent messages list."""
    for msg in messages:
        if str(msg.get("id", "")) == message_id:
            return msg
    return None
