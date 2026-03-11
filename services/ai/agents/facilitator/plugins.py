"""Facilitator agent SK plugins (7 tools).

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
    """Tools for the Facilitator AI to interact with the idea workspace."""

    def __init__(self, idea_id: str, idea_context: dict[str, Any] | None = None) -> None:
        self.idea_id = idea_id
        self.idea_context = idea_context or {}
        self.delegations: list[dict[str, Any]] = []
        self.board_instructions: list[dict[str, Any]] = []

    @kernel_function(
        name="send_chat_message",
        description=(
            "Send a chat message to the idea's conversation. Use this to respond to users, "
            "ask clarifying questions, or post delegation messages. "
            "Supports board item references using [[Item Title]] syntax."
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

        # Validate board item references — strip invalid [[...]] to plain text
        board_state = self.idea_context.get("board_state", {})
        content = _validate_board_refs(content, board_state)

        await publish_event("ai.chat_response.ready", {
            "idea_id": self.idea_id,
            "content": content,
            "message_type": message_type,
            "sender_type": "ai",
            "ai_agent": "facilitator",
        })

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
        recent_messages = self.idea_context.get("recent_messages", [])
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
            "idea_id": self.idea_id,
            "message_id": message_id,
            "reaction_type": reaction_type,
        })

        return {"success": True}

    @kernel_function(
        name="update_title",
        description=(
            "Update the idea's title. Generate a short, concise title (under 60 characters) "
            "that reflects the current direction of the brainstorming."
        ),
    )
    async def update_title(self, title: str) -> dict[str, Any]:
        """Publish ai.title.updated event."""
        if self.idea_context.get("title_manually_edited"):
            return _error_response(
                "title_locked",
                "The title was manually edited. AI title updates are disabled.",
            )

        # Truncate to 60 chars
        truncated = title[:60] if len(title) > 60 else title

        await publish_event("ai.title.updated", {
            "idea_id": self.idea_id,
            "title": truncated,
        })

        return {"success": True, "title": truncated}

    @kernel_function(
        name="delegate_to_context_agent",
        description=(
            "Delegate to the Context Agent to retrieve company-specific information "
            "from the knowledge base."
        ),
    )
    async def delegate_to_context_agent(self, query: str) -> dict[str, Any]:
        """Publish ai.delegation.started event (non-blocking)."""
        if not query or not query.strip():
            return _error_response("validation_error", "Query must not be empty.")

        delegation_id = str(uuid.uuid4())
        self.delegations.append({
            "delegation_id": delegation_id,
            "delegation_type": "context_agent",
            "query": query,
        })

        await publish_event("ai.delegation.started", {
            "idea_id": self.idea_id,
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

        delegation_id = str(uuid.uuid4())
        self.delegations.append({
            "delegation_id": delegation_id,
            "delegation_type": "context_extension",
            "query": query,
        })

        await publish_event("ai.delegation.started", {
            "idea_id": self.idea_id,
            "delegation_type": "context_extension",
            "delegation_id": delegation_id,
            "query": query,
        })

        return {"delegation_id": delegation_id, "status": "queued"}

    @kernel_function(
        name="request_board_changes",
        description=(
            "Submit board modification instructions for the Board Agent to execute. "
            "Express SEMANTIC INTENT — describe what content to add, update, or "
            "reorganize and why. Reference board items by title. The Board Agent "
            "handles all spatial layout, grouping, and positioning. Only call this "
            "when the brainstorming has produced content that should be captured or "
            "restructured on the board."
        ),
    )
    async def request_board_changes(
        self,
        instructions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Accept board change instructions for Board Agent execution."""
        if not instructions:
            return _error_response(
                "validation_error", "At least one instruction is required."
            )

        valid_intents = {
            "add_topic", "update_topic", "remove_topic", "reorganize",
            "add_relationship", "update_relationship", "remove_relationship",
        }

        for i, instr in enumerate(instructions):
            intent = instr.get("intent")
            if not intent or intent not in valid_intents:
                return _error_response(
                    "validation_error",
                    f"Instruction {i}: invalid or missing intent '{intent}'. "
                    f"Must be one of: {', '.join(sorted(valid_intents))}.",
                )
            if not instr.get("description"):
                return _error_response(
                    "validation_error",
                    f"Instruction {i}: 'description' is required.",
                )

        self.board_instructions.extend(instructions)
        logger.info(
            "Board changes requested for idea %s: %d instructions",
            self.idea_id,
            len(instructions),
        )

        return {"accepted": True, "instruction_count": len(instructions)}


def _validate_board_refs(content: str, board_state: dict[str, Any]) -> str:
    """Validate [[Item Title]] references against board state.

    Invalid references are stripped to plain text (brackets removed).
    """
    import re

    nodes = board_state.get("nodes", [])
    node_titles = {n.get("title", "") for n in nodes if n.get("title")}

    def _replace(match: re.Match[str]) -> str:
        title = match.group(1)
        if title in node_titles:
            return match.group(0)  # valid — keep [[Title]]
        return title  # invalid — strip brackets

    return re.sub(r"\[\[([^\]]+)\]\]", _replace, content)


def _find_message(
    messages: list[dict[str, Any]], message_id: str
) -> dict[str, Any] | None:
    """Find a message by ID in the recent messages list."""
    for msg in messages:
        if str(msg.get("id", "")) == message_id:
            return msg
    return None
