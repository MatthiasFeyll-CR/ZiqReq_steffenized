"""Tests for the Context Agent (US-003).

Test IDs: T-2.15.03
Also covers: prompt rendering, retriever integration, mock mode, grounding refusal.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.context_agent.agent import ContextAgent
from agents.context_agent.prompt import build_system_prompt


def _make_chunk(
    chunk_id: str | None = None,
    chunk_text: str = "Sample chunk text",
    source_section: str | None = "onboarding",
    similarity: float = 0.85,
) -> dict:
    return {
        "id": chunk_id or str(uuid.uuid4()),
        "chunk_text": chunk_text,
        "source_section": source_section,
        "similarity": similarity,
    }


# ── System prompt rendering ──


class TestSystemPrompt:
    def test_prompt_includes_query(self):
        """System prompt renders the user query."""
        prompt = build_system_prompt(
            query="What is the onboarding process?",
            chunks=[],
        )
        assert "What is the onboarding process?" in prompt

    def test_prompt_includes_chunks(self):
        """System prompt renders retrieved chunks."""
        chunks = [
            _make_chunk(chunk_text="New employees start with orientation."),
            _make_chunk(
                chunk_text="IT setup takes 24-48 hours.",
                source_section="it_setup",
            ),
        ]
        prompt = build_system_prompt(query="test", chunks=chunks)
        assert "New employees start with orientation." in prompt
        assert "IT setup takes 24-48 hours." in prompt
        assert 'source_section="onboarding"' in prompt
        assert 'source_section="it_setup"' in prompt

    def test_prompt_no_chunks(self):
        """System prompt handles no chunks case."""
        prompt = build_system_prompt(query="test", chunks=[])
        assert "(no relevant chunks retrieved)" in prompt

    def test_prompt_includes_grounding_rules(self):
        """System prompt includes grounding rules."""
        prompt = build_system_prompt(query="test", chunks=[])
        assert "grounding_rules" in prompt
        assert "NEVER fabricate" in prompt
        assert "citation_rules" in prompt

    def test_prompt_chunk_shows_similarity(self):
        """Chunks in prompt show relevance score."""
        chunk = _make_chunk(similarity=0.92)
        prompt = build_system_prompt(query="test", chunks=[chunk])
        assert 'relevance="0.92"' in prompt


# ── T-2.15.03: Context Agent grounded in retrieved chunks ──


class TestContextAgentGrounding:
    """T-2.15.03: Context Agent response cites chunk content only."""

    @pytest.mark.asyncio
    async def test_no_chunks_returns_refusal(self):
        """Context Agent refuses to answer when no relevant chunks found."""
        mock_retriever = AsyncMock()
        mock_retriever.retrieve = AsyncMock(return_value=[])

        agent = ContextAgent(retriever=mock_retriever)

        # Bypass mock mode — call _execute directly
        result = await agent._execute({
            "query": "What is the company's vacation policy?",
            "project_id": "project-1",
            "query_embedding": [0.1] * 1536,
        })

        assert "don't have enough context" in result["response"]
        assert result["chunks_used"] == []

    @pytest.mark.asyncio
    async def test_no_embedding_returns_refusal(self):
        """Context Agent refuses when no query_embedding provided."""
        mock_retriever = AsyncMock()
        mock_retriever.retrieve = AsyncMock(return_value=[])

        agent = ContextAgent(retriever=mock_retriever)
        result = await agent._execute({
            "query": "What is the company's vacation policy?",
            "project_id": "project-1",
            # No query_embedding
        })

        assert "don't have enough context" in result["response"]
        assert result["chunks_used"] == []
        # Retriever should not be called without embedding
        mock_retriever.retrieve.assert_not_called()

    @pytest.mark.asyncio
    async def test_chunks_passed_to_sk_and_ids_returned(self):
        """Context Agent passes chunks to prompt and returns chunk IDs used."""
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

        chunks = [
            _make_chunk(chunk_id="chunk-1", chunk_text="Onboarding takes 3 days."),
            _make_chunk(chunk_id="chunk-2", chunk_text="IT setup: 24-48 hours."),
        ]
        mock_retriever = AsyncMock()
        mock_retriever.retrieve = AsyncMock(return_value=chunks)

        agent = ContextAgent(retriever=mock_retriever)

        # Mock the SK service call
        mock_message = AsyncMock()
        mock_message.__str__ = lambda self: "Based on the onboarding section, it takes 3 days."

        with (
            patch("agents.context_agent.agent.get_deployment", return_value="test-deploy"),
            patch("agents.context_agent.agent.create_kernel") as mock_kernel_factory,
        ):
            mock_service = AsyncMock(spec=AzureChatCompletion)
            mock_service.get_prompt_execution_settings_class.return_value = _MockSettings
            mock_service.get_chat_message_contents = AsyncMock(return_value=[mock_message])

            mock_kernel = MagicMock()
            mock_kernel.get_service.return_value = mock_service
            mock_kernel_factory.return_value = mock_kernel

            result = await agent._execute({
                "query": "How long is onboarding?",
                "project_id": "project-1",
                "query_embedding": [0.1] * 1536,
            })

        assert result["chunks_used"] == ["chunk-1", "chunk-2"]
        assert result["response"] == "Based on the onboarding section, it takes 3 days."
        mock_retriever.retrieve.assert_called_once_with(
            query_embedding=[0.1] * 1536,
            project_type=None,
        )


# ── Mock mode ──


class TestContextAgentMockMode:
    @pytest.mark.asyncio
    async def test_mock_mode_returns_fixture(self, settings):
        """ContextAgent.process() in mock mode returns fixture data."""
        settings.AI_MOCK_MODE = True
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        agent = ContextAgent()
        result = await agent.process({
            "query": "test question",
            "project_id": "test-project",
        })
        assert "response" in result
        assert "chunks_used" in result
        assert isinstance(result["chunks_used"], list)
        assert len(result["chunks_used"]) == 2


# ── Retriever unit tests ──


class TestRetriever:
    def test_retriever_default_top_k(self):
        """Retriever defaults to top_k=5."""
        from embedding.retriever import Retriever

        r = Retriever()
        assert r.top_k == 5

    def test_retriever_custom_top_k(self):
        """Retriever accepts custom top_k."""
        from embedding.retriever import Retriever

        r = Retriever(top_k=10)
        assert r.top_k == 10

    def test_retriever_default_min_similarity(self):
        """Retriever defaults to min_similarity=0.7."""
        from embedding.retriever import Retriever

        r = Retriever()
        assert r.min_similarity == 0.7

    def test_retriever_custom_min_similarity(self):
        """Retriever accepts custom min_similarity."""
        from embedding.retriever import Retriever

        r = Retriever(min_similarity=0.8)
        assert r.min_similarity == 0.8


class _MockSettings:
    """Minimal mock for prompt execution settings."""

    def __init__(self, service_id: str = "default") -> None:
        self.service_id = service_id
        self.max_tokens = 1000
        self.temperature = 0.7
