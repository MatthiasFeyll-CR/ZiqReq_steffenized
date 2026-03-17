"""Summarizing AI system prompt template.

Builds the system prompt for the Summarizing AI agent, which generates
hierarchical requirements documents (Epics/Stories or Milestones/Packages)
from project requirements data.
"""

from __future__ import annotations

from typing import Any


def build_system_prompt(input_data: dict[str, Any]) -> str:
    """Build the Summarizing AI system prompt.

    Args:
        input_data: Dict with keys:
            - mode: str — generation mode (full_generation, selective_regeneration,
              item_regeneration)
            - project_type: str — 'software' or 'non_software'
            - chat_summary: str — summary of chat context
            - recent_messages: list[dict] — last 20 chat messages
            - locked_items: dict[str, bool] — locked item IDs
            - allow_information_gaps: bool — whether to allow /TODO markers
            - item_id: str | None — for item_regeneration mode

    Returns:
        Rendered system prompt string.
    """
    mode = input_data.get("mode", "full_generation")
    project_type = input_data.get("project_type", "software")
    chat_summary = input_data.get("chat_summary", "")
    recent_messages = input_data.get("recent_messages", [])
    locked_items = input_data.get("locked_items", {})
    allow_information_gaps = input_data.get("allow_information_gaps", False)
    item_id = input_data.get("item_id")

    messages_formatted = _format_messages(recent_messages)
    mode_instructions = _build_mode_instructions(mode, locked_items, item_id, project_type)
    gaps_instructions = _build_gaps_instructions(allow_information_gaps)
    output_format = _build_output_format(project_type)
    readiness_spec = _build_readiness_spec(project_type)

    return f"""<system>
<identity>You are a requirements document generator for ZiqReq at Commerz Real. Your role is to \
generate structured hierarchical requirements documents from project requirements data.</identity>

<critical_rule>
NEVER FABRICATE INFORMATION. If the project discussion did not produce enough information for an \
item, output "Not enough information." Do NOT fill gaps with invented, inferred, or assumed \
content. Every claim in the document must be traceable to the chat messages provided.
</critical_rule>

<generation_mode>{mode}</generation_mode>
<project_type>{project_type}</project_type>

{readiness_spec}

{gaps_instructions}

<mode_instructions>
{mode_instructions}
</mode_instructions>

<project>
  <chat_summary>{chat_summary}</chat_summary>
  <recent_messages>
{messages_formatted}
  </recent_messages>
</project>

{output_format}
</system>"""


def _format_messages(messages: list[dict[str, Any]]) -> str:
    """Format recent messages for the prompt."""
    if not messages:
        return "    (no recent messages)"
    lines = []
    for msg in messages:
        sender = msg.get("sender_type", "unknown")
        agent = msg.get("ai_agent", "")
        content = msg.get("content", "")
        label = f"{sender}" if not agent else f"{sender}({agent})"
        lines.append(f"    <message sender=\"{label}\">{content}</message>")
    return "\n".join(lines)


def _build_mode_instructions(
    mode: str,
    locked_items: dict[str, bool],
    item_id: str | None,
    project_type: str,
) -> str:
    """Build mode-specific instructions."""
    if project_type == "software":
        parent_label = "epics"
        child_label = "user stories"
    else:
        parent_label = "milestones"
        child_label = "work packages"

    if mode == "full_generation":
        return (
            f"Generate ALL {parent_label} and {child_label} from scratch "
            "based on the project requirements data."
        )
    elif mode == "selective_regeneration":
        locked_ids = [k for k, v in locked_items.items() if v]
        locked_str = ", ".join(locked_ids) if locked_ids else "(none)"
        return (
            f"Regenerate ONLY unlocked {parent_label} and {child_label}.\n"
            f"Locked items (DO NOT regenerate, preserve as-is): {locked_str}\n"
            "For locked items, include them in the output exactly as they are."
        )
    elif mode == "item_regeneration":
        return (
            f"Regenerate ONLY the item with ID: {item_id}\n"
            "Include all other items as-is in the output."
        )
    return (
        f"Generate ALL {parent_label} and {child_label} from scratch "
        "based on the project requirements data."
    )


def _build_gaps_instructions(allow_information_gaps: bool) -> str:
    """Build information gaps instructions."""
    if allow_information_gaps:
        return (
            "<information_gaps_mode>\n"
            "When information is insufficient for an item, leave /TODO markers:\n"
            '"/TODO: [What information is needed]"\n'
            "This helps users identify what additional requirements discussion is needed.\n"
            "</information_gaps_mode>"
        )
    return (
        "<no_gaps_mode>\n"
        "When information is insufficient for an item, output exactly\n"
        '"Not enough information." — do NOT use /TODO markers or fabricate.\n'
        "</no_gaps_mode>"
    )


def _build_output_format(project_type: str) -> str:
    """Build the output format specification based on project type."""
    if project_type == "software":
        return """<output_format>
Respond with ONLY a valid JSON object with this structure:
{
  "title": "Project title",
  "short_description": "1-2 sentence summary",
  "structure": [
    {
      "epic_id": "unique-id",
      "title": "Epic title",
      "description": "Detailed epic description (2-4 paragraphs)",
      "stories": [
        {
          "story_id": "unique-id",
          "title": "As a [role], I want [capability] so that [benefit]",
          "description": "Story details (1-2 paragraphs)",
          "acceptance_criteria": "Bullet list of testable criteria",
          "priority": "High | Medium | Low"
        }
      ]
    }
  ],
  "readiness_evaluation": {
    "ready_for_development": true or false,
    "missing_information": ["list of gaps"],
    "recommendation": "summary recommendation"
  }
}

Do NOT include any text before or after the JSON object.
</output_format>"""
    else:
        return """<output_format>
Respond with ONLY a valid JSON object with this structure:
{
  "title": "Project title",
  "short_description": "1-2 sentence summary",
  "structure": [
    {
      "milestone_id": "unique-id",
      "title": "Milestone title",
      "description": "Detailed milestone description (2-4 paragraphs)",
      "packages": [
        {
          "package_id": "unique-id",
          "title": "Work package title",
          "description": "Package details (1-2 paragraphs)",
          "deliverables": "Bullet list of concrete deliverables",
          "dependencies": "What must be completed first or what this depends on"
        }
      ]
    }
  ],
  "readiness_evaluation": {
    "ready_for_execution": true or false,
    "missing_information": ["list of gaps"],
    "recommendation": "summary recommendation"
  }
}

Do NOT include any text before or after the JSON object.
</output_format>"""


def _build_readiness_spec(project_type: str) -> str:
    """Build the readiness evaluation specification based on project type."""
    if project_type == "software":
        return (
            "<readiness_evaluation>\n"
            "Evaluate readiness for development:\n"
            "  - Ready when ALL epics have at least one user story with acceptance criteria\n"
            "  - Missing information: list any epics without stories, or stories without acceptance criteria\n"
            "  - Set ready_for_development to true only when all criteria are met\n"
            "</readiness_evaluation>"
        )
    else:
        return (
            "<readiness_evaluation>\n"
            "Evaluate readiness for execution:\n"
            "  - Ready when ALL milestones have at least one work package with deliverables\n"
            "  - Missing information: list any milestones without packages, or packages without deliverables\n"
            "  - Set ready_for_execution to true only when all criteria are met\n"
            "</readiness_evaluation>"
        )
