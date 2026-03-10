"""Tests for the ChatProcessingPipeline (US-003).

Test ID: T-2.10.03 — Abort and restart.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from events.publishers import clear_published_events, get_published_events
from processing.pipeline import ChatProcessingPipeline, PipelineAborted


@pytest.fixture(autouse=True)
def _clear_events():
    """Clear published events before each test."""
    clear_published_events()
    yield
    clear_published_events()


@pytest.fixture()
def _clear_pipeline_state():
    """Clear class-level pipeline state between tests."""
    ChatProcessingPipeline._versions.clear()
    ChatProcessingPipeline._abort_flags.clear()
    yield
    ChatProcessingPipeline._versions.clear()
    ChatProcessingPipeline._abort_flags.clear()


def _mock_core_client(idea_context: dict | None = None) -> MagicMock:
    """Create a mock CoreClient with sensible defaults."""
    client = MagicMock()
    client.get_idea_context.return_value = idea_context or {
        "idea": {
            "title": "Test Idea",
            "state": "brainstorming",
            "agent_mode": "interactive",
            "title_manually_edited": False,
        },
        "recent_messages": [
            {
                "id": "msg-1",
                "content": "Let's brainstorm about invoices",
                "sender_type": "user",
                "sender_name": "Lisa",
                "has_ai_reaction": False,
            },
        ],
        "board_state": {"nodes": [], "connections": []},
        "chat_summary": None,
        "facilitator_bucket_content": "",
    }
    return client


# ── Basic pipeline execution ──


class TestPipelineExecution:
    @pytest.mark.asyncio
    async def test_full_pipeline_completes(self, _clear_pipeline_state, settings):
        """Pipeline runs all 7 steps and publishes ai.processing.complete."""
        settings.AI_MOCK_MODE = True
        from pathlib import Path
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        core_client = _mock_core_client()
        pipeline = ChatProcessingPipeline(core_client=core_client)

        result = await pipeline.execute("idea-1")

        assert result["status"] == "completed"
        assert result["processing_id"] is not None

        # Step 1: gRPC was called
        core_client.get_idea_context.assert_called_once_with("idea-1")

        # Step 6: completion event published
        events = get_published_events()
        complete_events = [e for e in events if e["event_type"] == "ai.processing.complete"]
        assert len(complete_events) == 1
        assert complete_events[0]["idea_id"] == "idea-1"
        assert complete_events[0]["counter_reset"] is True

    @pytest.mark.asyncio
    async def test_pipeline_increments_version(self, _clear_pipeline_state, settings):
        """Each pipeline.execute() increments the processing version."""
        settings.AI_MOCK_MODE = True
        from pathlib import Path
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        core_client = _mock_core_client()
        pipeline = ChatProcessingPipeline(core_client=core_client)

        assert pipeline.get_version("idea-1") == 0
        await pipeline.execute("idea-1")
        assert pipeline.get_version("idea-1") == 1
        await pipeline.execute("idea-1")
        assert pipeline.get_version("idea-1") == 2


# ── T-2.10.03: Abort and restart ──


class TestPipelineAbort:
    @pytest.mark.asyncio
    async def test_abort_flag_causes_early_exit(self, _clear_pipeline_state, settings):
        """T-2.10.03: Setting abort flag mid-processing causes pipeline to exit early."""
        settings.AI_MOCK_MODE = True
        from pathlib import Path
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        core_client = _mock_core_client()
        pipeline = ChatProcessingPipeline(core_client=core_client)

        # Pre-set abort flag before execution
        ChatProcessingPipeline._versions["idea-1"] = 0
        # The pipeline will call _start_processing which sets version to 1,
        # then we need to set abort before step boundary.
        # We'll intercept via a side effect on get_idea_context.

        def set_abort_on_load(*args, **kwargs):
            pipeline.set_abort("idea-1")
            return _mock_core_client().get_idea_context.return_value

        core_client.get_idea_context.side_effect = set_abort_on_load

        result = await pipeline.execute("idea-1")

        assert result["status"] == "aborted"
        assert result["result"] is None

        # No completion event should be published
        events = get_published_events()
        complete_events = [e for e in events if e["event_type"] == "ai.processing.complete"]
        assert len(complete_events) == 0

    @pytest.mark.asyncio
    async def test_version_mismatch_aborts(self, _clear_pipeline_state, settings):
        """Version mismatch (new pipeline started) causes abort."""
        settings.AI_MOCK_MODE = True
        from pathlib import Path
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        core_client = _mock_core_client()
        pipeline = ChatProcessingPipeline(core_client=core_client)

        # Simulate version bump during step 1 (new message triggers new pipeline)
        def bump_version_on_load(*args, **kwargs):
            ChatProcessingPipeline._versions["idea-1"] = 999
            return _mock_core_client().get_idea_context.return_value

        core_client.get_idea_context.side_effect = bump_version_on_load

        result = await pipeline.execute("idea-1")

        assert result["status"] == "aborted"

    @pytest.mark.asyncio
    async def test_abort_then_restart_succeeds(self, _clear_pipeline_state, settings):
        """T-2.10.03: After abort, a new pipeline execution succeeds."""
        settings.AI_MOCK_MODE = True
        from pathlib import Path
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        core_client = _mock_core_client()
        pipeline = ChatProcessingPipeline(core_client=core_client)

        # First run: abort via flag
        call_count = 0
        def abort_first_time(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                pipeline.set_abort("idea-1")
            return _mock_core_client().get_idea_context.return_value

        core_client.get_idea_context.side_effect = abort_first_time

        result1 = await pipeline.execute("idea-1")
        assert result1["status"] == "aborted"

        # Second run: should succeed (abort flag cleared by _start_processing)
        result2 = await pipeline.execute("idea-1")
        assert result2["status"] == "completed"

        # Completion event from second run
        events = get_published_events()
        complete_events = [e for e in events if e["event_type"] == "ai.processing.complete"]
        assert len(complete_events) == 1


# ── Version tracking ──


class TestVersionTracking:
    def test_get_version_default_zero(self, _clear_pipeline_state):
        pipeline = ChatProcessingPipeline()
        assert pipeline.get_version("nonexistent") == 0

    def test_set_abort_flag(self, _clear_pipeline_state):
        pipeline = ChatProcessingPipeline()
        pipeline.set_abort("idea-1")
        assert ChatProcessingPipeline._abort_flags["idea-1"] is True

    def test_check_abort_raises_on_flag(self, _clear_pipeline_state):
        pipeline = ChatProcessingPipeline()
        ChatProcessingPipeline._versions["idea-1"] = 1
        ChatProcessingPipeline._abort_flags["idea-1"] = True
        with pytest.raises(PipelineAborted, match="Abort flag"):
            pipeline._check_abort("idea-1", expected_version=1, step=3)

    def test_check_abort_raises_on_version_mismatch(self, _clear_pipeline_state):
        pipeline = ChatProcessingPipeline()
        ChatProcessingPipeline._versions["idea-1"] = 5
        ChatProcessingPipeline._abort_flags["idea-1"] = False
        with pytest.raises(PipelineAborted, match="Version mismatch"):
            pipeline._check_abort("idea-1", expected_version=3, step=2)


# ── Delegation stub (M7) ──


class TestDelegationStub:
    @pytest.mark.asyncio
    async def test_delegation_reinvokes_facilitator(self, _clear_pipeline_state, settings):
        """When Facilitator requests delegation, pipeline re-invokes with stub results."""
        settings.AI_MOCK_MODE = True
        from pathlib import Path
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        core_client = _mock_core_client()
        pipeline = ChatProcessingPipeline(core_client=core_client)

        # Mock the facilitator to return delegations on first call, none on second
        call_count = 0
        async def mock_process(input_data):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {
                    "delegations": [{"delegation_type": "context_agent", "query": "test"}],
                    "board_instructions": [],
                    "response": "Let me check...",
                    "token_usage": {"input": 100, "output": 20},
                }
            return {
                "delegations": [],
                "board_instructions": [],
                "response": "Here's what I found.",
                "token_usage": {"input": 150, "output": 30},
            }

        with patch("agents.facilitator.agent.FacilitatorAgent") as MockAgent:
            instance = MockAgent.return_value
            instance.process = mock_process
            result = await pipeline.execute("idea-1")

        assert result["status"] == "completed"
        assert call_count == 2  # Facilitator invoked twice


# ── Board Agent stub (M7) ──


class TestBoardAgentStub:
    @pytest.mark.asyncio
    async def test_board_changes_logged_not_executed(self, _clear_pipeline_state, settings):
        """Board Agent stub logs instructions but does not execute them."""
        settings.AI_MOCK_MODE = True
        from pathlib import Path
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        core_client = _mock_core_client()
        pipeline = ChatProcessingPipeline(core_client=core_client)

        async def mock_process(input_data):
            return {
                "delegations": [],
                "board_instructions": [{"intent": "add_topic", "description": "Test"}],
                "response": "I'll add that to the board.",
                "token_usage": {"input": 100, "output": 20},
            }

        with patch("agents.facilitator.agent.FacilitatorAgent") as MockAgent:
            instance = MockAgent.return_value
            instance.process = mock_process
            result = await pipeline.execute("idea-1")

        assert result["status"] == "completed"


# ── Context Assembler ──


class TestContextAssembler:
    def test_assemble_basic_context(self):
        from processing.context_assembler import ContextAssembler

        assembler = ContextAssembler()
        response = {
            "idea": {
                "title": "Invoice Automation",
                "state": "brainstorming",
                "agent_mode": "interactive",
                "title_manually_edited": False,
            },
            "recent_messages": [
                {"id": "msg-1", "content": "Hello", "sender_type": "user"},
            ],
            "board_state": {"nodes": [], "connections": []},
            "chat_summary": "Previous discussion about workflows.",
            "facilitator_bucket_content": "SAP, DocuSign",
        }

        result = assembler.assemble("idea-123", response)

        assert result["idea_id"] == "idea-123"
        assert result["idea_context"]["title"] == "Invoice Automation"
        assert result["idea_context"]["agent_mode"] == "interactive"
        assert len(result["recent_messages"]) == 1
        assert result["chat_summary"] == "Previous discussion about workflows."
        assert result["facilitator_bucket_content"] == "SAP, DocuSign"
        assert result["delegation_results"] is None
        assert result["extension_results"] is None

    def test_assemble_empty_response(self):
        from processing.context_assembler import ContextAssembler

        assembler = ContextAssembler()
        result = assembler.assemble("idea-empty", {})

        assert result["idea_id"] == "idea-empty"
        assert result["idea_context"]["title"] == ""
        assert result["idea_context"]["agent_mode"] == "interactive"
        assert result["recent_messages"] == []
        assert result["chat_summary"] is None
