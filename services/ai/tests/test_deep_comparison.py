"""Tests for the Deep Comparison Agent (US-003).

Test IDs: T-5.3.01, T-5.3.02
Covers: structured output validation, Pydantic enforcement with retry,
prompt rendering, consumer integration, event publishing.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.deep_comparison.agent import DeepComparisonAgent, DeepComparisonOutput
from agents.deep_comparison.prompt import build_system_prompt

# ── Pydantic output model ──


class TestDeepComparisonOutput:
    def test_valid_output(self):
        """T-5.3.01: Deep Comparison returns structured output."""
        output = DeepComparisonOutput(
            is_similar=True,
            confidence=0.85,
            explanation="Both ideas address the same problem of automated testing.",
            overlap_areas=["testing", "automation"],
        )
        assert output.is_similar is True
        assert output.confidence == 0.85
        assert len(output.overlap_areas) == 2

    def test_confidence_range_low(self):
        output = DeepComparisonOutput(
            is_similar=False,
            confidence=0.0,
            explanation="No overlap between the ideas at all.",
            overlap_areas=[],
        )
        assert output.confidence == 0.0

    def test_confidence_range_high(self):
        output = DeepComparisonOutput(
            is_similar=True,
            confidence=1.0,
            explanation="These ideas are identical in scope and approach.",
            overlap_areas=["everything"],
        )
        assert output.confidence == 1.0

    def test_confidence_below_zero_rejected(self):
        with pytest.raises(Exception):
            DeepComparisonOutput(
                is_similar=False,
                confidence=-0.1,
                explanation="Invalid confidence value test.",
                overlap_areas=[],
            )

    def test_confidence_above_one_rejected(self):
        with pytest.raises(Exception):
            DeepComparisonOutput(
                is_similar=True,
                confidence=1.1,
                explanation="Invalid confidence value test.",
                overlap_areas=[],
            )

    def test_explanation_too_short_rejected(self):
        with pytest.raises(Exception):
            DeepComparisonOutput(
                is_similar=False,
                confidence=0.5,
                explanation="Short",
                overlap_areas=[],
            )

    def test_empty_overlap_areas_valid(self):
        output = DeepComparisonOutput(
            is_similar=False,
            confidence=0.2,
            explanation="The ideas address completely different domains.",
            overlap_areas=[],
        )
        assert output.overlap_areas == []


# ── Prompt rendering ──


class TestDeepComparisonPrompt:
    def test_includes_idea_a_title(self):
        prompt = build_system_prompt(
            idea_a_title="AI Brainstorming",
            idea_a_keywords=["ai", "brainstorming"],
            idea_a_chat_summary="Discussion about AI.",
            idea_a_board_summary="",
            idea_b_title="Other Idea",
            idea_b_keywords=[],
            idea_b_chat_summary="",
            idea_b_board_summary="",
        )
        assert "AI Brainstorming" in prompt

    def test_includes_idea_b_title(self):
        prompt = build_system_prompt(
            idea_a_title="Idea A",
            idea_a_keywords=[],
            idea_a_chat_summary="",
            idea_a_board_summary="",
            idea_b_title="Machine Learning Pipeline",
            idea_b_keywords=["ml", "pipeline"],
            idea_b_chat_summary="",
            idea_b_board_summary="",
        )
        assert "Machine Learning Pipeline" in prompt

    def test_includes_keywords(self):
        prompt = build_system_prompt(
            idea_a_title="Test",
            idea_a_keywords=["security", "authentication"],
            idea_a_chat_summary="",
            idea_a_board_summary="",
            idea_b_title="Test B",
            idea_b_keywords=["encryption"],
            idea_b_chat_summary="",
            idea_b_board_summary="",
        )
        assert "security, authentication" in prompt
        assert "encryption" in prompt

    def test_empty_summaries_show_placeholder(self):
        prompt = build_system_prompt(
            idea_a_title="Test",
            idea_a_keywords=[],
            idea_a_chat_summary="",
            idea_a_board_summary="",
            idea_b_title="Test B",
            idea_b_keywords=[],
            idea_b_chat_summary="",
            idea_b_board_summary="",
        )
        assert "(no chat summary available)" in prompt
        assert "(no board summary available)" in prompt

    def test_identity(self):
        prompt = build_system_prompt(
            idea_a_title="Test",
            idea_a_keywords=[],
            idea_a_chat_summary="",
            idea_a_board_summary="",
            idea_b_title="Test B",
            idea_b_keywords=[],
            idea_b_chat_summary="",
            idea_b_board_summary="",
        )
        assert "Deep Comparison Agent" in prompt

    def test_output_format_instructions(self):
        prompt = build_system_prompt(
            idea_a_title="Test",
            idea_a_keywords=[],
            idea_a_chat_summary="",
            idea_a_board_summary="",
            idea_b_title="Test B",
            idea_b_keywords=[],
            idea_b_chat_summary="",
            idea_b_board_summary="",
        )
        assert "is_similar" in prompt
        assert "confidence" in prompt
        assert "explanation" in prompt
        assert "overlap_areas" in prompt


# ── Output validation ──


class TestOutputValidation:
    def test_valid_json_parsed(self):
        """T-5.3.01: Structured output validation."""
        raw = json.dumps({
            "is_similar": True,
            "confidence": 0.8,
            "explanation": "Both ideas propose similar solutions for team collaboration.",
            "overlap_areas": ["collaboration", "team management"],
        })
        result = DeepComparisonAgent._validate_output(raw)
        assert result is not None
        assert result.is_similar is True
        assert result.confidence == 0.8

    def test_invalid_json_returns_none(self):
        result = DeepComparisonAgent._validate_output("not valid json")
        assert result is None

    def test_missing_field_returns_none(self):
        raw = json.dumps({"is_similar": True, "confidence": 0.8})
        result = DeepComparisonAgent._validate_output(raw)
        assert result is None

    def test_invalid_confidence_returns_none(self):
        raw = json.dumps({
            "is_similar": True,
            "confidence": 5.0,
            "explanation": "Invalid confidence value.",
            "overlap_areas": [],
        })
        result = DeepComparisonAgent._validate_output(raw)
        assert result is None

    def test_short_explanation_returns_none(self):
        raw = json.dumps({
            "is_similar": True,
            "confidence": 0.8,
            "explanation": "Short",
            "overlap_areas": [],
        })
        result = DeepComparisonAgent._validate_output(raw)
        assert result is None


# ── Agent execution ──


class _MockSettings:
    def __init__(self, service_id: str = "default") -> None:
        self.service_id = service_id
        self.max_tokens = 800
        self.temperature = 0.3


class TestDeepComparisonAgent:
    @pytest.mark.asyncio
    async def test_returns_structured_output(self):
        """T-5.3.01: Deep Comparison returns structured JSON."""
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

        agent = DeepComparisonAgent()

        valid_response = json.dumps({
            "is_similar": True,
            "confidence": 0.85,
            "explanation": "Both ideas address automated code review with AI-driven analysis.",
            "overlap_areas": ["code review", "AI automation"],
        })

        mock_message = AsyncMock()
        mock_message.__str__ = lambda self: valid_response

        with (
            patch(
                "agents.deep_comparison.agent.get_deployment",
                return_value="default-deploy",
            ),
            patch(
                "agents.deep_comparison.agent.create_kernel"
            ) as mock_kernel_factory,
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

            result = await agent._execute({
                "idea_a_title": "Code Review Bot",
                "idea_a_keywords": ["code", "review", "automation"],
                "idea_a_chat_summary": "Discussing automated code review.",
                "idea_a_board_summary": "Architecture for review bot",
                "idea_b_title": "AI Code Analyzer",
                "idea_b_keywords": ["code", "analysis", "ai"],
                "idea_b_chat_summary": "AI-driven code analysis discussion.",
                "idea_b_board_summary": "ML model for code quality",
            })

        assert result["is_similar"] is True
        assert result["confidence"] == 0.85
        assert isinstance(result["explanation"], str)
        assert isinstance(result["overlap_areas"], list)

    @pytest.mark.asyncio
    async def test_retries_on_malformed_output(self):
        """T-5.3.02: Pydantic validation retry on malformed output."""
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

        agent = DeepComparisonAgent()

        malformed_response = "This is not valid JSON"
        valid_response = json.dumps({
            "is_similar": False,
            "confidence": 0.3,
            "explanation": "These ideas address completely different domains and problems.",
            "overlap_areas": [],
        })

        mock_malformed = AsyncMock()
        mock_malformed.__str__ = lambda self: malformed_response

        mock_valid = AsyncMock()
        mock_valid.__str__ = lambda self: valid_response

        call_count = 0

        async def mock_get_chat_messages(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return [mock_malformed]
            return [mock_valid]

        with (
            patch(
                "agents.deep_comparison.agent.get_deployment",
                return_value="default-deploy",
            ),
            patch(
                "agents.deep_comparison.agent.create_kernel"
            ) as mock_kernel_factory,
        ):
            mock_service = AsyncMock(spec=AzureChatCompletion)
            mock_service.get_prompt_execution_settings_class.return_value = (
                _MockSettings
            )
            mock_service.get_chat_message_contents = mock_get_chat_messages

            mock_kernel = MagicMock()
            mock_kernel.get_service.return_value = mock_service
            mock_kernel_factory.return_value = mock_kernel

            result = await agent._execute({
                "idea_a_title": "Test A",
                "idea_a_keywords": [],
                "idea_a_chat_summary": "",
                "idea_a_board_summary": "",
                "idea_b_title": "Test B",
                "idea_b_keywords": [],
                "idea_b_chat_summary": "",
                "idea_b_board_summary": "",
            })

        # Should have retried (2 calls total)
        assert call_count == 2
        assert result["is_similar"] is False
        assert result["confidence"] == 0.3

    @pytest.mark.asyncio
    async def test_both_attempts_fail_returns_not_similar(self):
        """When both parse attempts fail, returns a safe default."""
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

        agent = DeepComparisonAgent()

        mock_bad = AsyncMock()
        mock_bad.__str__ = lambda self: "still not json"

        with (
            patch(
                "agents.deep_comparison.agent.get_deployment",
                return_value="default-deploy",
            ),
            patch(
                "agents.deep_comparison.agent.create_kernel"
            ) as mock_kernel_factory,
        ):
            mock_service = AsyncMock(spec=AzureChatCompletion)
            mock_service.get_prompt_execution_settings_class.return_value = (
                _MockSettings
            )
            mock_service.get_chat_message_contents = AsyncMock(
                return_value=[mock_bad]
            )

            mock_kernel = MagicMock()
            mock_kernel.get_service.return_value = mock_service
            mock_kernel_factory.return_value = mock_kernel

            result = await agent._execute({
                "idea_a_title": "Test",
                "idea_a_keywords": [],
                "idea_a_chat_summary": "",
                "idea_a_board_summary": "",
                "idea_b_title": "Test B",
                "idea_b_keywords": [],
                "idea_b_chat_summary": "",
                "idea_b_board_summary": "",
            })

        assert result["is_similar"] is False
        assert result["confidence"] == 0.0

    @pytest.mark.asyncio
    async def test_uses_default_model_tier(self):
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

        agent = DeepComparisonAgent()

        valid = json.dumps({
            "is_similar": False,
            "confidence": 0.2,
            "explanation": "Different domains entirely.",
            "overlap_areas": [],
        })
        mock_msg = AsyncMock()
        mock_msg.__str__ = lambda self: valid

        with (
            patch(
                "agents.deep_comparison.agent.get_deployment",
                return_value="default-deploy",
            ) as mock_deploy,
            patch(
                "agents.deep_comparison.agent.create_kernel"
            ) as mock_kernel_factory,
        ):
            mock_service = AsyncMock(spec=AzureChatCompletion)
            mock_service.get_prompt_execution_settings_class.return_value = (
                _MockSettings
            )
            mock_service.get_chat_message_contents = AsyncMock(
                return_value=[mock_msg]
            )

            mock_kernel = MagicMock()
            mock_kernel.get_service.return_value = mock_service
            mock_kernel_factory.return_value = mock_kernel

            await agent._execute({
                "idea_a_title": "Test",
                "idea_a_keywords": [],
                "idea_a_chat_summary": "",
                "idea_a_board_summary": "",
                "idea_b_title": "Test B",
                "idea_b_keywords": [],
                "idea_b_chat_summary": "",
                "idea_b_board_summary": "",
            })

        mock_deploy.assert_called_once_with("default")


# ── Mock mode ──


class TestDeepComparisonMockMode:
    @pytest.mark.asyncio
    async def test_mock_mode_returns_fixture(self, settings):
        settings.AI_MOCK_MODE = True
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        agent = DeepComparisonAgent()
        result = await agent.process({
            "idea_a_title": "Test A",
            "idea_a_keywords": [],
            "idea_a_chat_summary": "",
            "idea_a_board_summary": "",
            "idea_b_title": "Test B",
            "idea_b_keywords": [],
            "idea_b_chat_summary": "",
            "idea_b_board_summary": "",
        })
        assert "is_similar" in result
        assert "confidence" in result
        assert "explanation" in result
        assert "overlap_areas" in result


# ── Consumer integration ──


class TestSimilarityConsumer:
    @pytest.fixture(autouse=True)
    def _clear_events(self):
        from events.publishers import clear_published_events
        clear_published_events()
        yield
        clear_published_events()

    @pytest.mark.asyncio
    async def test_confirmed_similarity_publishes_event(self):
        """When agent confirms similarity with high confidence, publishes event."""
        from agents.deep_comparison.consumer import handle_similarity_detected
        from events.publishers import get_published_events

        mock_core_client = MagicMock()
        mock_core_client.get_idea_context.side_effect = [
            {
                "idea": {"title": "Code Review Bot", "state": "open", "keywords": ["code"]},
                "chat_summary": "Discussing code review.",
                "board_state": {"nodes": []},
            },
            {
                "idea": {"title": "AI Analyzer", "state": "open", "keywords": ["code"]},
                "chat_summary": "AI analysis discussion.",
                "board_state": {"nodes": []},
            },
        ]

        agent_result = {
            "is_similar": True,
            "confidence": 0.85,
            "explanation": "Both ideas address automated code review with AI.",
            "overlap_areas": ["code review"],
        }

        with (
            patch("agents.deep_comparison.consumer.CoreClient", return_value=mock_core_client),
            patch("agents.deep_comparison.consumer.DeepComparisonAgent") as MockAgent,
        ):
            mock_agent_instance = AsyncMock()
            mock_agent_instance.process.return_value = agent_result
            MockAgent.return_value = mock_agent_instance

            result = await handle_similarity_detected({
                "requesting_idea_id": "idea-a",
                "target_idea_id": "idea-b",
                "keyword_overlap_count": 8,
            })

        assert result["confirmed"] is True
        events = get_published_events()
        assert len(events) == 1
        assert events[0]["event_type"] == "ai.similarity.confirmed"
        assert events[0]["requesting_idea_id"] == "idea-a"
        assert events[0]["target_idea_id"] == "idea-b"
        assert events[0]["confidence"] == 0.85

    @pytest.mark.asyncio
    async def test_dismissed_similarity_no_event(self):
        """When agent says not similar, no event is published."""
        from agents.deep_comparison.consumer import handle_similarity_detected
        from events.publishers import get_published_events

        mock_core_client = MagicMock()
        mock_core_client.get_idea_context.side_effect = [
            {
                "idea": {"title": "Idea A", "state": "open", "keywords": []},
                "chat_summary": "",
                "board_state": {"nodes": []},
            },
            {
                "idea": {"title": "Idea B", "state": "open", "keywords": []},
                "chat_summary": "",
                "board_state": {"nodes": []},
            },
        ]

        agent_result = {
            "is_similar": False,
            "confidence": 0.2,
            "explanation": "These ideas address completely different domains.",
            "overlap_areas": [],
        }

        with (
            patch("agents.deep_comparison.consumer.CoreClient", return_value=mock_core_client),
            patch("agents.deep_comparison.consumer.DeepComparisonAgent") as MockAgent,
        ):
            mock_agent_instance = AsyncMock()
            mock_agent_instance.process.return_value = agent_result
            MockAgent.return_value = mock_agent_instance

            result = await handle_similarity_detected({
                "requesting_idea_id": "idea-a",
                "target_idea_id": "idea-b",
                "keyword_overlap_count": 7,
            })

        assert result["confirmed"] is False
        events = get_published_events()
        assert len(events) == 0

    @pytest.mark.asyncio
    async def test_low_confidence_no_event(self):
        """Even if is_similar=true, low confidence means no event."""
        from agents.deep_comparison.consumer import handle_similarity_detected
        from events.publishers import get_published_events

        mock_core_client = MagicMock()
        mock_core_client.get_idea_context.side_effect = [
            {
                "idea": {"title": "A", "state": "open", "keywords": []},
                "chat_summary": "",
                "board_state": {"nodes": []},
            },
            {
                "idea": {"title": "B", "state": "open", "keywords": []},
                "chat_summary": "",
                "board_state": {"nodes": []},
            },
        ]

        agent_result = {
            "is_similar": True,
            "confidence": 0.5,
            "explanation": "Some similarity but not enough confidence.",
            "overlap_areas": ["vague overlap"],
        }

        with (
            patch("agents.deep_comparison.consumer.CoreClient", return_value=mock_core_client),
            patch("agents.deep_comparison.consumer.DeepComparisonAgent") as MockAgent,
        ):
            mock_agent_instance = AsyncMock()
            mock_agent_instance.process.return_value = agent_result
            MockAgent.return_value = mock_agent_instance

            result = await handle_similarity_detected({
                "requesting_idea_id": "idea-a",
                "target_idea_id": "idea-b",
                "keyword_overlap_count": 7,
            })

        assert result["confirmed"] is False
        events = get_published_events()
        assert len(events) == 0

    @pytest.mark.asyncio
    async def test_event_includes_idea_states(self):
        """Confirmed event includes both idea states."""
        from agents.deep_comparison.consumer import handle_similarity_detected
        from events.publishers import get_published_events

        mock_core_client = MagicMock()
        mock_core_client.get_idea_context.side_effect = [
            {
                "idea": {"title": "A", "state": "in_review", "keywords": []},
                "chat_summary": "",
                "board_state": {"nodes": []},
            },
            {
                "idea": {"title": "B", "state": "open", "keywords": []},
                "chat_summary": "",
                "board_state": {"nodes": []},
            },
        ]

        with (
            patch("agents.deep_comparison.consumer.CoreClient", return_value=mock_core_client),
            patch("agents.deep_comparison.consumer.DeepComparisonAgent") as MockAgent,
        ):
            mock_agent_instance = AsyncMock()
            mock_agent_instance.process.return_value = {
                "is_similar": True,
                "confidence": 0.9,
                "explanation": "Highly similar ideas addressing same problem.",
                "overlap_areas": ["collaboration"],
            }
            MockAgent.return_value = mock_agent_instance

            await handle_similarity_detected({
                "requesting_idea_id": "idea-a",
                "target_idea_id": "idea-b",
                "keyword_overlap_count": 10,
            })

        events = get_published_events()
        assert events[0]["requesting_idea_state"] == "in_review"
        assert events[0]["target_idea_state"] == "open"
