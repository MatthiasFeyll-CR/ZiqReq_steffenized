"""FacilitatorAgent — the primary AI agent for requirements structuring.

Extends BaseAgent with SK function-calling loop, system prompt rendering,
and the FacilitatorPlugin (5 tools).
"""

from __future__ import annotations

import logging
from typing import Any

from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory

from agents.base import BaseAgent
from agents.facilitator.plugins import FacilitatorPlugin
from agents.facilitator.prompt import build_system_prompt
from kernel.model_router import get_deployment
from kernel.sk_factory import create_kernel
from kernel.token_tracker import TokenTracker

logger = logging.getLogger(__name__)


class FacilitatorAgent(BaseAgent):
    """Facilitator agent — guides requirements structuring via 5 tools.

    Uses SK's automatic function-calling loop with max_auto_invoke_attempts=3.
    """

    agent_name: str = "facilitator"
    fixture_file: str = "facilitator_response.json"

    def __init__(self) -> None:
        self.token_tracker = TokenTracker()

    async def _execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the Facilitator via Semantic Kernel function-calling loop.

        Args:
            input_data: Dict with keys:
                - project_id: str
                - project_context: dict (title, state, agent_mode, title_manually_edited, etc.)
                - recent_messages: list[dict]
                - chat_summary: str | None
                - facilitator_bucket_content: str
                - delegation_results: str | None
                - extension_results: str | None
        """
        project_id: str = input_data["project_id"]
        project_context: dict[str, Any] = input_data.get("project_context", {})

        # Build system prompt
        prompt_context = _build_prompt_context(input_data)
        system_prompt = build_system_prompt(prompt_context)

        # Create kernel with default tier deployment
        deployment = get_deployment("default")
        kernel = create_kernel(deployment, service_id="facilitator")

        # Create and register plugin
        plugin = FacilitatorPlugin(
            project_id=project_id,
            project_context={
                **project_context,
                "recent_messages": input_data.get("recent_messages", []),
            },
        )
        kernel.add_plugin(plugin, plugin_name="Facilitator")

        # Configure execution settings
        service = kernel.get_service("facilitator")
        assert isinstance(service, AzureChatCompletion)

        settings = service.get_prompt_execution_settings_class()(service_id="facilitator")
        settings.max_tokens = 1000
        settings.temperature = 0.7
        settings.frequency_penalty = 0.3
        settings.function_choice_behavior = FunctionChoiceBehavior.Auto(
            auto_invoke=True,
            maximum_auto_invoke_attempts=3,
        )

        # Build chat history with system prompt
        chat_history = ChatHistory(system_message=system_prompt)

        # Add recent user messages as the conversation
        recent = input_data.get("recent_messages", [])
        for msg in recent:
            role = "assistant" if msg.get("sender_type") == "ai" else "user"
            content = msg.get("content", "")
            sender_name = msg.get("sender_name", "")
            display = f"[{sender_name}]: {content}" if sender_name else content
            if role == "user":
                chat_history.add_user_message(display)
            else:
                chat_history.add_assistant_message(display)

        # Invoke SK chat completion
        result = await service.get_chat_message_contents(
            chat_history=chat_history,
            settings=settings,
            kernel=kernel,
        )

        # Track tokens
        if result:
            last_msg = result[-1]
            metadata = getattr(last_msg, "metadata", None)
            self.token_tracker.record("facilitator", deployment, metadata)

        return {
            "delegations": plugin.delegations,
            "chat_message_sent": plugin.chat_message_sent,
            "response": result[-1].content if result else None,
            "token_usage": {
                "input": self.token_tracker.total_input,
                "output": self.token_tracker.total_output,
            },
        }


def _build_prompt_context(input_data: dict[str, Any]) -> dict[str, Any]:
    """Map pipeline input_data to prompt template variables."""
    ctx = input_data.get("project_context", {})
    return {
        "agent_mode": ctx.get("agent_mode", "interactive"),
        "project_title": ctx.get("title", ""),
        "project_state": ctx.get("state", "open"),
        "title_manually_edited": ctx.get("title_manually_edited", False),
        "facilitator_bucket_content": input_data.get("facilitator_bucket_content", ""),
        "recent_messages_formatted": _format_messages(input_data.get("recent_messages", [])),
        "chat_summary": input_data.get("chat_summary"),
        "delegation_results": input_data.get("delegation_results"),
        "extension_results": input_data.get("extension_results"),
        "is_multi_user": ctx.get("is_multi_user", False),
        "user_names_list": ctx.get("user_names_list", ""),
        "creator_language": ctx.get("creator_language", "English"),
        "no_messages_yet": len(input_data.get("recent_messages", [])) == 0,
    }


def _format_messages(messages: list[dict[str, Any]]) -> str:
    """Format recent messages for XML prompt injection."""
    lines = []
    for msg in messages:
        sender = msg.get("sender_name", msg.get("sender_type", "unknown"))
        content = msg.get("content", "")
        msg_id = msg.get("id", "")
        msg_type = msg.get("sender_type", "user")
        lines.append(f'<message id="{msg_id}" sender="{sender}" type="{msg_type}">{content}</message>')
    return "\n".join(lines) if lines else "(no messages yet)"
