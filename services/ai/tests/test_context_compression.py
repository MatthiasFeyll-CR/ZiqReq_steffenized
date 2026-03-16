"""Tests for the Context Compression Agent (US-008).

Covers: prompt rendering, incremental compression, mock mode,
empty messages handling, CoreClient persistence, pipeline compression trigger.

Test ID: T-2.14.03 — Compression triggers at threshold.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.context_compression.agent import ContextCompressionAgent
from agents.context_compression.prompt import build_system_prompt


def _make_message(
    msg_id: str = "msg-001",
    sender_type: str = "user",
    sender_id: str = "user-1",
    ai_agent: str = "",
    content: str = "Let's discuss the project timeline.",
    created_at: str = "2026-03-10T14:32:00Z",
) -> dict:
    return {
        "id": msg_id,
        "sender_type": sender_type,
        "sender_id": sender_id,
        "ai_agent": ai_agent,
        "content": content,
        "created_at": created_at,
    }


# ── System prompt rendering ──


class TestSystemPrompt:
    def test_prompt_includes_messages(self):
        """System prompt renders messages to compress."""
        messages = [
            _make_message(content="We should use microservices."),
            _make_message(content="Agreed, with gRPC."),
        ]
        prompt = build_system_prompt(messages)
        assert "We should use microservices." in prompt
        assert "Agreed, with gRPC." in prompt

    def test_prompt_includes_previous_summary(self):
        """System prompt includes previous summary when provided."""
        prompt = build_system_prompt(
            [_make_message()],
            previous_summary="The team decided on PostgreSQL.",
        )
        assert "The team decided on PostgreSQL." in prompt
        assert "previous_summary" in prompt

    def test_prompt_no_previous_summary(self):
        """System prompt indicates first compression when no previous summary."""
        prompt = build_system_prompt([_make_message()])
        assert "first compression" in prompt

    def test_prompt_no_messages(self):
        """System prompt handles empty messages list."""
        prompt = build_system_prompt([])
        assert "(no messages to compress)" in prompt

    def test_prompt_includes_compression_rules(self):
        """System prompt includes compression rules."""
        prompt = build_system_prompt([_make_message()])
        assert "compression_rules" in prompt
        assert "NEVER fabricate" in prompt
        assert "key decisions" in prompt

    def test_prompt_identity(self):
        """System prompt includes agent identity."""
        prompt = build_system_prompt([_make_message()])
        assert "Context Compression Agent" in prompt
        assert "Incremental summarization" in prompt

    def test_prompt_message_shows_sender(self):
        """Messages show sender information."""
        msg = _make_message(sender_type="user", sender_id="alice")
        prompt = build_system_prompt([msg])
        assert 'sender="alice"' in prompt

    def test_prompt_ai_message_shows_agent_name(self):
        """AI messages show agent name as sender."""
        msg = _make_message(
            sender_type="ai", ai_agent="facilitator", sender_id=""
        )
        prompt = build_system_prompt([msg])
        assert 'sender="facilitator"' in prompt


# ── Agent execution ──


class _MockSettings:
    """Minimal mock for prompt execution settings."""

    def __init__(self, service_id: str = "default") -> None:
        self.service_id = service_id
        self.max_tokens = 2000
        self.temperature = 0.3


class TestContextCompressionAgent:
    @pytest.mark.asyncio
    async def test_empty_messages_returns_existing_summary(self):
        """Agent returns existing summary when no messages to compress."""
        mock_client = MagicMock()
        agent = ContextCompressionAgent(core_client=mock_client)

        result = await agent._execute({
            "project_id": "project-1",
            "messages_to_compress": [],
            "previous_summary": "Previous decisions made.",
            "compression_iteration": 2,
            "context_window_usage": 50.0,
        })

        assert result["summary_text"] == "Previous decisions made."
        assert result["compression_iteration"] == 2
        assert result["context_window_usage"] == 50.0

    @pytest.mark.asyncio
    async def test_compression_invokes_sk_and_persists(self):
        """Agent compresses messages via SK and persists to CoreClient."""
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

        messages = [
            _make_message(msg_id="msg-1", content="Use JWT."),
            _make_message(msg_id="msg-2", content="Agreed."),
        ]
        mock_client = MagicMock()
        agent = ContextCompressionAgent(core_client=mock_client)

        mock_message = AsyncMock()
        mock_message.__str__ = lambda self: "Team decided to use JWT authentication."

        with (
            patch(
                "agents.context_compression.agent.get_deployment",
                return_value="default-deploy",
            ),
            patch(
                "agents.context_compression.agent.create_kernel"
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
                "project_id": "project-1",
                "messages_to_compress": messages,
                "previous_summary": None,
                "compression_iteration": 0,
                "context_window_usage": 65.0,
            })

        assert result["summary_text"] == "Team decided to use JWT authentication."
        assert result["compression_iteration"] == 1
        assert result["context_window_usage"] == 65.0

        # Verify persistence
        mock_client.upsert_context_summary.assert_called_once_with(
            project_id="project-1",
            summary_text="Team decided to use JWT authentication.",
            messages_covered_up_to_id="msg-2",
            compression_iteration=1,
            context_window_usage=65.0,
        )

    @pytest.mark.asyncio
    async def test_uses_default_model_tier(self):
        """Agent uses default deployment tier."""
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

        messages = [_make_message()]
        mock_client = MagicMock()
        agent = ContextCompressionAgent(core_client=mock_client)

        mock_message = AsyncMock()
        mock_message.__str__ = lambda self: "summary"

        with (
            patch(
                "agents.context_compression.agent.get_deployment",
                return_value="default-deploy",
            ) as mock_deploy,
            patch(
                "agents.context_compression.agent.create_kernel"
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

            await agent._execute({
                "project_id": "project-1",
                "messages_to_compress": messages,
                "previous_summary": None,
            })

        mock_deploy.assert_called_once_with("default")

    @pytest.mark.asyncio
    async def test_incremental_compression(self):
        """Agent builds on previous summary (incremental)."""
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

        messages = [_make_message(msg_id="msg-5", content="New topic: deploy.")]
        mock_client = MagicMock()
        agent = ContextCompressionAgent(core_client=mock_client)

        mock_message = AsyncMock()
        mock_message.__str__ = lambda self: "Previous + deployment discussion."

        with (
            patch(
                "agents.context_compression.agent.get_deployment",
                return_value="default-deploy",
            ),
            patch(
                "agents.context_compression.agent.create_kernel"
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
                "project_id": "project-1",
                "messages_to_compress": messages,
                "previous_summary": "Team decided on JWT.",
                "compression_iteration": 1,
                "context_window_usage": 70.0,
            })

        assert result["compression_iteration"] == 2
        assert result["summary_text"] == "Previous + deployment discussion."

        # Verify upsert called with incremented iteration
        mock_client.upsert_context_summary.assert_called_once()
        call_kwargs = mock_client.upsert_context_summary.call_args
        assert call_kwargs.kwargs["compression_iteration"] == 2

    @pytest.mark.asyncio
    async def test_grpc_persist_failure_handled(self):
        """Agent handles CoreClient upsert failure gracefully."""
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

        messages = [_make_message(msg_id="msg-1")]
        mock_client = MagicMock()
        mock_client.upsert_context_summary.side_effect = Exception("gRPC down")
        agent = ContextCompressionAgent(core_client=mock_client)

        mock_message = AsyncMock()
        mock_message.__str__ = lambda self: "summary"

        with (
            patch(
                "agents.context_compression.agent.get_deployment",
                return_value="default-deploy",
            ),
            patch(
                "agents.context_compression.agent.create_kernel"
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

            # Should not raise — handles gracefully
            result = await agent._execute({
                "project_id": "project-1",
                "messages_to_compress": messages,
                "previous_summary": None,
            })

        assert result["summary_text"] == "summary"


# ── Mock mode ──


class TestContextCompressionMockMode:
    @pytest.mark.asyncio
    async def test_mock_mode_returns_fixture(self, settings):
        """ContextCompressionAgent.process() in mock mode returns fixture data."""
        settings.AI_MOCK_MODE = True
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        agent = ContextCompressionAgent()
        result = await agent.process({
            "project_id": "test-project",
            "messages_to_compress": [],
            "previous_summary": None,
        })
        assert "summary_text" in result
        assert "compression_iteration" in result
        assert result["compression_iteration"] == 1
        assert isinstance(result["summary_text"], str)
        assert len(result["summary_text"]) > 0


# ── Pipeline compression trigger (T-2.14.03) ──


class TestPipelineCompressionTrigger:
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
    async def test_compression_triggered_above_threshold(self, settings):
        """T-2.14.03: Compression agent invoked when context utilization > 60%."""
        settings.AI_MOCK_MODE = False
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        from processing.pipeline import ChatProcessingPipeline

        # Create messages with enough content to exceed 60% of 128k tokens
        # 128000 tokens * 60% = 76800 tokens * 4 chars/token = 307200 chars
        big_content = "x" * 320000  # Slightly over 60%
        core_client = MagicMock()
        core_client.get_project_context.return_value = {
            "project": {"title": "Test", "state": "brainstorming",
                     "agent_mode": "interactive", "title_manually_edited": False},
            "recent_messages": [
                {"id": "msg-1", "content": big_content, "sender_type": "user"},
            ],
            "chat_summary": None,
            "facilitator_bucket_content": "",
        }
        core_client.get_admin_parameter.return_value = {"key": "context_compression_threshold", "value": "60"}

        pipeline = ChatProcessingPipeline(core_client=core_client)

        compression_called = False

        async def mock_compression_process(input_data):
            nonlocal compression_called
            compression_called = True
            return {
                "summary_text": "Compressed summary.",
                "compression_iteration": 1,
                "context_window_usage": 65.0,
            }

        async def mock_facilitator_process(input_data):
            return {
                "delegations": [],

                "response": "Done.",
                "token_usage": {"input": 100, "output": 20},
            }

        with (
            patch("agents.facilitator.agent.FacilitatorAgent") as MockFacilitator,
            patch("agents.context_compression.agent.ContextCompressionAgent") as MockCompression,
        ):
            MockFacilitator.return_value.process = mock_facilitator_process
            MockCompression.return_value.process = mock_compression_process
            result = await pipeline.execute("project-1")

        assert result["status"] == "completed"
        assert compression_called is True

    @pytest.mark.asyncio
    async def test_compression_not_triggered_below_threshold(self, settings):
        """Compression not triggered when utilization is below threshold."""
        settings.AI_MOCK_MODE = False
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        from processing.pipeline import ChatProcessingPipeline

        # Small content — well below threshold
        core_client = MagicMock()
        core_client.get_project_context.return_value = {
            "project": {"title": "Test", "state": "brainstorming",
                     "agent_mode": "interactive", "title_manually_edited": False},
            "recent_messages": [
                {"id": "msg-1", "content": "Short message", "sender_type": "user"},
            ],
            "chat_summary": None,
            "facilitator_bucket_content": "",
        }
        core_client.get_admin_parameter.return_value = {"key": "context_compression_threshold", "value": "60"}

        pipeline = ChatProcessingPipeline(core_client=core_client)

        compression_called = False

        async def mock_compression_process(input_data):
            nonlocal compression_called
            compression_called = True
            return {"summary_text": "Summary.", "compression_iteration": 1, "context_window_usage": 5.0}

        async def mock_facilitator_process(input_data):
            return {
                "delegations": [],

                "response": "Done.",
                "token_usage": {"input": 100, "output": 20},
            }

        with (
            patch("agents.facilitator.agent.FacilitatorAgent") as MockFacilitator,
            patch("agents.context_compression.agent.ContextCompressionAgent") as MockCompression,
        ):
            MockFacilitator.return_value.process = mock_facilitator_process
            MockCompression.return_value.process = mock_compression_process
            result = await pipeline.execute("project-1")

        assert result["status"] == "completed"
        assert compression_called is False

    @pytest.mark.asyncio
    async def test_compression_skipped_in_mock_mode(self, settings):
        """Compression check is skipped in mock mode."""
        settings.AI_MOCK_MODE = True
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        from processing.pipeline import ChatProcessingPipeline

        core_client = MagicMock()
        core_client.get_project_context.return_value = {
            "project": {"title": "Test", "state": "brainstorming",
                     "agent_mode": "interactive", "title_manually_edited": False},
            "recent_messages": [],
            "chat_summary": None,
            "facilitator_bucket_content": "",
        }

        pipeline = ChatProcessingPipeline(core_client=core_client)

        async def mock_facilitator_process(input_data):
            return {
                "delegations": [],

                "response": "Done.",
                "token_usage": {"input": 100, "output": 20},
            }

        with patch("agents.facilitator.agent.FacilitatorAgent") as MockFacilitator:
            MockFacilitator.return_value.process = mock_facilitator_process
            result = await pipeline.execute("project-1")

        assert result["status"] == "completed"
        # get_admin_parameter should NOT be called for compression in mock mode
        for call in core_client.get_admin_parameter.call_args_list:
            assert call.args[0] != "context_compression_threshold"

    @pytest.mark.asyncio
    async def test_compression_with_existing_summary(self, settings):
        """Compression passes previous summary to agent for incremental compression."""
        settings.AI_MOCK_MODE = False
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        from processing.pipeline import ChatProcessingPipeline

        big_content = "x" * 320000
        core_client = MagicMock()
        core_client.get_project_context.return_value = {
            "project": {"title": "Test", "state": "brainstorming",
                     "agent_mode": "interactive", "title_manually_edited": False},
            "recent_messages": [
                {"id": "msg-5", "content": big_content, "sender_type": "user"},
            ],
            "chat_summary": {
                "summary_text": "Previous decisions about auth.",
                "compression_iteration": 2,
            },
            "facilitator_bucket_content": "",
        }
        core_client.get_admin_parameter.return_value = {"key": "context_compression_threshold", "value": "60"}

        pipeline = ChatProcessingPipeline(core_client=core_client)

        compression_input = {}

        async def mock_compression_process(input_data):
            nonlocal compression_input
            compression_input = input_data
            return {
                "summary_text": "Updated summary.",
                "compression_iteration": 3,
                "context_window_usage": 70.0,
            }

        async def mock_facilitator_process(input_data):
            return {
                "delegations": [],

                "response": "Done.",
                "token_usage": {"input": 100, "output": 20},
            }

        with (
            patch("agents.facilitator.agent.FacilitatorAgent") as MockFacilitator,
            patch("agents.context_compression.agent.ContextCompressionAgent") as MockCompression,
        ):
            MockFacilitator.return_value.process = mock_facilitator_process
            MockCompression.return_value.process = mock_compression_process
            await pipeline.execute("project-1")

        assert compression_input["previous_summary"] == "Previous decisions about auth."
        assert compression_input["compression_iteration"] == 2
