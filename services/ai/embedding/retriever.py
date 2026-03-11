"""pgvector cosine similarity search for RAG retrieval."""

from __future__ import annotations

import logging
from typing import Any

from grpc_clients.core_client import CoreClient

logger = logging.getLogger(__name__)


class Retriever:
    """Retrieves context chunks via pgvector cosine similarity search.

    Uses admin-configurable top_k and min_similarity threshold.
    """

    def __init__(
        self,
        top_k: int | None = None,
        min_similarity: float | None = None,
    ) -> None:
        self._top_k = top_k
        self._min_similarity = min_similarity

    @property
    def top_k(self) -> int:
        if self._top_k is not None:
            return self._top_k
        try:
            client = CoreClient()
            result = client.get_admin_parameter("context_rag_top_k")
            value = result.get("value", "")
            if value:
                return int(value)
        except Exception:
            logger.debug("Could not read context_rag_top_k — using default")
        return 5

    @property
    def min_similarity(self) -> float:
        if self._min_similarity is not None:
            return self._min_similarity
        try:
            client = CoreClient()
            result = client.get_admin_parameter("context_rag_min_similarity")
            value = result.get("value", "")
            if value:
                return float(value)
        except Exception:
            logger.debug("Could not read context_rag_min_similarity — using default")
        return 0.7

    async def retrieve(
        self,
        query_embedding: list[float],
        bucket_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve top_k chunks by cosine similarity to query_embedding.

        Args:
            query_embedding: The embedding vector for the query (1536 dims).
            bucket_id: Optional filter to a specific bucket.

        Returns:
            List of chunk dicts with keys: id, chunk_text, source_section, similarity.
            Filtered by min_similarity threshold, ordered by descending similarity.
        """
        from pgvector.django import CosineDistance

        from apps.embedding.models import ContextChunk

        top_k = self.top_k
        min_similarity = self.min_similarity

        queryset = ContextChunk.objects.annotate(
            distance=CosineDistance("embedding", query_embedding),
        )

        if bucket_id:
            queryset = queryset.filter(bucket_id=bucket_id)

        # Cosine distance = 1 - cosine_similarity, so filter distance < (1 - min_similarity)
        max_distance = 1.0 - min_similarity
        queryset = queryset.filter(distance__lte=max_distance)

        queryset = queryset.order_by("distance")[:top_k]

        results = []
        for chunk in queryset:
            similarity = 1.0 - chunk.distance
            results.append({
                "id": str(chunk.id),
                "chunk_text": chunk.chunk_text,
                "source_section": chunk.source_section,
                "similarity": round(similarity, 4),
            })

        logger.info(
            "Retriever found %d chunks (top_k=%d, min_similarity=%.2f)",
            len(results),
            top_k,
            min_similarity,
        )
        return results
