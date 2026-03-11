"""Context Compression Agent system prompt template."""

from __future__ import annotations

from typing import Any


def build_system_prompt(
    messages_to_compress: list[dict[str, Any]],
    previous_summary: str | None = None,
) -> str:
    """Build the Context Compression Agent system prompt.

    Args:
        messages_to_compress: New messages to compress into the summary.
        previous_summary: Existing summary from prior compression iterations (if any).

    Returns:
        Rendered system prompt string.
    """
    messages_formatted = _format_messages(messages_to_compress)
    previous_section = (
        f"<previous_summary>\n{previous_summary}\n</previous_summary>"
        if previous_summary
        else "<previous_summary>(no previous summary — this is the first compression)</previous_summary>"
    )

    return f"""<system>
<identity>You are the Context Compression Agent for ZiqReq, responsible for \
summarizing older chat messages into a concise compressed context that preserves \
conversation continuity without exceeding token limits.</identity>

<mode>Incremental summarization</mode>

{previous_section}

<new_messages_to_compress>
{messages_formatted}
</new_messages_to_compress>

<compression_rules>
1. Produce a single cohesive summary that integrates the previous summary (if any) with the new messages
2. Preserve key decisions, agreements, and action items with attribution to users by name
3. Preserve topic threads and their progression — do not lose the narrative arc
4. Keep user names attached to their contributions and decisions
5. Preserve any technical specifics, numbers, dates, or deadlines mentioned
6. Omit greetings, filler, and repetitive acknowledgments
7. Use concise, factual language — no opinions or interpretations
8. Structure the summary with clear topic sections when multiple threads exist
9. The summary should be significantly shorter than the original messages
10. NEVER fabricate information not present in the previous summary or new messages
</compression_rules>

<output_format>
Return ONLY the compressed summary text. Do not include XML tags, headers, or metadata.
The summary will be injected directly into future prompts as conversation context.
</output_format>
</system>"""


def _format_messages(messages: list[dict[str, Any]]) -> str:
    """Format chat messages for compression."""
    if not messages:
        return "(no messages to compress)"
    lines = []
    for msg in messages:
        sender_type = msg.get("sender_type", "unknown")
        sender_id = msg.get("sender_id", "")
        ai_agent = msg.get("ai_agent", "")
        content = msg.get("content", "")
        created_at = msg.get("created_at", "")
        sender_label = ai_agent if ai_agent else (sender_id or sender_type)
        lines.append(
            f'<message sender="{sender_label}" sender_type="{sender_type}" '
            f'timestamp="{created_at}">\n'
            f"{content}\n"
            f"</message>"
        )
    return "\n".join(lines)
