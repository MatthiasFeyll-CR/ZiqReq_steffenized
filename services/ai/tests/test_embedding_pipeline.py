"""Tests for the Context Chunks Embedding Pipeline (US-004).

Covers: Chunker, Embedder, Reindexer, and UpdateContextAgentBucket servicer.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from embedding.chunker import Chunker
from embedding.embedder import Embedder

# ── Chunker tests ──


class TestChunker:
    def test_empty_input_returns_empty(self):
        """Chunker returns empty list for empty input."""
        chunker = Chunker(max_chunk_tokens=512, chunk_overlap=50)
        result = chunker.chunk(sections={}, free_text="")
        assert result == []

    def test_single_section_one_chunk(self):
        """Single short section produces one chunk with source_section set."""
        chunker = Chunker(max_chunk_tokens=512, chunk_overlap=50)
        result = chunker.chunk(
            sections={"onboarding": "Welcome to the company. We have a great team."},
            free_text="",
        )
        assert len(result) == 1
        assert result[0]["source_section"] == "onboarding"
        assert "Welcome to the company" in result[0]["chunk_text"]
        assert result[0]["token_count"] > 0

    def test_free_text_has_null_source_section(self):
        """Free text chunks have source_section=None."""
        chunker = Chunker(max_chunk_tokens=512, chunk_overlap=50)
        result = chunker.chunk(
            sections={},
            free_text="Some important context about the company.",
        )
        assert len(result) == 1
        assert result[0]["source_section"] is None
        assert "important context" in result[0]["chunk_text"]

    def test_multiple_sections(self):
        """Multiple sections produce separate chunks each with correct source_section."""
        chunker = Chunker(max_chunk_tokens=512, chunk_overlap=50)
        result = chunker.chunk(
            sections={
                "onboarding": "Welcome to the company.",
                "it_setup": "IT provisioning takes 24 hours.",
            },
            free_text="",
        )
        assert len(result) == 2
        sections = {c["source_section"] for c in result}
        assert sections == {"onboarding", "it_setup"}

    def test_long_text_splits_into_multiple_chunks(self):
        """Long text exceeding max_tokens is split into multiple chunks."""
        chunker = Chunker(max_chunk_tokens=10, chunk_overlap=2)
        long_text = " ".join(f"word{i}" for i in range(100))
        result = chunker.chunk(
            sections={"docs": long_text},
            free_text="",
        )
        assert len(result) > 1
        for chunk in result:
            assert chunk["source_section"] == "docs"

    def test_empty_section_skipped(self):
        """Empty or whitespace-only sections are skipped."""
        chunker = Chunker(max_chunk_tokens=512, chunk_overlap=50)
        result = chunker.chunk(
            sections={"empty": "", "whitespace": "   ", "real": "Content here."},
            free_text="",
        )
        assert len(result) == 1
        assert result[0]["source_section"] == "real"

    def test_sections_and_free_text_combined(self):
        """Both sections and free_text produce chunks."""
        chunker = Chunker(max_chunk_tokens=512, chunk_overlap=50)
        result = chunker.chunk(
            sections={"intro": "Welcome."},
            free_text="Extra info.",
        )
        assert len(result) == 2
        source_sections = [c["source_section"] for c in result]
        assert "intro" in source_sections
        assert None in source_sections

    def test_default_max_chunk_tokens(self):
        """Default max_chunk_tokens is 512 when admin param not available."""
        chunker = Chunker()
        assert chunker.max_chunk_tokens == 512

    def test_default_chunk_overlap(self):
        """Default chunk_overlap is 50 when admin param not available."""
        chunker = Chunker()
        assert chunker.chunk_overlap == 50

    def test_custom_params(self):
        """Custom max_chunk_tokens and chunk_overlap are respected."""
        chunker = Chunker(max_chunk_tokens=256, chunk_overlap=25)
        assert chunker.max_chunk_tokens == 256
        assert chunker.chunk_overlap == 25

    def test_token_estimate(self):
        """Token estimation returns ~4 chars per token."""
        assert Chunker._estimate_tokens("hello world") >= 1
        assert Chunker._estimate_tokens("a" * 400) == 100


# ── Embedder tests ──


class TestEmbedder:
    @pytest.mark.asyncio
    async def test_empty_chunks_returns_empty(self):
        """Embedder returns empty list for empty input."""
        embedder = Embedder()
        result = await embedder.embed([])
        assert result == []

    @pytest.mark.asyncio
    async def test_embed_adds_embedding_key(self):
        """Embedder adds embedding to each chunk."""
        mock_embedding = [0.1] * 1536
        chunks = [
            {"chunk_text": "Hello world", "token_count": 3, "source_section": "test"},
        ]

        embedder = Embedder(deployment_name="test-deploy")
        with patch.object(embedder, "_call_embedding_api", new_callable=AsyncMock) as mock_api:
            mock_api.return_value = [mock_embedding]
            result = await embedder.embed(chunks)

        assert len(result) == 1
        assert result[0]["embedding"] == mock_embedding
        assert result[0]["chunk_text"] == "Hello world"
        assert result[0]["token_count"] == 3

    @pytest.mark.asyncio
    async def test_embed_multiple_chunks(self):
        """Embedder handles multiple chunks."""
        embeddings = [[0.1] * 1536, [0.2] * 1536]
        chunks = [
            {"chunk_text": "First", "token_count": 1, "source_section": "a"},
            {"chunk_text": "Second", "token_count": 1, "source_section": "b"},
        ]

        embedder = Embedder(deployment_name="test-deploy")
        with patch.object(embedder, "_call_embedding_api", new_callable=AsyncMock) as mock_api:
            mock_api.return_value = embeddings
            result = await embedder.embed(chunks)

        assert len(result) == 2
        assert result[0]["embedding"] == embeddings[0]
        assert result[1]["embedding"] == embeddings[1]

    @pytest.mark.asyncio
    async def test_embed_api_failure_raises_runtime_error(self):
        """Embedder raises RuntimeError if API fails."""
        chunks = [{"chunk_text": "test", "token_count": 1, "source_section": None}]
        embedder = Embedder(deployment_name="test-deploy")

        with patch.object(embedder, "_call_embedding_api", new_callable=AsyncMock) as mock_api:
            mock_api.side_effect = Exception("API down")
            with pytest.raises(RuntimeError, match="Embedding failed"):
                await embedder.embed(chunks)

    @pytest.mark.asyncio
    async def test_embed_count_mismatch_raises(self):
        """Embedder raises RuntimeError if embedding count doesn't match chunks."""
        chunks = [
            {"chunk_text": "First", "token_count": 1, "source_section": None},
            {"chunk_text": "Second", "token_count": 1, "source_section": None},
        ]
        embedder = Embedder(deployment_name="test-deploy")

        with patch.object(embedder, "_call_embedding_api", new_callable=AsyncMock) as mock_api:
            mock_api.return_value = [[0.1] * 1536]  # Only 1, but need 2
            with pytest.raises(RuntimeError, match="count mismatch"):
                await embedder.embed(chunks)

    def test_default_deployment_name(self, settings):
        """Embedder uses AZURE_OPENAI_EMBEDDING_DEPLOYMENT by default."""
        settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT = "my-embedding-model"
        embedder = Embedder()
        assert embedder.deployment_name == "my-embedding-model"

    def test_custom_deployment_name(self):
        """Embedder respects custom deployment_name."""
        embedder = Embedder(deployment_name="custom-model")
        assert embedder.deployment_name == "custom-model"


