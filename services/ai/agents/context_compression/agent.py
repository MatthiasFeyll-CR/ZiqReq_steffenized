"""ContextCompressionAgent — summarizes older chat messages into compressed context.

Extends BaseAgent with incremental summarization. Does NOT use SK function
calling (no tools) — direct chat completion with default model tier.
"""

from __future__ import annotations

import logging
from typing import Any

from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory

from agents.base import BaseAgent
from agents.context_compression.prompt import build_system_prompt
from grpc_clients.core_client import CoreClient
from kernel.model_router import get_deployment
from kernel.sk_factory import create_kernel

logger = logging.getLogger(__name__)


class ContextCompressionAgent(BaseAgent):
    """Context Compression Agent — incrementally summarizes chat messages.

    Triggered when context window utilization exceeds the configured threshold.
    Builds on previous summaries to maintain continuity.
    """

    agent_name: str = "context_compression"
    fixture_file: str = "context_compression_response.json"

    def __init__(self, core_client: CoreClient | None = None) -> None:
        self._core_client = core_client or CoreClient()

    async def _execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the Context Compression Agent via Semantic Kernel.

        Args:
            input_data: Dict with keys:
                - idea_id: str — the idea context
                - messages_to_compress: list[dict] — messages to compress
                - previous_summary: str|None — existing summary from prior iteration
        """
        idea_id: str = input_data["idea_id"]
        messages_to_compress: list[dict[str, Any]] = input_data.get(
            "messages_to_compress", []
        )
        previous_summary: str | None = input_data.get("previous_summary")

        if not messages_to_compress:
            logger.info(
                "[context_compression] No messages to compress for idea %s",
                idea_id,
            )
            return {
                "summary_text": previous_summary or "",
                "compression_iteration": input_data.get("compression_iteration", 0),
                "context_window_usage": input_data.get("context_window_usage", 0.0),
            }

        # Build system prompt with messages and previous summary
        system_prompt = build_system_prompt(messages_to_compress, previous_summary)

        # Create kernel with default tier deployment
        deployment = get_deployment("default")
        kernel = create_kernel(deployment, service_id="context_compression")

        # Get chat completion service
        service = kernel.get_service("context_compression")
        assert isinstance(service, AzureChatCompletion)

        settings = service.get_prompt_execution_settings_class()(
            service_id="context_compression"
        )
        settings.max_tokens = 2000
        settings.temperature = 0.3

        # Build chat history
        chat_history = ChatHistory(system_message=system_prompt)
        chat_history.add_user_message(
            "Compress the messages above into a concise summary, "
            "integrating with the previous summary if one exists."
        )

        # Invoke SK chat completion
        result = await service.get_chat_message_contents(
            chat_history=chat_history,
            settings=settings,
            kernel=kernel,
        )

        summary_text = str(result[0]) if result else ""

        compression_iteration = input_data.get("compression_iteration", 0) + 1
        context_window_usage = input_data.get("context_window_usage", 0.0)

        # Persist summary via CoreClient gRPC (upsert)
        last_message_id = ""
        if messages_to_compress:
            last_message_id = messages_to_compress[-1].get("id", "")

        try:
            self._core_client.upsert_context_summary(
                idea_id=idea_id,
                summary_text=summary_text,
                messages_covered_up_to_id=last_message_id,
                compression_iteration=compression_iteration,
                context_window_usage=context_window_usage,
            )
        except Exception:
            logger.exception(
                "[context_compression] Failed to persist summary for idea %s",
                idea_id,
            )

        logger.info(
            "[context_compression] Compressed %d messages for idea %s "
            "(iteration %d, usage %.1f%%)",
            len(messages_to_compress),
            idea_id,
            compression_iteration,
            context_window_usage,
        )

        return {
            "summary_text": summary_text,
            "compression_iteration": compression_iteration,
            "context_window_usage": context_window_usage,
        }
