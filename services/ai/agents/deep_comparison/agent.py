"""DeepComparisonAgent — confirms genuine similarity between two ideas.

Extends BaseAgent with AI-powered deep comparison. Does NOT use SK function
calling (no tools) — direct chat completion with default model tier.
Validates output via Pydantic with one retry on malformed output.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import BaseModel, Field
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory

from agents.base import BaseAgent
from agents.deep_comparison.prompt import build_system_prompt
from kernel.model_router import get_deployment
from kernel.sk_factory import create_kernel

logger = logging.getLogger(__name__)

CONFIDENCE_THRESHOLD = 0.7


class DeepComparisonOutput(BaseModel):
    """Pydantic model for Deep Comparison Agent output validation."""

    is_similar: bool
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str = Field(min_length=10)
    overlap_areas: list[str]


class DeepComparisonAgent(BaseAgent):
    """Deep Comparison Agent — confirms genuine similarity between ideas.

    Consumes similarity.detected events, performs full-context comparison,
    and publishes ai.similarity.confirmed if genuinely similar.
    """

    agent_name: str = "deep_comparison"
    fixture_file: str = "deep_comparison_response.json"

    async def _execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the Deep Comparison Agent via Semantic Kernel.

        Args:
            input_data: Dict with keys for both ideas:
                - idea_a_title, idea_a_keywords, idea_a_chat_summary, idea_a_board_summary
                - idea_b_title, idea_b_keywords, idea_b_chat_summary, idea_b_board_summary
        """
        system_prompt = build_system_prompt(
            idea_a_title=input_data.get("idea_a_title", ""),
            idea_a_keywords=input_data.get("idea_a_keywords", []),
            idea_a_chat_summary=input_data.get("idea_a_chat_summary", ""),
            idea_a_board_summary=input_data.get("idea_a_board_summary", ""),
            idea_b_title=input_data.get("idea_b_title", ""),
            idea_b_keywords=input_data.get("idea_b_keywords", []),
            idea_b_chat_summary=input_data.get("idea_b_chat_summary", ""),
            idea_b_board_summary=input_data.get("idea_b_board_summary", ""),
        )

        deployment = get_deployment("default")
        kernel = create_kernel(deployment, service_id="deep_comparison")

        service = kernel.get_service("deep_comparison")
        assert isinstance(service, AzureChatCompletion)

        settings = service.get_prompt_execution_settings_class()(
            service_id="deep_comparison"
        )
        settings.max_tokens = 800
        settings.temperature = 0.3

        chat_history = ChatHistory(system_message=system_prompt)
        chat_history.add_user_message(
            "Compare the two ideas and return a JSON object with your analysis."
        )

        result = await service.get_chat_message_contents(
            chat_history=chat_history,
            settings=settings,
            kernel=kernel,
        )

        raw_response = str(result[0]) if result else "{}"

        # Validate with Pydantic — retry once on malformed output
        output = self._validate_output(raw_response)
        if output is None:
            logger.warning(
                "[deep_comparison] First parse failed, retrying with format instruction"
            )
            chat_history.add_assistant_message(raw_response)
            chat_history.add_user_message(
                "Your previous response was not valid JSON matching the required "
                "schema. Please return ONLY a JSON object with these exact fields: "
                "is_similar (bool), confidence (float 0-1), explanation (string, "
                "min 10 chars), overlap_areas (list of strings)."
            )

            retry_result = await service.get_chat_message_contents(
                chat_history=chat_history,
                settings=settings,
                kernel=kernel,
            )
            retry_response = str(retry_result[0]) if retry_result else "{}"
            output = self._validate_output(retry_response)

            if output is None:
                logger.error(
                    "[deep_comparison] Retry also failed — returning not similar"
                )
                return {
                    "is_similar": False,
                    "confidence": 0.0,
                    "explanation": "Failed to parse AI response after retry",
                    "overlap_areas": [],
                }

        logger.info(
            "[deep_comparison] Result: is_similar=%s, confidence=%.2f",
            output.is_similar,
            output.confidence,
        )

        return output.model_dump()

    @staticmethod
    def _validate_output(raw_response: str) -> DeepComparisonOutput | None:
        """Parse and validate the LLM response via Pydantic.

        Returns the validated model or None if parsing/validation fails.
        """
        try:
            parsed = json.loads(raw_response.strip())
            return DeepComparisonOutput.model_validate(parsed)
        except (json.JSONDecodeError, Exception):
            logger.debug(
                "[deep_comparison] Validation failed for response: %s",
                raw_response[:200],
            )
            return None
