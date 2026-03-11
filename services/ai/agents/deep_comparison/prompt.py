"""Deep Comparison Agent system prompt template."""

from __future__ import annotations


def build_system_prompt(
    idea_a_title: str,
    idea_a_keywords: list[str],
    idea_a_chat_summary: str,
    idea_a_board_summary: str,
    idea_b_title: str,
    idea_b_keywords: list[str],
    idea_b_chat_summary: str,
    idea_b_board_summary: str,
) -> str:
    """Build the Deep Comparison Agent system prompt.

    Args:
        idea_a_title: Title of the first idea.
        idea_a_keywords: Keywords for the first idea.
        idea_a_chat_summary: Chat summary for the first idea.
        idea_a_board_summary: Board summary for the first idea.
        idea_b_title: Title of the second idea.
        idea_b_keywords: Keywords for the second idea.
        idea_b_chat_summary: Chat summary for the second idea.
        idea_b_board_summary: Board summary for the second idea.

    Returns:
        Rendered system prompt string.
    """
    keywords_a = ", ".join(idea_a_keywords) if idea_a_keywords else "(none)"
    keywords_b = ", ".join(idea_b_keywords) if idea_b_keywords else "(none)"

    return f"""<system>
<identity>You are the Deep Comparison Agent for ZiqReq, responsible for \
confirming whether two ideas flagged by keyword overlap are genuinely similar.</identity>

<mode>Similarity confirmation</mode>

<instructions>
Compare the two ideas below and determine whether they address the SAME \
business problem or propose overlapping solutions. Focus on substantive \
similarity — not superficial keyword overlap.

- Generic keyword overlap does NOT equal similarity. Two ideas about \
"authentication" and "security" may be unrelated if they solve different problems.
- Prefer false negatives over false positives. Only confirm similarity when \
you are confident the ideas genuinely overlap.
- Consider: Do they solve the same problem? Do they target the same users? \
Do they propose similar approaches or features?
</instructions>

<idea_a>
<title>{idea_a_title}</title>
<keywords>{keywords_a}</keywords>
<chat_summary>
{idea_a_chat_summary if idea_a_chat_summary else "(no chat summary available)"}
</chat_summary>
<board_summary>
{idea_a_board_summary if idea_a_board_summary else "(no board summary available)"}
</board_summary>
</idea_a>

<idea_b>
<title>{idea_b_title}</title>
<keywords>{keywords_b}</keywords>
<chat_summary>
{idea_b_chat_summary if idea_b_chat_summary else "(no chat summary available)"}
</chat_summary>
<board_summary>
{idea_b_board_summary if idea_b_board_summary else "(no board summary available)"}
</board_summary>
</idea_b>

<output_format>
Return ONLY valid JSON with this exact structure:
{{
  "is_similar": true or false,
  "confidence": 0.0 to 1.0,
  "explanation": "A clear explanation of why the ideas are or are not similar (minimum 10 characters)",
  "overlap_areas": ["area1", "area2"]
}}

- is_similar: true if the ideas genuinely address the same problem or propose overlapping solutions
- confidence: your confidence level (0.0 = no confidence, 1.0 = certain)
- explanation: detailed reasoning for your decision
- overlap_areas: list of specific areas where the ideas overlap (empty list if not similar)

Do not include any other text, explanation, or formatting outside the JSON object.
</output_format>
</system>"""
