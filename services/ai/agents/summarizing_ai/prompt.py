"""Summarizing AI system prompt template.

Builds the system prompt for the Summarizing AI agent, which generates
6-section BRDs from brainstorming data.
"""

from __future__ import annotations

from typing import Any

# The 6 BRD section keys in canonical order
SECTION_KEYS = [
    "title",
    "short_description",
    "current_workflow",
    "affected_department",
    "core_capabilities",
    "success_criteria",
]

SECTION_LABELS = {
    "title": "1. Title",
    "short_description": "2. Short Description",
    "current_workflow": "3. Current Workflow & Pain Points",
    "affected_department": "4. Affected Department",
    "core_capabilities": "5. Core Capabilities",
    "success_criteria": "6. Success Criteria",
}

# Minimum information anchors for readiness evaluation
READINESS_ANCHORS = {
    "title": "3+ keywords from chat",
    "short_description": "1+ pain point or goal",
    "current_workflow": "2+ process steps",
    "affected_department": "1+ team/department",
    "core_capabilities": "2+ capabilities",
    "success_criteria": "1+ measurable outcome",
}


def build_system_prompt(input_data: dict[str, Any]) -> str:
    """Build the Summarizing AI system prompt.

    Args:
        input_data: Dict with keys:
            - mode: str — generation mode
            - chat_summary: str — summary of chat context
            - recent_messages: list[dict] — last 20 chat messages
            - locked_sections: list[str] — locked section names
            - allow_information_gaps: bool — whether to allow /TODO markers
            - section_name: str | None — for section_regeneration mode

    Returns:
        Rendered system prompt string.
    """
    mode = input_data.get("mode", "full_generation")
    chat_summary = input_data.get("chat_summary", "")
    recent_messages = input_data.get("recent_messages", [])
    locked_sections = input_data.get("locked_sections", [])
    allow_information_gaps = input_data.get("allow_information_gaps", False)
    section_name = input_data.get("section_name")

    messages_formatted = _format_messages(recent_messages)
    mode_instructions = _build_mode_instructions(mode, locked_sections, section_name)
    gaps_instructions = _build_gaps_instructions(allow_information_gaps)
    sections_spec = _build_sections_spec()
    readiness_spec = _build_readiness_spec()

    return f"""<system>
<identity>You are the Summarizing AI for ZiqReq at Commerz Real. Your role is to generate \
structured Business Requirements Documents (BRDs) from brainstorming session data.</identity>

<critical_rule>
NEVER FABRICATE INFORMATION. If the brainstorming did not produce enough information for a \
section, output "Not enough information." Do NOT fill gaps with invented, inferred, or assumed \
content. Every claim in the BRD must be traceable to the chat messages provided.
</critical_rule>

<sections>
{sections_spec}
</sections>

<readiness_evaluation>
Evaluate each section: "ready" (sufficient detail) or "insufficient" (lacks detail).
Minimum information anchors:
{readiness_spec}
</readiness_evaluation>

{gaps_instructions}

<mode_instructions>
{mode_instructions}
</mode_instructions>

<idea>
  <chat_summary>{chat_summary}</chat_summary>
  <recent_messages>
{messages_formatted}
  </recent_messages>
</idea>

<output_format>
Respond with ONLY a valid JSON object containing these keys:
- section_title: string
- section_short_description: string
- section_current_workflow: string
- section_affected_department: string
- section_core_capabilities: string
- section_success_criteria: string
- readiness_evaluation: object with keys (title, short_description, current_workflow, \
affected_department, core_capabilities, success_criteria) each valued "ready" or "insufficient"

Do NOT include any text before or after the JSON object.
</output_format>
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
    mode: str, locked_sections: list[str], section_name: str | None
) -> str:
    """Build mode-specific instructions."""
    if mode == "full_generation":
        return "Generate ALL 6 sections from scratch based on the brainstorming data."
    elif mode == "selective_regeneration":
        locked_str = ", ".join(locked_sections) if locked_sections else "(none)"
        unlocked = [s for s in SECTION_KEYS if s not in locked_sections]
        unlocked_str = ", ".join(unlocked) if unlocked else "(none)"
        return (
            f"Regenerate ONLY the unlocked sections: {unlocked_str}\n"
            f"Locked sections (DO NOT regenerate, return null for these): {locked_str}\n"
            "For locked sections, set the section value to null in the JSON output."
        )
    elif mode == "section_regeneration":
        return (
            f"Regenerate ONLY the section: {section_name}\n"
            "For all other sections, set the section value to null in the JSON output.\n"
            "Only evaluate readiness for the regenerated section; set others to their current status or null."
        )
    return "Generate ALL 6 sections from scratch."


def _build_gaps_instructions(allow_information_gaps: bool) -> str:
    """Build information gaps instructions."""
    if allow_information_gaps:
        return (
            "<information_gaps_mode>\n"
            "When information is insufficient for a section, leave /TODO markers:\n"
            '"/TODO: [What information is needed]"\n'
            "This helps users identify what additional brainstorming is needed.\n"
            "</information_gaps_mode>"
        )
    return (
        "<no_gaps_mode>\n"
        "When information is insufficient for a section, output exactly\n"
        '"Not enough information." — do NOT use /TODO markers or fabricate.\n'
        "</no_gaps_mode>"
    )


def _build_sections_spec() -> str:
    """Build the sections specification."""
    return "\n".join(
        f"  {label}: {_section_description(key)}"
        for key, label in SECTION_LABELS.items()
    )


def _section_description(key: str) -> str:
    """Return a brief description for each section."""
    descriptions = {
        "title": "Concise, descriptive title for the requirement",
        "short_description": "2-3 sentence summary of the requirement",
        "current_workflow": "Describe the current process and its pain points",
        "affected_department": "Which teams and departments this impacts",
        "core_capabilities": "What users will be able to do with the solution",
        "success_criteria": "Measurable outcomes that define success",
    }
    return descriptions.get(key, "")


def _build_readiness_spec() -> str:
    """Build the readiness evaluation specification."""
    return "\n".join(
        f"  - {SECTION_LABELS[key]}: {anchor}"
        for key, anchor in READINESS_ANCHORS.items()
    )
