"""SummarizingAIAgent — generates hierarchical requirements documents.

Extends BaseAgent with direct chat completion (no tools). Supports 3 modes:
full_generation, selective_regeneration, and item_regeneration.
Output is hierarchical: Epics/Stories (software) or Milestones/Packages (non-software).
"""

from __future__ import annotations

import json
import logging
from typing import Any

from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory

from agents.base import BaseAgent
from agents.summarizing_ai.prompt import build_system_prompt
from kernel.model_router import get_deployment
from kernel.sk_factory import create_kernel

logger = logging.getLogger(__name__)


class SummarizingAIAgent(BaseAgent):
    """Summarizing AI Agent — generates hierarchical requirements documents.

    Supports 3 generation modes:
    - full_generation: generates all items from scratch
    - selective_regeneration: only regenerates unlocked items
    - item_regeneration: regenerates a single epic/milestone or story/package
    """

    agent_name: str = "summarizing_ai"
    fixture_file: str = "summarizing_ai_response.json"

    async def _execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the Summarizing AI via Semantic Kernel.

        Args:
            input_data: Dict with keys:
                - mode: str — generation mode
                - project_type: str — 'software' or 'non_software'
                - chat_summary: str — summary of chat context
                - recent_messages: list[dict] — last 20 messages
                - locked_items: dict[str, bool] — locked item IDs
                - allow_information_gaps: bool — /TODO vs 'Not enough information'
                - item_id: str | None — for item_regeneration mode
        """
        mode = input_data.get("mode", "full_generation")
        project_type = input_data.get("project_type", "software")

        system_prompt = build_system_prompt(input_data)

        deployment = get_deployment("default")
        kernel = create_kernel(deployment, service_id="summarizing_ai")

        service = kernel.get_service("summarizing_ai")
        assert isinstance(service, AzureChatCompletion)

        settings = service.get_prompt_execution_settings_class()(
            service_id="summarizing_ai"
        )
        settings.max_tokens = 4000
        settings.temperature = 0.3

        chat_history = ChatHistory(system_message=system_prompt)
        chat_history.add_user_message(
            "Generate the requirements document based on the project data provided."
        )

        result = await service.get_chat_message_contents(
            chat_history=chat_history,
            settings=settings,
            kernel=kernel,
        )

        response_text = str(result[0]) if result else ""

        parsed = _parse_response(response_text, project_type)
        output = _apply_mode_logic(parsed, input_data)

        logger.info(
            "[summarizing_ai] Generated requirements doc (mode=%s, type=%s) — readiness: %s",
            mode,
            project_type,
            output.get("readiness_evaluation", {}),
        )

        return output

    async def _load_mock_response(
        self, input_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Load mock response and apply mode logic."""
        raw = await super()._load_mock_response(input_data)
        return _apply_mode_logic(raw, input_data)


def _parse_response(text: str, project_type: str) -> dict[str, Any]:
    """Parse the JSON response from the LLM.

    Handles cases where the LLM wraps JSON in markdown code blocks.
    Validates the structure matches the expected project_type format.
    """
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.error("[summarizing_ai] Failed to parse response: %s", text[:200])
        return _empty_response(project_type)

    if not _validate_structure(parsed, project_type):
        logger.warning(
            "[summarizing_ai] Response structure invalid for project_type=%s",
            project_type,
        )
        return _empty_response(project_type)

    return parsed


def _validate_structure(parsed: dict[str, Any], project_type: str) -> bool:
    """Validate the parsed response has the expected hierarchical structure."""
    if not isinstance(parsed, dict):
        return False
    if "structure" not in parsed:
        return False
    structure = parsed["structure"]
    if not isinstance(structure, list):
        return False

    if project_type == "software":
        for item in structure:
            if not isinstance(item, dict):
                return False
            if "epic_id" not in item:
                return False
    else:
        for item in structure:
            if not isinstance(item, dict):
                return False
            if "milestone_id" not in item:
                return False

    return True


def _empty_response(project_type: str) -> dict[str, Any]:
    """Return an empty response when parsing or validation fails."""
    if project_type == "software":
        return {
            "title": "Not enough information.",
            "short_description": "Not enough information.",
            "structure": [],
            "readiness_evaluation": {
                "ready_for_development": False,
                "missing_information": ["Failed to generate requirements document."],
                "recommendation": "Continue discussion to provide more detail.",
            },
        }
    else:
        return {
            "title": "Not enough information.",
            "short_description": "Not enough information.",
            "structure": [],
            "readiness_evaluation": {
                "ready_for_execution": False,
                "missing_information": ["Failed to generate requirements document."],
                "recommendation": "Continue discussion to provide more detail.",
            },
        }


def _apply_mode_logic(
    parsed: dict[str, Any], input_data: dict[str, Any]
) -> dict[str, Any]:
    """Apply generation mode logic to the parsed response.

    - selective_regeneration: preserve locked items as-is
    - item_regeneration: only regenerate the target item
    """
    mode = input_data.get("mode", "full_generation")
    project_type = input_data.get("project_type", "software")

    readiness = parsed.get("readiness_evaluation", {})
    if not readiness:
        if project_type == "software":
            readiness = {
                "ready_for_development": False,
                "missing_information": [],
                "recommendation": "",
            }
        else:
            readiness = {
                "ready_for_execution": False,
                "missing_information": [],
                "recommendation": "",
            }

    output: dict[str, Any] = {
        "title": parsed.get("title", ""),
        "short_description": parsed.get("short_description", ""),
        "structure": parsed.get("structure", []),
        "readiness_evaluation": readiness,
    }

    if mode == "selective_regeneration":
        locked_items = input_data.get("locked_items", {})
        # Structure items are kept as-is; the LLM was instructed to preserve locked items
        # We just ensure locked items are not removed from the output
        output["locked_items_preserved"] = list(locked_items.keys())

    elif mode == "item_regeneration":
        item_id = input_data.get("item_id")
        output["regenerated_item_id"] = item_id

    return output
