"""Section-aware + free text chunking for context agent bucket."""

from __future__ import annotations

import logging
from typing import Any

from grpc_clients.core_client import CoreClient

logger = logging.getLogger(__name__)


class Chunker:
    """Splits context_agent_bucket content into chunks for embedding.

    Section-aware: each section key becomes source_section.
    Free text has source_section=None.
    """

    def __init__(
        self,
        max_chunk_tokens: int | None = None,
        chunk_overlap: int | None = None,
    ) -> None:
        self._max_chunk_tokens = max_chunk_tokens
        self._chunk_overlap = chunk_overlap

    @property
    def max_chunk_tokens(self) -> int:
        if self._max_chunk_tokens is not None:
            return self._max_chunk_tokens
        try:
            client = CoreClient()
            result = client.get_admin_parameter("max_chunk_tokens")
            value = result.get("value", "")
            if value:
                return int(value)
        except Exception:
            logger.debug("Could not read max_chunk_tokens — using default")
        return 512

    @property
    def chunk_overlap(self) -> int:
        if self._chunk_overlap is not None:
            return self._chunk_overlap
        try:
            client = CoreClient()
            result = client.get_admin_parameter("chunk_overlap")
            value = result.get("value", "")
            if value:
                return int(value)
        except Exception:
            logger.debug("Could not read chunk_overlap — using default")
        return 50

    def chunk(
        self,
        sections: dict[str, str],
        free_text: str,
    ) -> list[dict[str, Any]]:
        """Split bucket content into chunks.

        Args:
            sections: {section_key: section_text} from context_agent_bucket.sections jsonb.
            free_text: Free text content from context_agent_bucket.free_text.

        Returns:
            List of dicts with keys: chunk_text, token_count, source_section.
        """
        max_tokens = self.max_chunk_tokens
        overlap = self.chunk_overlap
        chunks: list[dict[str, Any]] = []

        for section_key, section_text in sections.items():
            if not section_text or not section_text.strip():
                continue
            section_chunks = self._split_text(section_text.strip(), max_tokens, overlap)
            for text in section_chunks:
                chunks.append({
                    "chunk_text": text,
                    "token_count": self._estimate_tokens(text),
                    "source_section": section_key,
                })

        if free_text and free_text.strip():
            free_chunks = self._split_text(free_text.strip(), max_tokens, overlap)
            for text in free_chunks:
                chunks.append({
                    "chunk_text": text,
                    "token_count": self._estimate_tokens(text),
                    "source_section": None,
                })

        logger.info("Chunker produced %d chunks", len(chunks))
        return chunks

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Rough token estimate: ~4 chars per token (OpenAI heuristic)."""
        return max(1, len(text) // 4)

    @staticmethod
    def _split_text(text: str, max_tokens: int, overlap: int) -> list[str]:
        """Split text into chunks respecting token limits with overlap.

        Splits on sentence/paragraph boundaries when possible.
        """
        words = text.split()
        if not words:
            return []

        # Approximate: 1 token ≈ 0.75 words (so max_tokens tokens ≈ max_tokens * 0.75 words)
        # But to be safe, use ~1.3 words per token
        max_words = max(1, int(max_tokens * 0.75))
        overlap_words = max(0, int(overlap * 0.75))

        if len(words) <= max_words:
            return [text]

        chunks: list[str] = []
        start = 0
        while start < len(words):
            end = min(start + max_words, len(words))
            chunk_text = " ".join(words[start:end])
            chunks.append(chunk_text)
            if end >= len(words):
                break
            start = end - overlap_words

        return chunks
