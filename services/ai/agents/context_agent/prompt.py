"""Context Agent system prompt template."""

from __future__ import annotations

from typing import Any


def build_system_prompt(query: str, chunks: list[dict[str, Any]]) -> str:
    """Build the Context Agent system prompt with query and retrieved chunks.

    Args:
        query: The user's question or search query.
        chunks: Retrieved context chunks from pgvector search.

    Returns:
        Rendered system prompt string.
    """
    chunks_formatted = _format_chunks(chunks)

    return f"""<system>
<identity>You are the Context Agent for ZiqReq, responsible for answering company-specific \
questions using only the retrieved context chunks provided below.</identity>

<mode>RAG retrieval + grounding</mode>

<query>{query}</query>

<retrieved_context>
{chunks_formatted}
</retrieved_context>

<grounding_rules>
1. You MUST only use information from the retrieved context chunks above
2. Cite the source_section when referencing specific information
3. If no relevant chunks are retrieved, respond with: "I don't have enough context to answer \
that question. The knowledge base doesn't contain relevant information on this topic."
4. NEVER fabricate, hallucinate, or infer information not present in the chunks
5. If the chunks contain partial information, clearly state what you can and cannot answer
6. When multiple chunks are relevant, synthesize them into a coherent response
7. Keep responses concise and directly relevant to the query
</grounding_rules>

<citation_rules>
- Reference chunks by their source_section (e.g., "According to [section_name]...")
- If a chunk has no source_section, reference it as "company context"
- Do not invent section names not present in the chunks
</citation_rules>
</system>"""


def _format_chunks(chunks: list[dict[str, Any]]) -> str:
    """Format retrieved chunks for prompt injection."""
    if not chunks:
        return "(no relevant chunks retrieved)"
    lines = []
    for i, chunk in enumerate(chunks, 1):
        chunk_id = chunk.get("id", "?")
        text = chunk.get("chunk_text", "")
        source = chunk.get("source_section") or "general"
        similarity = chunk.get("similarity", 0.0)
        lines.append(
            f'<chunk id="{chunk_id}" source_section="{source}" relevance="{similarity}">\n'
            f"{text}\n"
            f"</chunk>"
        )
    return "\n".join(lines)