# ── Reindexer tests ──


class TestReindexer:
    def _make_reindexer(self):
        """Create a Reindexer with mocked dependencies."""
        from embedding.reindexer import Reindexer

        with (
            patch("embedding.chunker.Chunker.__init__", return_value=None),
            patch("embedding.embedder.Embedder.__init__", return_value=None),
        ):
            return Reindexer()

    @pytest.mark.asyncio
    async def test_reindex_empty_content(self):
        """Reindex with empty content clears chunks and returns zero counts."""
        reindexer = self._make_reindexer()
        reindexer.chunker = MagicMock()
        reindexer.chunker.chunk.return_value = []
        reindexer.embedder = AsyncMock()

        with patch.object(reindexer, "_delete_existing_chunks", new_callable=AsyncMock):
            result = await reindexer.reindex("bucket-1", {}, "")

        assert result["chunk_count"] == 0
        assert result["total_tokens"] == 0
        assert "duration_ms" in result

    @pytest.mark.asyncio
    async def test_reindex_full_pipeline(self):
        """Reindex orchestrates chunk, embed, persist."""
        chunks = [
            {"chunk_text": "Hello", "token_count": 2, "source_section": "test"},
        ]
        embedded_chunks = [
            {"chunk_text": "Hello", "token_count": 2, "source_section": "test", "embedding": [0.1] * 1536},
        ]

        reindexer = self._make_reindexer()
        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = chunks
        reindexer.chunker = mock_chunker

        mock_embedder = AsyncMock()
        mock_embedder.embed = AsyncMock(return_value=embedded_chunks)
        reindexer.embedder = mock_embedder

        with patch.object(reindexer, "_persist_chunks", new_callable=AsyncMock):
            result = await reindexer.reindex(
                "bucket-1",
                {"test": "Hello world"},
                "",
            )

        assert result["chunk_count"] == 1
        assert result["total_tokens"] == 2
        assert "duration_ms" in result
        mock_chunker.chunk.assert_called_once_with({"test": "Hello world"}, "")
        mock_embedder.embed.assert_called_once_with(chunks)

    @pytest.mark.asyncio
    async def test_reindex_propagates_embedding_error(self):
        """Reindex raises if embedding fails (no partial updates)."""
        chunks = [{"chunk_text": "Hello", "token_count": 2, "source_section": "test"}]

        reindexer = self._make_reindexer()
        reindexer.chunker = MagicMock()
        reindexer.chunker.chunk.return_value = chunks
        reindexer.embedder = AsyncMock()
        reindexer.embedder.embed = AsyncMock(side_effect=RuntimeError("Embedding failed"))

        with pytest.raises(RuntimeError, match="Embedding failed"):
            await reindexer.reindex("bucket-1", {"test": "Hello"}, "")


