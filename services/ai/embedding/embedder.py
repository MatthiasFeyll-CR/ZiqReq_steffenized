"""Azure OpenAI text-embedding-3-small wrapper."""

from __future__ import annotations

import logging
from typing import Any

from django.conf import settings

logger = logging.getLogger(__name__)


class Embedder:
    """Generates embeddings via Azure OpenAI text-embedding-3-small.

    Uses the AZURE_OPENAI_EMBEDDING_DEPLOYMENT setting for the deployment name.
    """

    def __init__(self, deployment_name: str | None = None) -> None:
        self._deployment_name = deployment_name

    @property
    def deployment_name(self) -> str:
        if self._deployment_name:
            return self._deployment_name
        return getattr(settings, "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "") or "text-embedding-3-small"

    async def embed(
        self,
        chunks: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Generate embeddings for a list of chunks.

        Args:
            chunks: List of dicts with at least 'chunk_text', 'token_count', 'source_section'.

        Returns:
            Same list with 'embedding' key added (vector(1536)) to each chunk.

        Raises:
            RuntimeError: If embedding API call fails.
        """
        if not chunks:
            return []

        texts = [c["chunk_text"] for c in chunks]

        try:
            embeddings = await self._call_embedding_api(texts)
        except Exception as exc:
            logger.error("Embedding API call failed: %s", exc)
            raise RuntimeError(f"Embedding failed: {exc}") from exc

        if len(embeddings) != len(chunks):
            raise RuntimeError(
                f"Embedding count mismatch: got {len(embeddings)}, expected {len(chunks)}"
            )

        result = []
        for chunk, embedding in zip(chunks, embeddings):
            result.append({
                **chunk,
                "embedding": embedding,
            })

        logger.info("Embedder generated %d embeddings", len(result))
        return result

    async def _call_embedding_api(self, texts: list[str]) -> list[list[float]]:
        """Call Azure OpenAI embedding endpoint.

        Uses openai SDK directly (SK embedding support is limited).
        """
        from openai import AsyncAzureOpenAI

        client = AsyncAzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
        )

        response = await client.embeddings.create(
            input=texts,
            model=self.deployment_name,
        )

        return [item.embedding for item in response.data]
