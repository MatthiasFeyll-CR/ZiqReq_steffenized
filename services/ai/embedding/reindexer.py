"""Full re-index on bucket update.

Deletes all existing context_chunks for a bucket and inserts new
chunked + embedded data. No partial updates — if embedding fails,
the entire operation is rolled back.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from django.db import transaction

logger = logging.getLogger(__name__)


class Reindexer:
    """Orchestrates the full chunk → embed → persist pipeline."""

    def __init__(self) -> None:
        from embedding.chunker import Chunker
        from embedding.embedder import Embedder

        self.chunker = Chunker()
        self.embedder = Embedder()

    async def reindex(
        self,
        bucket_id: str,
        sections: dict[str, str],
        free_text: str,
        context_type: str | None = None,
    ) -> dict[str, Any]:
        """Re-index a context agent bucket: chunk, embed, persist.

        Deletes all existing chunks for the bucket and inserts new ones.
        This is an atomic operation — if embedding fails, no changes are made.

        Args:
            bucket_id: UUID of the context_agent_bucket.
            sections: {section_key: section_text} from bucket.
            free_text: Free text content from bucket.
            context_type: The bucket's context_type (global, software, non_software).

        Returns:
            Dict with chunk_count, total_tokens, duration_ms.

        Raises:
            RuntimeError: If embedding fails (no partial updates).
        """
        start = time.monotonic()

        chunks = self.chunker.chunk(sections, free_text)

        if not chunks:
            logger.info("No content to index for bucket %s — clearing chunks", bucket_id)
            await self._delete_existing_chunks(bucket_id)
            elapsed = int((time.monotonic() - start) * 1000)
            return {"chunk_count": 0, "total_tokens": 0, "duration_ms": elapsed}

        embedded_chunks = await self.embedder.embed(chunks)

        await self._persist_chunks(bucket_id, embedded_chunks, context_type=context_type)

        total_tokens = sum(c["token_count"] for c in embedded_chunks)
        elapsed = int((time.monotonic() - start) * 1000)

        logger.info(
            "Reindex complete for bucket %s: %d chunks, %d tokens, %dms",
            bucket_id,
            len(embedded_chunks),
            total_tokens,
            elapsed,
        )

        return {
            "chunk_count": len(embedded_chunks),
            "total_tokens": total_tokens,
            "duration_ms": elapsed,
        }

    async def _delete_existing_chunks(self, bucket_id: str) -> None:
        """Delete all context_chunks for a bucket."""
        from apps.embedding.models import ContextChunk

        deleted_count, _ = await ContextChunk.objects.filter(
            bucket_id=bucket_id,
        ).adelete()
        logger.info("Deleted %d existing chunks for bucket %s", deleted_count, bucket_id)

    async def _persist_chunks(
        self,
        bucket_id: str,
        embedded_chunks: list[dict[str, Any]],
        context_type: str | None = None,
    ) -> None:
        """Atomically replace all chunks for a bucket."""
        from apps.embedding.models import ContextChunk

        async with transaction.atomic():
            await self._delete_existing_chunks(bucket_id)

            chunk_objects = []
            for idx, chunk in enumerate(embedded_chunks):
                chunk_objects.append(
                    ContextChunk(
                        bucket_id=bucket_id,
                        chunk_index=idx,
                        chunk_text=chunk["chunk_text"],
                        token_count=chunk["token_count"],
                        embedding=chunk["embedding"],
                        source_section=chunk["source_section"],
                        context_type=context_type,
                    )
                )

            await ContextChunk.objects.abulk_create(chunk_objects)
            logger.info(
                "Persisted %d chunks for bucket %s",
                len(chunk_objects),
                bucket_id,
            )