# ── Context Servicer tests ──


class TestContextServicer:
    def test_update_triggers_reindex(self):
        """UpdateContextAgentBucket triggers embedding pipeline."""
        import sys

        from grpc_server.servicers.context_servicer import AiContextServicer

        mock_request = MagicMock()
        mock_request.sections_json = '{"intro": "Hello world"}'
        mock_request.free_text = "Extra info"

        mock_reindexer = AsyncMock()
        mock_reindexer.reindex = AsyncMock(return_value={
            "chunk_count": 3,
            "total_tokens": 100,
            "duration_ms": 50,
        })

        mock_bucket = MagicMock()
        mock_bucket.id = "test-bucket-id"

        mock_bucket_model = MagicMock()
        mock_bucket_model.objects.first.return_value = mock_bucket

        mock_context_models = MagicMock()
        mock_context_models.ContextAgentBucket = mock_bucket_model

        with (
            patch("embedding.reindexer.Reindexer", return_value=mock_reindexer),
            patch.dict(sys.modules, {"apps.context.models": mock_context_models}),
        ):
            servicer = AiContextServicer()
            result = servicer.UpdateContextAgentBucket(mock_request, None)

        assert result["chunk_count"] == 3
        assert result["total_tokens"] == 100
        assert result["duration_ms"] == 50

    def test_get_stubs_still_work(self):
        """Non-updated methods still return placeholder responses."""
        import sys

        from grpc_server.servicers.context_servicer import AiContextServicer

        mock_bucket_model = MagicMock()
        mock_bucket_model.objects.first.return_value = None

        mock_context_models = MagicMock()
        mock_context_models.ContextAgentBucket = mock_bucket_model
        mock_context_models.FacilitatorContextBucket = mock_bucket_model

        with patch.dict(sys.modules, {"apps.context.models": mock_context_models}):
            servicer = AiContextServicer()
            result = servicer.GetContextAgentBucket(MagicMock(), None)
        assert "sections_json" in result
        assert result["sections_json"] == "{}"
