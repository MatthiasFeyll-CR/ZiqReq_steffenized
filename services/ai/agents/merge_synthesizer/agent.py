"""MergeSynthesizerAgent — synthesizes two merged ideas into combined context.

Extends BaseAgent with AI-powered merge synthesis. Does NOT use SK function
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
from agents.merge_synthesizer.prompt import build_system_prompt
from kernel.model_router import get_deployment
from kernel.sk_factory import create_kernel

logger = logging.getLogger(__name__)


class MergeSynthesizerOutput(BaseModel):
    """Pydantic model for Merge Synthesizer Agent output validation."""

    synthesis_message: str = Field(min_length=100)
    board_instructions: list[dict[str, Any]]


class MergeSynthesizerAgent(BaseAgent):
    """Merge Synthesizer Agent — creates synthesis for merged ideas.

    Consumes merge_request.accepted events, produces a synthesis message
    and board instructions for the new merged idea.
    """

    agent_name: str = "merge_synthesizer"
    fixture_file: str = "merge_synthesizer_response.json"

    async def _execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the Merge Synthesizer Agent via Semantic Kernel.

        Args:
            input_data: Dict with keys for both ideas:
                - idea_a_owner_name, idea_a_title, idea_a_summary, idea_a_board_nodes
                - idea_b_owner_name, idea_b_title, idea_b_summary, idea_b_board_nodes
        """
        system_prompt = build_system_prompt(
            idea_a_owner_name=input_data.get("idea_a_owner_name", ""),
            idea_a_title=input_data.get("idea_a_title", ""),
            idea_a_summary=input_data.get("idea_a_summary", ""),
            idea_a_board_nodes=input_data.get("idea_a_board_nodes", []),
            idea_b_owner_name=input_data.get("idea_b_owner_name", ""),
            idea_b_title=input_data.get("idea_b_title", ""),
            idea_b_summary=input_data.get("idea_b_summary", ""),
            idea_b_board_nodes=input_data.get("idea_b_board_nodes", []),
        )

        deployment = get_deployment("default")
        kernel = create_kernel(deployment, service_id="merge_synthesizer")

        service = kernel.get_service("merge_synthesizer")
        assert isinstance(service, AzureChatCompletion)

        settings = service.get_prompt_execution_settings_class()(
            service_id="merge_synthesizer"
        )
        settings.max_tokens = 2000
        settings.temperature = 0.4

        chat_history = ChatHistory(system_message=system_prompt)
        chat_history.add_user_message(
            "Synthesize the two ideas and return a JSON object with the "
            "synthesis_message and board_instructions."
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
                "[merge_synthesizer] First parse failed, retrying with format instruction"
            )
            chat_history.add_assistant_message(raw_response)
            chat_history.add_user_message(
                "Your previous response was not valid JSON matching the required "
                "schema. Please return ONLY a JSON object with these exact fields: "
                "synthesis_message (string, min 100 chars) and board_instructions "
                "(array of objects, each with at least 'intent' and 'description')."
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
                    "[merge_synthesizer] Retry also failed — returning empty synthesis"
                )
                return {
                    "synthesis_message": "",
                    "board_instructions": [],
                }

        logger.info(
            "[merge_synthesizer] Synthesis complete: message=%d chars, "
            "board_instructions=%d",
            len(output.synthesis_message),
            len(output.board_instructions),
        )

        return output.model_dump()

    @staticmethod
    def _validate_output(raw_response: str) -> MergeSynthesizerOutput | None:
        """Parse and validate the LLM response via Pydantic.

        Returns the validated model or None if parsing/validation fails.
        """
        try:
            parsed = json.loads(raw_response.strip())
            return MergeSynthesizerOutput.model_validate(parsed)
        except (json.JSONDecodeError, Exception):
            logger.debug(
                "[merge_synthesizer] Validation failed for response: %s",
                raw_response[:200],
            )
            return None
