"""SummarizingAIAgent — generates 6-section BRDs from project requirements data.

Extends BaseAgent with direct chat completion (no tools). Supports 3 modes:
full_generation, selective_regeneration, and section_regeneration.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory

from agents.base import BaseAgent
from agents.summarizing_ai.prompt import SECTION_KEYS, build_system_prompt
from kernel.model_router import get_deployment
from kernel.sk_factory import create_kernel

logger = logging.getLogger(__name__)


class SummarizingAIAgent(BaseAgent):
    """Summarizing AI Agent — generates structured BRDs.

    Supports 3 generation modes:
    - full_generation: generates all 6 sections
    - selective_regeneration: only regenerates unlocked sections
    - section_regeneration: regenerates a single specified section
    """

    agent_name: str = "summarizing_ai"
    fixture_file: str = "summarizing_ai_response.json"

    async def _execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the Summarizing AI via Semantic Kernel.

        Args:
            input_data: Dict with keys:
                - mode: str — generation mode
                - chat_summary: str — summary of chat context
                - recent_messages: list[dict] — last 20 messages
                - locked_sections: list[str] — locked section names
                - allow_information_gaps: bool — /TODO vs 'Not enough information'
                - section_name: str | None — for section_regeneration mode
        """
        mode = input_data.get("mode", "full_generation")

        # Build system prompt
        system_prompt = build_system_prompt(input_data)

        # Create kernel with default tier
        deployment = get_deployment("default")
        kernel = create_kernel(deployment, service_id="summarizing_ai")

        # Get chat completion service
        service = kernel.get_service("summarizing_ai")
        assert isinstance(service, AzureChatCompletion)

        settings = service.get_prompt_execution_settings_class()(
            service_id="summarizing_ai"
        )
        settings.max_tokens = 3000
        settings.temperature = 0.3

        # Build chat history
        chat_history = ChatHistory(system_message=system_prompt)
        chat_history.add_user_message(
            "Generate the BRD sections based on the project requirements data provided."
        )

        # Invoke SK chat completion
        result = await service.get_chat_message_contents(
            chat_history=chat_history,
            settings=settings,
            kernel=kernel,
        )

        response_text = str(result[0]) if result else ""

        # Parse JSON response
        parsed = _parse_response(response_text)

        # Apply mode logic
        output = _apply_mode_logic(parsed, input_data)

        logger.info(
            "[summarizing_ai] Generated BRD (mode=%s) — readiness: %s",
            mode,
            output.get("readiness_evaluation", {}),
        )

        return output

    async def _load_mock_response(
        self, input_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Load mock response and apply mode logic."""
        raw = await super()._load_mock_response(input_data)
        return _apply_mode_logic(raw, input_data)


def _parse_response(text: str) -> dict[str, Any]:
    """Parse the JSON response from the LLM.

    Handles cases where the LLM wraps JSON in markdown code blocks.
    """
    cleaned = text.strip()
    # Strip markdown code fences if present
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Remove first and last line (code fences)
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logger.error("[summarizing_ai] Failed to parse response: %s", text[:200])
        # Return empty BRD with all sections insufficient
        return {
            f"section_{key}": "Not enough information."
            for key in SECTION_KEYS
        } | {
            "readiness_evaluation": {
                key: "insufficient" for key in SECTION_KEYS
            }
        }


def _apply_mode_logic(
    parsed: dict[str, Any], input_data: dict[str, Any]
) -> dict[str, Any]:
    """Apply generation mode logic to the parsed response.

    - selective_regeneration: nullify locked sections
    - section_regeneration: nullify all except target section
    """
    mode = input_data.get("mode", "full_generation")
    locked_sections = input_data.get("locked_sections", [])
    section_name = input_data.get("section_name")

    # Ensure readiness_evaluation exists
    readiness = parsed.get("readiness_evaluation", {})
    if not readiness:
        readiness = {key: "insufficient" for key in SECTION_KEYS}

    output: dict[str, Any] = {}

    if mode == "selective_regeneration":
        for key in SECTION_KEYS:
            section_field = f"section_{key}"
            if key in locked_sections:
                output[section_field] = None
                # Preserve existing readiness for locked sections
                readiness[key] = readiness.get(key, "insufficient")
            else:
                output[section_field] = parsed.get(section_field)
    elif mode == "section_regeneration":
        for key in SECTION_KEYS:
            section_field = f"section_{key}"
            if key == section_name:
                output[section_field] = parsed.get(section_field)
            else:
                output[section_field] = None
    else:
        # full_generation — include all sections
        for key in SECTION_KEYS:
            section_field = f"section_{key}"
            output[section_field] = parsed.get(section_field)

    output["readiness_evaluation"] = readiness
    return output
