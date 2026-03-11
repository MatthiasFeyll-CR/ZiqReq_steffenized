"""KeywordAgent — extracts abstract keywords from idea content.

Extends BaseAgent with keyword extraction. Does NOT use SK function
calling (no tools) — direct chat completion with default model tier.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory

from agents.base import BaseAgent
from agents.keyword_agent.prompt import build_system_prompt
from grpc_clients.core_client import CoreClient
from kernel.model_router import get_deployment
from kernel.sk_factory import create_kernel

logger = logging.getLogger(__name__)


class KeywordAgent(BaseAgent):
    """Keyword Agent — extracts abstract keywords from idea content.

    Invoked at the end of each processing cycle to extract keywords
    for similarity detection via keyword matching.
    """

    agent_name: str = "keyword"
    fixture_file: str = "keyword_agent_response.json"

    def __init__(self, core_client: CoreClient | None = None) -> None:
        self._core_client = core_client or CoreClient()

    async def _execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the Keyword Agent via Semantic Kernel.

        Args:
            input_data: Dict with keys:
                - idea_id: str — the idea to extract keywords for
                - title: str — idea title
                - chat_summary: str — summary of chat content
                - board_content: str — summary of board content
        """
        idea_id: str = input_data["idea_id"]
        title: str = input_data.get("title", "")
        chat_summary: str = input_data.get("chat_summary", "")
        board_content: str = input_data.get("board_content", "")

        # Read max_keywords from admin params (default 20)
        max_keywords = 20
        try:
            param_result = self._core_client.get_admin_parameter(
                "max_keywords_per_idea"
            )
            value = param_result.get("value", "")
            if value:
                max_keywords = int(value)
        except Exception:
            logger.debug(
                "[keyword] Could not read max_keywords_per_idea — using default %d",
                max_keywords,
            )

        # Build system prompt
        system_prompt = build_system_prompt(
            title=title,
            chat_summary=chat_summary,
            board_content=board_content,
            max_keywords=max_keywords,
        )

        # Create kernel with default tier deployment
        deployment = get_deployment("default")
        kernel = create_kernel(deployment, service_id="keyword")

        # Get chat completion service
        service = kernel.get_service("keyword")
        assert isinstance(service, AzureChatCompletion)

        settings = service.get_prompt_execution_settings_class()(
            service_id="keyword"
        )
        settings.max_tokens = 500
        settings.temperature = 0.3

        # Build chat history
        chat_history = ChatHistory(system_message=system_prompt)
        chat_history.add_user_message(
            "Extract keywords from the idea content above and return them "
            "as a JSON array of single-word strings."
        )

        # Invoke SK chat completion
        result = await service.get_chat_message_contents(
            chat_history=chat_history,
            settings=settings,
            kernel=kernel,
        )

        raw_response = str(result[0]) if result else "[]"

        # Parse keywords from JSON response
        keywords = self._parse_keywords(raw_response, max_keywords)

        # Persist keywords via CoreClient gRPC (upsert)
        try:
            self._core_client.upsert_keywords(
                idea_id=idea_id,
                keywords=keywords,
            )
        except Exception:
            logger.exception(
                "[keyword] Failed to persist keywords for idea %s",
                idea_id,
            )

        # Trigger idea embedding generation
        try:
            from embedding.idea_embedder import IdeaEmbedder

            embedder = IdeaEmbedder()
            await embedder.generate(
                idea_id=idea_id,
                title=title,
                chat_summary=chat_summary,
                board_content=board_content,
            )
        except Exception:
            logger.exception(
                "[keyword] Failed to generate idea embedding for idea %s",
                idea_id,
            )

        logger.info(
            "[keyword] Extracted %d keywords for idea %s",
            len(keywords),
            idea_id,
        )

        return {"keywords": keywords}

    @staticmethod
    def _parse_keywords(raw_response: str, max_keywords: int) -> list[str]:
        """Parse and validate keywords from LLM response.

        Ensures keywords are: single words, lowercase, no duplicates,
        sorted alphabetically, capped at max_keywords.
        """
        try:
            parsed = json.loads(raw_response.strip())
        except json.JSONDecodeError:
            logger.warning("[keyword] Failed to parse keywords JSON: %s", raw_response)
            return []

        if not isinstance(parsed, list):
            logger.warning("[keyword] Expected list, got %s", type(parsed).__name__)
            return []

        seen: set[str] = set()
        keywords: list[str] = []
        for item in parsed:
            if not isinstance(item, str):
                continue
            word = item.strip().lower()
            # Single word check: no spaces
            if not word or " " in word:
                continue
            if word not in seen:
                seen.add(word)
                keywords.append(word)

        keywords.sort()
        return keywords[:max_keywords]
