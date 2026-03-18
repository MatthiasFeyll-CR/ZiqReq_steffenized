"""ContextExtensionAgent — searches full uncompressed chat history.

Extends BaseAgent with full history retrieval via CoreClient gRPC.
Does NOT use SK function calling (no tools) — direct chat completion
with escalated model tier for larger context window.
"""

from __future__ import annotations

import logging
from typing import Any

from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory

from agents.base import BaseAgent
from agents.context_extension.prompt import build_system_prompt
from grpc_clients.core_client import CoreClient
from kernel.model_router import get_deployment
from kernel.sk_factory import create_kernel

logger = logging.getLogger(__name__)


class ContextExtensionAgent(BaseAgent):
    """Context Extension Agent — retrieves specific details from full chat history.

    Uses escalated model tier (larger context window) and 90s timeout
    to handle potentially large conversation histories.
    """

    agent_name: str = "context_extension"
    fixture_file: str = "context_extension_response.json"

    def __init__(self, core_client: CoreClient | None = None) -> None:
        self._core_client = core_client or CoreClient()

    async def _execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the Context Extension Agent via Semantic Kernel.

        Args:
            input_data: Dict with keys:
                - query: str — the search query for conversation details
                - project_id: str — the project context
        """
        query: str = input_data["query"]
        project_id: str = input_data["project_id"]

        # Load full chat history via CoreClient gRPC
        try:
            history_result = self._core_client.get_full_chat_history(project_id)
        except Exception:
            logger.exception(
                "[context_extension] Failed to load chat history for project %s",
                project_id,
            )
            return {
                "response": (
                    "Unable to retrieve the full chat history. "
                    "The conversation history service is currently unavailable."
                ),
                "messages_cited": [],
            }

        messages: list[dict[str, Any]] = history_result.get("messages", [])

        # Load project attachments with completed extraction for extended search
        attachments: list[dict[str, Any]] = []
        try:
            attachments = self._core_client.get_project_attachments(project_id)
        except Exception:
            logger.warning(
                "[context_extension] Failed to load attachments for project %s",
                project_id,
            )

        # If no messages and no attachments, return early
        if not messages and not attachments:
            logger.info(
                "[context_extension] No messages or attachments for project %s",
                project_id,
            )
            return {
                "response": (
                    "The conversation history is empty. "
                    "There are no past messages to search through."
                ),
                "messages_cited": [],
            }

        # Build system prompt with query, full history, and attachments
        system_prompt = build_system_prompt(query, messages, attachments)

        # Create kernel with escalated tier deployment (larger context window)
        deployment = get_deployment("escalated")
        kernel = create_kernel(deployment, service_id="context_extension")

        # Get chat completion service
        service = kernel.get_service("context_extension")
        assert isinstance(service, AzureChatCompletion)

        settings = service.get_prompt_execution_settings_class()(
            service_id="context_extension"
        )
        settings.max_tokens = 1000
        settings.temperature = 0.3
        # 90s timeout (1.5x ai_processing_timeout of 60s)
        settings.timeout = 90

        # Build chat history
        chat_history = ChatHistory(system_message=system_prompt)
        chat_history.add_user_message(query)

        # Invoke SK chat completion
        result = await service.get_chat_message_contents(
            chat_history=chat_history,
            settings=settings,
            kernel=kernel,
        )

        response_text = str(result[0]) if result else ""

        # Extract cited message IDs from the messages (best-effort)
        message_ids = [m.get("id", "") for m in messages if m.get("id")]

        logger.info(
            "[context_extension] Generated response from %d messages for project %s",
            len(messages),
            project_id,
        )

        return {
            "response": response_text,
            "messages_cited": message_ids,
        }
