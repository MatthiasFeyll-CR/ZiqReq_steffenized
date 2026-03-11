"""Tests for the Keyword Agent (US-009).

Covers: prompt rendering, keyword extraction + parsing, mock mode,
CoreClient persistence, IdeaEmbedder trigger, pipeline integration.

Test IDs: T-5.1.01, T-5.1.02, T-5.1.03 — keyword extraction tests.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.keyword_agent.agent import KeywordAgent
from agents.keyword_agent.prompt import build_system_prompt

# ── System prompt rendering ──


class TestKeywordPrompt:
    def test_prompt_includes_title(self):
        prompt = build_system_prompt(
            title="AI-powered brainstorming tool",
            chat_summary="Discussion about microservices.",
            board_content="",
        )
        assert "AI-powered brainstorming tool" in prompt

    def test_prompt_includes_chat_summary(self):
        prompt = build_system_prompt(
            title="Test",
            chat_summary="Team discussed authentication options.",
            board_content="",
        )
        assert "Team discussed authentication options." in prompt

    def test_prompt_includes_board_content(self):
        prompt = build_system_prompt(
            title="Test",
            chat_summary="",
            board_content="Node: Architecture decisions",
        )
        assert "Node: Architecture decisions" in prompt

    def test_prompt_includes_max_keywords(self):
        prompt = build_system_prompt(
            title="Test", chat_summary="", board_content="", max_keywords=15,
        )
        assert "15" in prompt

    def test_prompt_default_max_keywords(self):
        prompt = build_system_prompt(title="Test", chat_summary="", board_content="")
        assert "20" in prompt

    def test_prompt_empty_chat_summary_placeholder(self):
        prompt = build_system_prompt(title="Test", chat_summary="", board_content="")
        assert "(no chat summary available)" in prompt

    def test_prompt_empty_board_content_placeholder(self):
        prompt = build_system_prompt(title="Test", chat_summary="", board_content="")
        assert "(no board content available)" in prompt

    def test_prompt_identity(self):
        prompt = build_system_prompt(title="Test", chat_summary="", board_content="")
        assert "Keyword Agent" in prompt
        assert "Keyword extraction" in prompt

    def test_prompt_extraction_rules(self):
        prompt = build_system_prompt(title="Test", chat_summary="", board_content="")
        assert "single abstract word" in prompt
        assert "lowercase" in prompt
        assert "alphabetically" in prompt


# ── Keyword parsing ──


class TestKeywordParsing:
    def test_parse_valid_json(self):
        result = KeywordAgent._parse_keywords(
            '["database", "security", "auth"]', 20,
        )
        assert result == ["auth", "database", "security"]

    def test_parse_lowercase_enforcement(self):
        result = KeywordAgent._parse_keywords(
            '["Database", "SECURITY", "Auth"]', 20,
        )
        assert result == ["auth", "database", "security"]

    def test_parse_duplicates_removed(self):
        result = KeywordAgent._parse_keywords(
            '["database", "database", "security"]', 20,
        )
        assert result == ["database", "security"]

    def test_parse_multi_word_filtered(self):
        """T-5.1.03: Keywords are single abstract words."""
        result = KeywordAgent._parse_keywords(
            '["database", "machine learning", "security"]', 20,
        )
        assert result == ["database", "security"]

    def test_parse_max_keywords_cap(self):
        """T-5.1.02: Keywords capped at max_keywords_per_idea."""
        words = [f"word{i:02d}" for i in range(30)]
        raw = "[" + ", ".join(f'"{w}"' for w in words) + "]"
        result = KeywordAgent._parse_keywords(raw, 20)
        assert len(result) <= 20

    def test_parse_invalid_json(self):
        result = KeywordAgent._parse_keywords("not json", 20)
        assert result == []

    def test_parse_non_list_json(self):
        result = KeywordAgent._parse_keywords('{"key": "value"}', 20)
        assert result == []

    def test_parse_non_string_items_filtered(self):
        result = KeywordAgent._parse_keywords('[123, "valid", null]', 20)
        assert result == ["valid"]

    def test_parse_empty_strings_filtered(self):
        result = KeywordAgent._parse_keywords('["", "valid", "  "]', 20)
        assert result == ["valid"]

    def test_parse_sorted_alphabetically(self):
        result = KeywordAgent._parse_keywords(
            '["zebra", "apple", "mango"]', 20,
        )
        assert result == ["apple", "mango", "zebra"]


# ── Agent execution ──


class _MockSettings:
    def __init__(self, service_id: str = "default") -> None:
        self.service_id = service_id
        self.max_tokens = 500
        self.temperature = 0.3


class TestKeywordAgent:
    @pytest.mark.asyncio
    async def test_extracts_keywords_via_sk(self):
        """T-5.1.01: Keyword Agent extracts keywords from chat with clear direction."""
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

        mock_client = MagicMock()
        mock_client.get_admin_parameter.return_value = {
            "key": "max_keywords_per_idea", "value": "20",
        }
        agent = KeywordAgent(core_client=mock_client)

        mock_message = AsyncMock()
        mock_message.__str__ = lambda self: '["architecture", "deployment", "security"]'

        with (
            patch(
                "agents.keyword_agent.agent.get_deployment",
                return_value="default-deploy",
            ),
            patch(
                "agents.keyword_agent.agent.create_kernel"
            ) as mock_kernel_factory,
            patch(
                "embedding.idea_embedder.IdeaEmbedder"
            ) as MockEmbedder,
        ):
            mock_service = AsyncMock(spec=AzureChatCompletion)
            mock_service.get_prompt_execution_settings_class.return_value = (
                _MockSettings
            )
            mock_service.get_chat_message_contents = AsyncMock(
                return_value=[mock_message]
            )

            mock_kernel = MagicMock()
            mock_kernel.get_service.return_value = mock_service
            mock_kernel_factory.return_value = mock_kernel

            mock_embedder_instance = AsyncMock()
            MockEmbedder.return_value = mock_embedder_instance

            result = await agent._execute({
                "idea_id": "idea-1",
                "title": "AI Brainstorming Tool",
                "chat_summary": "Discussion about architecture.",
                "board_content": "Security module",
            })

        assert result["keywords"] == ["architecture", "deployment", "security"]
        mock_client.upsert_keywords.assert_called_once_with(
            idea_id="idea-1",
            keywords=["architecture", "deployment", "security"],
        )
        mock_embedder_instance.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_uses_default_model_tier(self):
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

        mock_client = MagicMock()
        mock_client.get_admin_parameter.return_value = {"key": "max_keywords_per_idea", "value": ""}
        agent = KeywordAgent(core_client=mock_client)

        mock_message = AsyncMock()
        mock_message.__str__ = lambda self: '["test"]'

        with (
            patch(
                "agents.keyword_agent.agent.get_deployment",
                return_value="default-deploy",
            ) as mock_deploy,
            patch(
                "agents.keyword_agent.agent.create_kernel"
            ) as mock_kernel_factory,
            patch("embedding.idea_embedder.IdeaEmbedder"),
        ):
            mock_service = AsyncMock(spec=AzureChatCompletion)
            mock_service.get_prompt_execution_settings_class.return_value = _MockSettings
            mock_service.get_chat_message_contents = AsyncMock(
                return_value=[mock_message]
            )

            mock_kernel = MagicMock()
            mock_kernel.get_service.return_value = mock_service
            mock_kernel_factory.return_value = mock_kernel

            await agent._execute({
                "idea_id": "idea-1",
                "title": "Test",
                "chat_summary": "",
                "board_content": "",
            })

        mock_deploy.assert_called_once_with("default")

    @pytest.mark.asyncio
    async def test_grpc_persist_failure_handled(self):
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

        mock_client = MagicMock()
        mock_client.get_admin_parameter.return_value = {"key": "max_keywords_per_idea", "value": ""}
        mock_client.upsert_keywords.side_effect = Exception("gRPC down")
        agent = KeywordAgent(core_client=mock_client)

        mock_message = AsyncMock()
        mock_message.__str__ = lambda self: '["test"]'

        with (
            patch(
                "agents.keyword_agent.agent.get_deployment",
                return_value="default-deploy",
            ),
            patch(
                "agents.keyword_agent.agent.create_kernel"
            ) as mock_kernel_factory,
            patch("embedding.idea_embedder.IdeaEmbedder"),
        ):
            mock_service = AsyncMock(spec=AzureChatCompletion)
            mock_service.get_prompt_execution_settings_class.return_value = _MockSettings
            mock_service.get_chat_message_contents = AsyncMock(
                return_value=[mock_message]
            )

            mock_kernel = MagicMock()
            mock_kernel.get_service.return_value = mock_service
            mock_kernel_factory.return_value = mock_kernel

            # Should not raise
            result = await agent._execute({
                "idea_id": "idea-1",
                "title": "Test",
                "chat_summary": "",
                "board_content": "",
            })

        assert result["keywords"] == ["test"]

    @pytest.mark.asyncio
    async def test_idea_embedder_failure_handled(self):
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

        mock_client = MagicMock()
        mock_client.get_admin_parameter.return_value = {"key": "max_keywords_per_idea", "value": ""}
        agent = KeywordAgent(core_client=mock_client)

        mock_message = AsyncMock()
        mock_message.__str__ = lambda self: '["test"]'

        with (
            patch(
                "agents.keyword_agent.agent.get_deployment",
                return_value="default-deploy",
            ),
            patch(
                "agents.keyword_agent.agent.create_kernel"
            ) as mock_kernel_factory,
            patch(
                "embedding.idea_embedder.IdeaEmbedder"
            ) as MockEmbedder,
        ):
            mock_service = AsyncMock(spec=AzureChatCompletion)
            mock_service.get_prompt_execution_settings_class.return_value = _MockSettings
            mock_service.get_chat_message_contents = AsyncMock(
                return_value=[mock_message]
            )

            mock_kernel = MagicMock()
            mock_kernel.get_service.return_value = mock_service
            mock_kernel_factory.return_value = mock_kernel

            mock_embedder_instance = AsyncMock()
            mock_embedder_instance.generate.side_effect = Exception("Embedding failed")
            MockEmbedder.return_value = mock_embedder_instance

            # Should not raise
            result = await agent._execute({
                "idea_id": "idea-1",
                "title": "Test",
                "chat_summary": "",
                "board_content": "",
            })

        assert result["keywords"] == ["test"]

    @pytest.mark.asyncio
    async def test_reads_max_keywords_admin_param(self):
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

        mock_client = MagicMock()
        mock_client.get_admin_parameter.return_value = {
            "key": "max_keywords_per_idea", "value": "10",
        }
        agent = KeywordAgent(core_client=mock_client)

        # Return 15 keywords, but max is 10
        words = [f"word{i:02d}" for i in range(15)]
        raw = "[" + ", ".join(f'"{w}"' for w in words) + "]"

        mock_message = AsyncMock()
        mock_message.__str__ = lambda self: raw

        with (
            patch(
                "agents.keyword_agent.agent.get_deployment",
                return_value="default-deploy",
            ),
            patch(
                "agents.keyword_agent.agent.create_kernel"
            ) as mock_kernel_factory,
            patch("embedding.idea_embedder.IdeaEmbedder"),
        ):
            mock_service = AsyncMock(spec=AzureChatCompletion)
            mock_service.get_prompt_execution_settings_class.return_value = _MockSettings
            mock_service.get_chat_message_contents = AsyncMock(
                return_value=[mock_message]
            )

            mock_kernel = MagicMock()
            mock_kernel.get_service.return_value = mock_service
            mock_kernel_factory.return_value = mock_kernel

            result = await agent._execute({
                "idea_id": "idea-1",
                "title": "Test",
                "chat_summary": "",
                "board_content": "",
            })

        assert len(result["keywords"]) <= 10


# ── Mock mode ──


class TestKeywordAgentMockMode:
    @pytest.mark.asyncio
    async def test_mock_mode_returns_fixture(self, settings):
        settings.AI_MOCK_MODE = True
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        agent = KeywordAgent()
        result = await agent.process({
            "idea_id": "test-idea",
            "title": "Test Idea",
            "chat_summary": "",
            "board_content": "",
        })
        assert "keywords" in result
        assert isinstance(result["keywords"], list)
        assert len(result["keywords"]) > 0
        # All keywords should be strings
        assert all(isinstance(k, str) for k in result["keywords"])


# ── Pipeline integration ──


class TestPipelineKeywordExtraction:
    @pytest.fixture(autouse=True)
    def _clear_events(self):
        from events.publishers import clear_published_events
        clear_published_events()
        yield
        clear_published_events()

    @pytest.fixture(autouse=True)
    def _clear_pipeline_state(self):
        from processing.pipeline import ChatProcessingPipeline
        ChatProcessingPipeline._versions.clear()
        ChatProcessingPipeline._abort_flags.clear()
        yield
        ChatProcessingPipeline._versions.clear()
        ChatProcessingPipeline._abort_flags.clear()

    @pytest.mark.asyncio
    async def test_keyword_extraction_invoked_in_pipeline(self, settings):
        """Keyword Agent is invoked in Step 6 of pipeline."""
        settings.AI_MOCK_MODE = False
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        from processing.pipeline import ChatProcessingPipeline

        core_client = MagicMock()
        core_client.get_idea_context.return_value = {
            "idea": {"title": "Test Idea", "state": "brainstorming",
                     "agent_mode": "interactive", "title_manually_edited": False},
            "recent_messages": [
                {"id": "msg-1", "content": "Short message", "sender_type": "user"},
            ],
            "board_state": {"nodes": [], "connections": []},
            "chat_summary": None,
            "facilitator_bucket_content": "",
        }
        core_client.get_admin_parameter.return_value = {"key": "context_compression_threshold", "value": "60"}

        pipeline = ChatProcessingPipeline(core_client=core_client)

        keyword_called = False

        async def mock_keyword_process(input_data):
            nonlocal keyword_called
            keyword_called = True
            return {"keywords": ["brainstorming", "test"]}

        async def mock_facilitator_process(input_data):
            return {
                "delegations": [],
                "board_instructions": [],
                "response": "Done.",
                "token_usage": {"input": 100, "output": 20},
            }

        with (
            patch("agents.facilitator.agent.FacilitatorAgent") as MockFacilitator,
            patch("agents.keyword_agent.agent.KeywordAgent") as MockKeyword,
        ):
            MockFacilitator.return_value.process = mock_facilitator_process
            MockKeyword.return_value.process = mock_keyword_process
            result = await pipeline.execute("idea-1")

        assert result["status"] == "completed"
        assert keyword_called is True

    @pytest.mark.asyncio
    async def test_keyword_extraction_skipped_in_mock_mode(self, settings):
        """Keyword extraction is skipped in mock mode."""
        settings.AI_MOCK_MODE = True
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        from processing.pipeline import ChatProcessingPipeline

        core_client = MagicMock()
        core_client.get_idea_context.return_value = {
            "idea": {"title": "Test", "state": "brainstorming",
                     "agent_mode": "interactive", "title_manually_edited": False},
            "recent_messages": [],
            "board_state": {"nodes": [], "connections": []},
            "chat_summary": None,
            "facilitator_bucket_content": "",
        }

        pipeline = ChatProcessingPipeline(core_client=core_client)

        async def mock_facilitator_process(input_data):
            return {
                "delegations": [],
                "board_instructions": [],
                "response": "Done.",
                "token_usage": {"input": 100, "output": 20},
            }

        with patch("agents.facilitator.agent.FacilitatorAgent") as MockFacilitator:
            MockFacilitator.return_value.process = mock_facilitator_process
            result = await pipeline.execute("idea-1")

        assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_keyword_extraction_failure_does_not_block_pipeline(self, settings):
        """Keyword extraction failure does not block pipeline completion."""
        settings.AI_MOCK_MODE = False
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        from processing.pipeline import ChatProcessingPipeline

        core_client = MagicMock()
        core_client.get_idea_context.return_value = {
            "idea": {"title": "Test", "state": "brainstorming",
                     "agent_mode": "interactive", "title_manually_edited": False},
            "recent_messages": [
                {"id": "msg-1", "content": "Short", "sender_type": "user"},
            ],
            "board_state": {"nodes": [], "connections": []},
            "chat_summary": None,
            "facilitator_bucket_content": "",
        }
        core_client.get_admin_parameter.return_value = {"key": "context_compression_threshold", "value": "60"}

        pipeline = ChatProcessingPipeline(core_client=core_client)

        async def mock_keyword_process(input_data):
            raise Exception("Keyword Agent crashed")

        async def mock_facilitator_process(input_data):
            return {
                "delegations": [],
                "board_instructions": [],
                "response": "Done.",
                "token_usage": {"input": 100, "output": 20},
            }

        with (
            patch("agents.facilitator.agent.FacilitatorAgent") as MockFacilitator,
            patch("agents.keyword_agent.agent.KeywordAgent") as MockKeyword,
        ):
            MockFacilitator.return_value.process = mock_facilitator_process
            MockKeyword.return_value.process = mock_keyword_process
            result = await pipeline.execute("idea-1")

        # Pipeline should still complete despite keyword extraction failure
        assert result["status"] == "completed"
