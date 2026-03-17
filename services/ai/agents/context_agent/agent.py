"""ContextAgent — RAG retrieval agent for company-specific questions.

Extends BaseAgent with pgvector-based chunk retrieval and grounded response
generation. Does NOT use SK function calling (no tools) — direct chat completion.
"""

from __future__ import annotations

import logging
from typing import Any

from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory

from agents.base import BaseAgent
from agents.context_agent.prompt import build_system_prompt
from embedding.retriever import Retriever
from kernel.model_router import get_deployment
from kernel.sk_factory import create_kernel

logger = logging.getLogger(__name__)


class ContextAgent(BaseAgent):
    """Context Agent — answers company-specific questions via RAG.

    Retrieves relevant chunks from pgvector, injects them into the prompt,
    and generates a grounded response citing only retrieved content.
    """

    agent_name: str = "context_agent"
    fixture_file: str = "context_agent_response.json"

    def __init__(self, retriever: Retriever | None = None) -> None:
        self._retriever = retriever or Retriever()

    async def _execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the Context Agent via Semantic Kernel.

        Args:
            input_data: Dict with keys:
                - query: str — the user's question
                - project_id: str — the project context
                - query_embedding: list[float] — pre-computed embedding of the query
        """
        query: str = input_data["query"]
        project_id: str = input_data["project_id"]
        query_embedding: list[float] = input_data.get("query_embedding", [])
        project_type: str | None = input_data.get("project_type")

        # Retrieve relevant chunks via pgvector cosine similarity
        # Filter by context_type IN (global, project_type) when project_type is set
        chunks: list[dict[str, Any]] = []
        if query_embedding:
            chunks = await self._retriever.retrieve(
                query_embedding=query_embedding,
                project_type=project_type,
            )

        chunk_ids = [c["id"] for c in chunks]

        # If no chunks retrieved, return grounding refusal
        if not chunks:
            logger.info(
                "[context_agent] No relevant chunks for query in project %s",
                project_id,
            )
            return {
                "response": (
                    "I don't have enough context to answer that question. "
                    "The knowledge base doesn't contain relevant information on this topic."
                ),
                "chunks_used": [],
            }

        # Build system prompt with query and chunks
        system_prompt = build_system_prompt(query, chunks)

        # Create kernel with default tier deployment
        deployment = get_deployment("default")
        kernel = create_kernel(deployment, service_id="context_agent")

        # Get chat completion service
        service = kernel.get_service("context_agent")
        assert isinstance(service, AzureChatCompletion)

        settings = service.get_prompt_execution_settings_class()(
            service_id="context_agent"
        )
        settings.max_tokens = 1000
        settings.temperature = 0.3

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

        logger.info(
            "[context_agent] Generated response using %d chunks for project %s",
            len(chunks),
            project_id,
        )

        return {
            "response": response_text,
            "chunks_used": chunk_ids,
        }
