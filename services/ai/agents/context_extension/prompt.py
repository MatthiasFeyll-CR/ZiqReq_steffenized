"""Context Extension Agent system prompt template."""

from __future__ import annotations

from typing import Any


def build_system_prompt(
    query: str,
    messages: list[dict[str, Any]],
    attachments: list[dict[str, Any]] | None = None,
) -> str:
    """Build the Context Extension Agent system prompt.

    Args:
        query: The user's search query for specific conversation details.
        messages: Full chat history as chronological message list.
        attachments: Optional list of project attachments with extracted_content.

    Returns:
        Rendered system prompt string.
    """
    history_formatted = _format_messages(messages)
    attachments_formatted = _format_attachments(attachments or [])

    return f"""<system>
<identity>You are the Context Extension Agent for ZiqReq, responsible for searching \
through the full uncompressed chat history and project attachments to retrieve specific \
conversation details that may have been lost to context compression.</identity>

<mode>Full chat history + attachment search</mode>

<query>{query}</query>

<full_chat_history>
{history_formatted}
</full_chat_history>

{attachments_formatted}

<retrieval_rules>
1. Search the full chat history and attachment extracted content above to find information relevant to the query
2. Cite specific message timestamps and senders when referencing conversation details
3. If the query matches specific past decisions, agreements, or discussions, extract the exact details
4. If relevant information is found in an attachment, reference it by filename
5. If no relevant messages or attachments are found, state that the history does not contain the requested information
6. NEVER fabricate or invent conversation details not present in the history or attachments
7. Summarize findings concisely, focusing on the most relevant messages and attachment content
8. When multiple messages are relevant, present them in chronological order
</retrieval_rules>

<citation_rules>
- Reference messages by their timestamp and sender (e.g., "On [timestamp], [sender] said...")
- Include the message ID when citing specific messages for traceability
- Reference attachments by filename (e.g., "In the uploaded file [filename]...")
- If a discussion spans multiple messages, summarize the thread with references to key messages
</citation_rules>
</system>"""


def _format_messages(messages: list[dict[str, Any]]) -> str:
    """Format chat messages for prompt injection."""
    if not messages:
        return "(no messages in chat history)"
    lines = []
    for msg in messages:
        msg_id = msg.get("id", "?")
        sender_type = msg.get("sender_type", "unknown")
        sender_id = msg.get("sender_id", "")
        ai_agent = msg.get("ai_agent", "")
        content = msg.get("content", "")
        created_at = msg.get("created_at", "")
        sender_label = ai_agent if ai_agent else (sender_id or sender_type)
        # Append attachment filenames if present
        attachments = msg.get("attachments", [])
        if attachments:
            filenames = ", ".join(a.get("filename", "?") for a in attachments)
            content = f"{content}\n[Attachments: {filenames}]"
        lines.append(
            f'<message id="{msg_id}" sender="{sender_label}" '
            f'sender_type="{sender_type}" timestamp="{created_at}">\n'
            f"{content}\n"
            f"</message>"
        )
    return "\n".join(lines)


def _format_attachments(attachments: list[dict[str, Any]]) -> str:
    """Format project attachments with extracted content for search."""
    if not attachments:
        return ""
    lines = ["<project_attachments>"]
    for att in attachments:
        att_id = att.get("id", "")
        filename = att.get("filename", "")
        content_type = att.get("content_type", "")
        extracted = att.get("extracted_content", "")
        message_id = att.get("message_id") or ""
        lines.append(
            f'<attachment id="{att_id}" filename="{filename}" '
            f'content_type="{content_type}" message_id="{message_id}">\n'
            f"{extracted}\n"
            f"</attachment>"
        )
    lines.append("</project_attachments>")
    return "\n".join(lines)
