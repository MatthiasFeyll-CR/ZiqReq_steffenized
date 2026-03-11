"""Tests for the Merge Synthesizer Agent (US-009).

Test IDs: T-5.5.05
Covers: structured output validation, Pydantic enforcement with retry,
prompt rendering, consumer integration, event publishing.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.merge_synthesizer.agent import MergeSynthesizerAgent, MergeSynthesizerOutput
from agents.merge_synthesizer.prompt import build_system_prompt

# ── Pydantic output model ──


class TestMergeSynthesizerOutput:
    def test_valid_output(self):
        """T-5.5.05: Merge Synthesizer returns {synthesis_message, board_instructions}."""
        output = MergeSynthesizerOutput(
            synthesis_message="A" * 100,
            board_instructions=[
                {"intent": "add_topic", "description": "Add combined topic"},
            ],
        )
        assert len(output.synthesis_message) == 100
        assert len(output.board_instructions) == 1

    def test_synthesis_message_too_short_rejected(self):
        with pytest.raises(Exception):
            MergeSynthesizerOutput(
                synthesis_message="Too short",
                board_instructions=[],
            )

    def test_empty_board_instructions_valid(self):
        output = MergeSynthesizerOutput(
            synthesis_message="A" * 100,
            board_instructions=[],
        )
        assert output.board_instructions == []

    def test_multiple_board_instructions(self):
        output = MergeSynthesizerOutput(
            synthesis_message="A" * 150,
            board_instructions=[
                {"intent": "add_topic", "description": "First topic"},
                {"intent": "add_topic", "description": "Second topic"},
                {"intent": "reorganize", "description": "Group related items"},
            ],
        )
        assert len(output.board_instructions) == 3

    def test_board_instruction_with_full_fields(self):
        output = MergeSynthesizerOutput(
            synthesis_message="A" * 100,
            board_instructions=[
                {
                    "intent": "add_topic",
                    "description": "Add workflow topic",
                    "suggested_title": "Workflow",
                    "suggested_content": ["Step 1", "Step 2"],
                    "related_to": ["Analytics"],
                    "suggested_group": "Core",
                },
            ],
        )
        instr = output.board_instructions[0]
        assert instr["intent"] == "add_topic"
        assert instr["suggested_title"] == "Workflow"


# ── Prompt rendering ──


class TestMergeSynthesizerPrompt:
    def test_includes_idea_a_title(self):
        prompt = build_system_prompt(
            idea_a_owner_name="Alice",
            idea_a_title="Workflow Automation",
            idea_a_summary="Automating processes.",
            idea_a_board_nodes=[],
            idea_b_owner_name="Bob",
            idea_b_title="Other Idea",
            idea_b_summary="",
            idea_b_board_nodes=[],
        )
        assert "Workflow Automation" in prompt

    def test_includes_idea_b_title(self):
        prompt = build_system_prompt(
            idea_a_owner_name="Alice",
            idea_a_title="Idea A",
            idea_a_summary="",
            idea_a_board_nodes=[],
            idea_b_owner_name="Bob",
            idea_b_title="Data Analytics Platform",
            idea_b_summary="Analytics discussion.",
            idea_b_board_nodes=[],
        )
        assert "Data Analytics Platform" in prompt

    def test_includes_owner_names(self):
        prompt = build_system_prompt(
            idea_a_owner_name="Lisa",
            idea_a_title="Test A",
            idea_a_summary="",
            idea_a_board_nodes=[],
            idea_b_owner_name="Thomas",
            idea_b_title="Test B",
            idea_b_summary="",
            idea_b_board_nodes=[],
        )
        assert "Lisa" in prompt
        assert "Thomas" in prompt

    def test_empty_summaries_show_placeholder(self):
        prompt = build_system_prompt(
            idea_a_owner_name="A",
            idea_a_title="Test A",
            idea_a_summary="",
            idea_a_board_nodes=[],
            idea_b_owner_name="B",
            idea_b_title="Test B",
            idea_b_summary="",
            idea_b_board_nodes=[],
        )
        assert "(no chat summary available)" in prompt

    def test_includes_board_nodes(self):
        prompt = build_system_prompt(
            idea_a_owner_name="A",
            idea_a_title="Test A",
            idea_a_summary="",
            idea_a_board_nodes=[
                {"type": "box", "title": "Revenue Model", "body": "SaaS pricing"},
            ],
            idea_b_owner_name="B",
            idea_b_title="Test B",
            idea_b_summary="",
            idea_b_board_nodes=[],
        )
        assert "Revenue Model" in prompt
        assert "SaaS pricing" in prompt

    def test_identity(self):
        prompt = build_system_prompt(
            idea_a_owner_name="A",
            idea_a_title="Test",
            idea_a_summary="",
            idea_a_board_nodes=[],
            idea_b_owner_name="B",
            idea_b_title="Test B",
            idea_b_summary="",
            idea_b_board_nodes=[],
        )
        assert "Merge Synthesizer" in prompt

    def test_output_format_instructions(self):
        prompt = build_system_prompt(
            idea_a_owner_name="A",
            idea_a_title="Test",
            idea_a_summary="",
            idea_a_board_nodes=[],
            idea_b_owner_name="B",
            idea_b_title="Test B",
            idea_b_summary="",
            idea_b_board_nodes=[],
        )
        assert "synthesis_message" in prompt
        assert "board_instructions" in prompt
        assert "intent" in prompt


# ── Output validation ──


class TestOutputValidation:
    def test_valid_json_parsed(self):
        """T-5.5.05: Structured output validation."""
        raw = json.dumps({
            "synthesis_message": "A" * 150,
            "board_instructions": [
                {"intent": "add_topic", "description": "Add combined topic"},
            ],
        })
        result = MergeSynthesizerAgent._validate_output(raw)
        assert result is not None
        assert len(result.synthesis_message) == 150
        assert len(result.board_instructions) == 1

    def test_invalid_json_returns_none(self):
        result = MergeSynthesizerAgent._validate_output("not valid json")
        assert result is None

    def test_short_synthesis_message_returns_none(self):
        raw = json.dumps({
            "synthesis_message": "Too short",
            "board_instructions": [],
        })
        result = MergeSynthesizerAgent._validate_output(raw)
        assert result is None

    def test_missing_field_returns_none(self):
        raw = json.dumps({"synthesis_message": "A" * 100})
        result = MergeSynthesizerAgent._validate_output(raw)
        assert result is None


# ── Agent execution ──


class _MockSettings:
    def __init__(self, service_id: str = "default") -> None:
        self.service_id = service_id
        self.max_tokens = 2000
        self.temperature = 0.4


class TestMergeSynthesizerAgent:
    @pytest.mark.asyncio
    async def test_returns_structured_output(self):
        """T-5.5.05: Merge Synthesizer produces synthesis + board instructions."""
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

        agent = MergeSynthesizerAgent()

        valid_response = json.dumps({
            "synthesis_message": "# Merged Idea\n\nThis combines two brainstorming sessions. " * 5,
            "board_instructions": [
                {
                    "intent": "add_topic",
                    "description": "Combined workflow topic",
                    "suggested_title": "Workflow Automation",
                    "suggested_content": ["Task routing", "Process orchestration"],
                },
            ],
        })

        mock_message = AsyncMock()
        mock_message.__str__ = lambda self: valid_response

        with (
            patch(
                "agents.merge_synthesizer.agent.get_deployment",
                return_value="default-deploy",
            ),
            patch(
                "agents.merge_synthesizer.agent.create_kernel"
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
                "idea_a_owner_name": "Alice",
                "idea_a_title": "Workflow Automation",
                "idea_a_summary": "Automating processes.",
                "idea_a_board_nodes": [],
                "idea_b_owner_name": "Bob",
                "idea_b_title": "Data Analytics",
                "idea_b_summary": "Analytics platform.",
                "idea_b_board_nodes": [],
            })

        assert "synthesis_message" in result
        assert "board_instructions" in result
        assert isinstance(result["board_instructions"], list)
        assert len(result["board_instructions"]) > 0

    @pytest.mark.asyncio
    async def test_retries_on_malformed_output(self):
        """Pydantic validation retry on malformed output."""
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

        agent = MergeSynthesizerAgent()

        malformed_response = "This is not valid JSON"
        synth_msg = "# Merged\n\nCombined brainstorming from both ideas. " * 3
        valid_response = json.dumps({
            "synthesis_message": synth_msg,
            "board_instructions": [
                {"intent": "add_topic", "description": "Combined topic"},
            ],
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
                "agents.merge_synthesizer.agent.get_deployment",
                return_value="default-deploy",
            ),
            patch(
                "agents.merge_synthesizer.agent.create_kernel"
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
                "idea_a_owner_name": "Alice",
                "idea_a_title": "Test A",
                "idea_a_summary": "",
                "idea_a_board_nodes": [],
                "idea_b_owner_name": "Bob",
                "idea_b_title": "Test B",
                "idea_b_summary": "",
                "idea_b_board_nodes": [],
            })

        assert call_count == 2
        assert "synthesis_message" in result
        assert len(result["synthesis_message"]) >= 100

    @pytest.mark.asyncio
    async def test_both_attempts_fail_returns_empty(self):
        """When both parse attempts fail, returns empty synthesis."""
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

        agent = MergeSynthesizerAgent()

        mock_bad = AsyncMock()
        mock_bad.__str__ = lambda self: "still not json"

        with (
            patch(
                "agents.merge_synthesizer.agent.get_deployment",
                return_value="default-deploy",
            ),
            patch(
                "agents.merge_synthesizer.agent.create_kernel"
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
                "idea_a_owner_name": "Alice",
                "idea_a_title": "Test",
                "idea_a_summary": "",
                "idea_a_board_nodes": [],
                "idea_b_owner_name": "Bob",
                "idea_b_title": "Test B",
                "idea_b_summary": "",
                "idea_b_board_nodes": [],
            })

        assert result["synthesis_message"] == ""
        assert result["board_instructions"] == []

    @pytest.mark.asyncio
    async def test_uses_default_model_tier(self):
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

        agent = MergeSynthesizerAgent()

        valid = json.dumps({
            "synthesis_message": "A" * 100,
            "board_instructions": [],
        })
        mock_msg = AsyncMock()
        mock_msg.__str__ = lambda self: valid

        with (
            patch(
                "agents.merge_synthesizer.agent.get_deployment",
                return_value="default-deploy",
            ) as mock_deploy,
            patch(
                "agents.merge_synthesizer.agent.create_kernel"
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
                "idea_a_owner_name": "A",
                "idea_a_title": "Test",
                "idea_a_summary": "",
                "idea_a_board_nodes": [],
                "idea_b_owner_name": "B",
                "idea_b_title": "Test B",
                "idea_b_summary": "",
                "idea_b_board_nodes": [],
            })

        mock_deploy.assert_called_once_with("default")


# ── Mock mode ──


class TestMergeSynthesizerMockMode:
    @pytest.mark.asyncio
    async def test_mock_mode_returns_fixture(self, settings):
        settings.AI_MOCK_MODE = True
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        agent = MergeSynthesizerAgent()
        result = await agent.process({
            "idea_a_owner_name": "Alice",
            "idea_a_title": "Test A",
            "idea_a_summary": "",
            "idea_a_board_nodes": [],
            "idea_b_owner_name": "Bob",
            "idea_b_title": "Test B",
            "idea_b_summary": "",
            "idea_b_board_nodes": [],
        })
        assert "synthesis_message" in result
        assert "board_instructions" in result
        assert isinstance(result["board_instructions"], list)


# ── Consumer integration ──


class TestMergeConsumer:
    @pytest.fixture(autouse=True)
    def _clear_events(self):
        from events.publishers import clear_published_events
        clear_published_events()
        yield
        clear_published_events()

    @pytest.mark.asyncio
    async def test_successful_synthesis_publishes_event(self):
        """When agent produces valid synthesis, publishes merge_synthesizer.complete."""
        from agents.merge_synthesizer.consumer import handle_merge_request_accepted
        from events.publishers import get_published_events

        mock_core_client = MagicMock()
        mock_core_client.get_idea_context.side_effect = [
            {
                "idea": {"title": "Workflow Automation", "owner_name": "Alice", "keywords": ["workflow"]},
                "chat_summary": "Automating processes.",
                "board_state": {"nodes": [{"type": "box", "title": "Process", "body": "Steps"}]},
            },
            {
                "idea": {"title": "Data Analytics", "owner_name": "Bob", "keywords": ["analytics"]},
                "chat_summary": "Analytics platform.",
                "board_state": {"nodes": [{"type": "box", "title": "Dashboard", "body": "Metrics"}]},
            },
        ]

        agent_result = {
            "synthesis_message": "# Merged Idea\n\n" + "Combined brainstorming. " * 10,
            "board_instructions": [
                {"intent": "add_topic", "description": "Combined topic"},
            ],
        }

        with (
            patch("agents.merge_synthesizer.consumer.CoreClient", return_value=mock_core_client),
            patch("agents.merge_synthesizer.consumer.MergeSynthesizerAgent") as MockAgent,
        ):
            mock_agent_instance = AsyncMock()
            mock_agent_instance.process.return_value = agent_result
            MockAgent.return_value = mock_agent_instance

            result = await handle_merge_request_accepted({
                "merge_request_id": "mr-001",
                "requesting_idea_id": "idea-a",
                "target_idea_id": "idea-b",
            })

        assert result["published"] is True
        events = get_published_events()
        assert len(events) == 1
        assert events[0]["event_type"] == "merge_synthesizer.complete"
        assert events[0]["merge_request_id"] == "mr-001"
        assert events[0]["requesting_idea_id"] == "idea-a"
        assert events[0]["target_idea_id"] == "idea-b"
        assert "synthesis_message" in events[0]
        assert "board_instructions" in events[0]

    @pytest.mark.asyncio
    async def test_empty_synthesis_no_event(self):
        """When agent returns empty output, no event is published."""
        from agents.merge_synthesizer.consumer import handle_merge_request_accepted
        from events.publishers import get_published_events

        mock_core_client = MagicMock()
        mock_core_client.get_idea_context.side_effect = [
            {
                "idea": {"title": "A", "owner_name": "Alice", "keywords": []},
                "chat_summary": "",
                "board_state": {"nodes": []},
            },
            {
                "idea": {"title": "B", "owner_name": "Bob", "keywords": []},
                "chat_summary": "",
                "board_state": {"nodes": []},
            },
        ]

        with (
            patch("agents.merge_synthesizer.consumer.CoreClient", return_value=mock_core_client),
            patch("agents.merge_synthesizer.consumer.MergeSynthesizerAgent") as MockAgent,
        ):
            mock_agent_instance = AsyncMock()
            mock_agent_instance.process.return_value = {
                "synthesis_message": "",
                "board_instructions": [],
            }
            MockAgent.return_value = mock_agent_instance

            result = await handle_merge_request_accepted({
                "merge_request_id": "mr-002",
                "requesting_idea_id": "idea-a",
                "target_idea_id": "idea-b",
            })

        assert result["published"] is False
        events = get_published_events()
        assert len(events) == 0

    @pytest.mark.asyncio
    async def test_event_includes_synthesis_payload(self):
        """Published event includes full synthesis_message and board_instructions."""
        from agents.merge_synthesizer.consumer import handle_merge_request_accepted
        from events.publishers import get_published_events

        mock_core_client = MagicMock()
        mock_core_client.get_idea_context.side_effect = [
            {
                "idea": {"title": "Idea A", "owner_name": "Alice", "keywords": []},
                "chat_summary": "Summary A",
                "board_state": {"nodes": []},
            },
            {
                "idea": {"title": "Idea B", "owner_name": "Bob", "keywords": []},
                "chat_summary": "Summary B",
                "board_state": {"nodes": []},
            },
        ]

        synthesis_msg = "# Merged\n\n" + "Detailed synthesis content. " * 10
        instructions = [
            {"intent": "add_topic", "description": "Topic A", "suggested_title": "Combined A"},
            {"intent": "add_topic", "description": "Topic B", "suggested_title": "Combined B"},
        ]

        with (
            patch("agents.merge_synthesizer.consumer.CoreClient", return_value=mock_core_client),
            patch("agents.merge_synthesizer.consumer.MergeSynthesizerAgent") as MockAgent,
        ):
            mock_agent_instance = AsyncMock()
            mock_agent_instance.process.return_value = {
                "synthesis_message": synthesis_msg,
                "board_instructions": instructions,
            }
            MockAgent.return_value = mock_agent_instance

            await handle_merge_request_accepted({
                "merge_request_id": "mr-003",
                "requesting_idea_id": "idea-a",
                "target_idea_id": "idea-b",
            })

        events = get_published_events()
        assert events[0]["synthesis_message"] == synthesis_msg
        assert events[0]["board_instructions"] == instructions
        assert len(events[0]["board_instructions"]) == 2
