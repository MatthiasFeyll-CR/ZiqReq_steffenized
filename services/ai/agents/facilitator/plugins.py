"""Facilitator agent SK plugins (6 tools).

Each method is decorated with @kernel_function so SK registers it as a
callable tool for the Azure OpenAI function-calling loop.
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from semantic_kernel.functions import kernel_function

from events.publishers import publish_event

logger = logging.getLogger(__name__)

# Valid operations grouped by project type
_SOFTWARE_OPERATIONS = frozenset({
    "add_epic", "update_epic", "remove_epic", "reorder_epics",
    "add_story", "update_story", "remove_story", "reorder_stories",
})
_NON_SOFTWARE_OPERATIONS = frozenset({
    "add_milestone", "update_milestone", "remove_milestone", "reorder_milestones",
    "add_package", "update_package", "remove_package", "reorder_packages",
})
_ALL_OPERATIONS = _SOFTWARE_OPERATIONS | _NON_SOFTWARE_OPERATIONS


def _parse_mutations_input(mutations: Any) -> list[dict[str, Any]] | None:
    """Parse mutations from various formats SK/LLM might provide.

    Handles:
      - Python list (SK parsed the JSON before passing)
      - Python dict (unwrap to find list inside, or treat as single mutation)
      - JSON string (standard path)
      - Plain-text function-call syntax fallback (e.g. 'add_epic(title: "...")')

    Returns a list of {operation, data} dicts, or None if unparseable.
    """
    if isinstance(mutations, list):
        return mutations if mutations else None

    if isinstance(mutations, dict):
        for v in mutations.values():
            if isinstance(v, list):
                return v if v else None
        if "operation" in mutations:
            return [mutations]
        return None

    if not isinstance(mutations, str):
        return None

    # Try JSON parse first
    try:
        parsed = json.loads(mutations)
        if isinstance(parsed, list) and parsed:
            return parsed
        if isinstance(parsed, dict):
            if "operation" in parsed:
                return [parsed]
            for v in parsed.values():
                if isinstance(v, list) and v:
                    return v
    except (json.JSONDecodeError, TypeError):
        pass

    # Fallback: parse plain-text function-call syntax like:
    #   add_epic(title: "My Epic", description: "...")
    #   add_story(epic_id: "...", title: "...", ...)
    return _parse_plaintext_mutations(mutations)


def _parse_plaintext_mutations(text: str) -> list[dict[str, Any]] | None:
    """Best-effort parser for plain-text function-call syntax from the LLM.

    Parses lines like:
        add_epic(title: "Title", description: "Desc")
        add_story(epic_id: "...", title: "...", acceptance_criteria: "...")
    """
    import re

    results: list[dict[str, Any]] = []
    # Match function-call patterns: operation_name(key: "value", ...)
    pattern = re.compile(
        r'(add_epic|update_epic|remove_epic|reorder_epics'
        r'|add_story|update_story|remove_story|reorder_stories'
        r'|add_milestone|update_milestone|remove_milestone|reorder_milestones'
        r'|add_package|update_package|remove_package|reorder_packages)'
        r'\s*\(([^)]*)\)',
        re.DOTALL,
    )

    for match in pattern.finditer(text):
        operation = match.group(1)
        args_str = match.group(2)

        # Parse key: "value" pairs (handles escaped quotes)
        data: dict[str, Any] = {}
        kv_pattern = re.compile(
            r'(\w+)\s*:\s*"((?:[^"\\]|\\.)*)"\s*[,;]?\s*',
            re.DOTALL,
        )
        for kv_match in kv_pattern.finditer(args_str):
            key = kv_match.group(1)
            value = kv_match.group(2).replace('\\"', '"').replace("\\n", "\n")
            data[key] = value

        if data:
            # Map 'epic' key to 'epic_id' for add_story references by title
            # (LLM sometimes uses epic: "Epic Title" instead of epic_id)
            if "epic" in data and "epic_id" not in data:
                data["epic_id"] = data.pop("epic")
            if "milestone" in data and "milestone_id" not in data:
                data["milestone_id"] = data.pop("milestone")

            results.append({"operation": operation, "data": data})

    return results if results else None


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
        self.requirements_mutations: list[dict[str, Any]] = []

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
            "that reflects the current direction of the project."
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

    @kernel_function(
        name="update_requirements_structure",
        description=(
            "Submit structured mutations to update the project's requirements. "
            "The mutations parameter MUST be a JSON array of objects. "
            "Each object has 'operation' (string) and 'data' (object). "
            "You CAN add epics/milestones and their children (stories/packages) in a SINGLE call. "
            "For add_story/add_package referencing a NEW epic/milestone from the same batch, "
            "set epic_id/milestone_id to the EXACT title of the new epic/milestone. "
            "For existing epics/milestones, use the UUID from the requirements structure. "
            "Example: "
            '[{"operation":"add_epic","data":{"title":"User Management","description":"..."}}, '
            '{"operation":"add_story","data":{"epic_id":"User Management","title":"As a user, I want to log in",'
            '"description":"...","acceptance_criteria":"...","priority":"High"}}]. '
            "Valid operations for software: add_epic, update_epic, remove_epic, reorder_epics, "
            "add_story, update_story, remove_story, reorder_stories. "
            "Valid operations for non-software: add_milestone, update_milestone, remove_milestone, "
            "reorder_milestones, add_package, update_package, remove_package, reorder_packages. "
            "The response includes generated IDs for all newly created items."
        ),
    )
    async def update_requirements_structure(
        self,
        mutations: str,
    ) -> dict[str, Any]:
        """Apply requirements structure mutations.

        Args:
            mutations: JSON array of {operation, data} objects.
                SK may also pass a Python list/dict directly instead of a string.
        """
        logger.info(
            "update_requirements_structure called: mutations type=%s, value=%.200s",
            type(mutations).__name__,
            str(mutations)[:200],
        )
        mutations_list = _parse_mutations_input(mutations)

        if not mutations_list:
            return _error_response(
                "validation_error",
                "mutations must be a JSON array of {operation, data} objects. "
                'Example: [{"operation":"add_epic","data":{"title":"Epic Title","description":"..."}}]',
            )

        if not isinstance(mutations_list, list) or len(mutations_list) == 0:
            return _error_response("validation_error", "mutations must be a non-empty array.")

        project_type = self.project_context.get("project_type", "software")
        valid_ops = _SOFTWARE_OPERATIONS if project_type == "software" else _NON_SOFTWARE_OPERATIONS

        # Track newly created parent items by title → generated UUID
        # so child mutations in the same batch can reference them.
        pending_parents: dict[str, str] = {}

        results: list[dict[str, Any]] = []
        for mutation in mutations_list:
            operation = mutation.get("operation", "")
            data = mutation.get("data", {})

            # Validate operation is known
            if operation not in _ALL_OPERATIONS:
                results.append({
                    "operation": operation,
                    "status": "failed",
                    "error": f"Unknown operation: {operation}",
                })
                continue

            # Validate operation matches project type
            if operation not in valid_ops:
                results.append({
                    "operation": operation,
                    "status": "failed",
                    "error": f"Operation '{operation}' is not valid for {project_type} projects.",
                })
                continue

            # Validate required data fields
            validation_error = _validate_mutation_data(operation, data)
            if validation_error:
                results.append({
                    "operation": operation,
                    "status": "failed",
                    "error": validation_error,
                })
                continue

            # Pre-generate UUIDs for add operations
            generated_id = None
            if operation in ("add_epic", "add_milestone"):
                generated_id = str(uuid.uuid4())
                data["_generated_id"] = generated_id
                title = data.get("title", "")
                if title:
                    pending_parents[title] = generated_id

            elif operation in ("add_story", "add_package"):
                generated_id = str(uuid.uuid4())
                data["_generated_id"] = generated_id
                # Resolve parent reference: if epic_id/milestone_id matches
                # a pending parent title, substitute the generated UUID.
                parent_key = "epic_id" if operation == "add_story" else "milestone_id"
                parent_ref = data.get(parent_key, "")
                if parent_ref in pending_parents:
                    data[parent_key] = pending_parents[parent_ref]

            result_entry: dict[str, Any] = {
                "operation": operation,
                "status": "success",
                "error": None,
            }
            if generated_id:
                result_entry["generated_id"] = generated_id
            results.append(result_entry)

            await publish_event("ai.requirements.updated", {
                "project_id": self.project_id,
                "operation": operation,
                "data": data,
            })

        # Store mutations for pipeline to process
        self.requirements_mutations.extend(
            m for m, r in zip(mutations_list, results) if r["status"] == "success"
        )

        accepted = any(r["status"] == "success" for r in results)
        return {
            "accepted": accepted,
            "mutation_count": sum(1 for r in results if r["status"] == "success"),
            "mutations_applied": results,
        }

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


# Required fields per mutation operation
_REQUIRED_FIELDS: dict[str, list[str]] = {
    "add_epic": ["title"],
    "update_epic": ["epic_id"],
    "remove_epic": ["epic_id"],
    "reorder_epics": ["order"],
    "add_story": ["epic_id", "title"],
    "update_story": ["story_id"],
    "remove_story": ["story_id"],
    "reorder_stories": ["epic_id", "order"],
    "add_milestone": ["title"],
    "update_milestone": ["milestone_id"],
    "remove_milestone": ["milestone_id"],
    "reorder_milestones": ["order"],
    "add_package": ["milestone_id", "title"],
    "update_package": ["package_id"],
    "remove_package": ["package_id"],
    "reorder_packages": ["milestone_id", "order"],
}


def _validate_mutation_data(operation: str, data: dict[str, Any]) -> str | None:
    """Validate that required fields are present for the given operation.

    Returns an error message string if validation fails, or None if valid.
    """
    required = _REQUIRED_FIELDS.get(operation, [])
    missing = [f for f in required if not data.get(f)]
    if missing:
        return f"Missing required fields for {operation}: {', '.join(missing)}"
    return None
