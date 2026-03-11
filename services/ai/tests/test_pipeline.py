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


# ── Context Agent delegation (M8) ──


class TestContextAgentDelegation:
    @pytest.mark.asyncio
    async def test_delegation_reinvokes_facilitator(self, _clear_pipeline_state, settings):
        """When Facilitator requests context_agent delegation, pipeline re-invokes with results."""
        settings.AI_MOCK_MODE = True
        from pathlib import Path
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        core_client = _mock_core_client()
        pipeline = ChatProcessingPipeline(core_client=core_client)

        call_count = 0
        received_delegation_results = None

        async def mock_process(input_data):
            nonlocal call_count, received_delegation_results
            call_count += 1
            if call_count == 1:
                return {
                    "delegations": [{"delegation_type": "context_agent", "delegation_id": "d1", "query": "test"}],
                    "board_instructions": [],
                    "response": "Let me check...",
                    "token_usage": {"input": 100, "output": 20},
                }
            received_delegation_results = input_data.get("delegation_results")
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
        # In mock mode, delegation results contain mock message
        assert received_delegation_results is not None
        assert "mock mode" in received_delegation_results.lower()

    @pytest.mark.asyncio
    async def test_delegation_publishes_complete_event(self, _clear_pipeline_state, settings):
        """Pipeline publishes ai.delegation.complete after delegation handling."""
        settings.AI_MOCK_MODE = True
        from pathlib import Path
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        core_client = _mock_core_client()
        pipeline = ChatProcessingPipeline(core_client=core_client)

        async def mock_process(input_data):
            if input_data.get("delegation_results") is None:
                return {
                    "delegations": [{"delegation_type": "context_agent", "delegation_id": "d1", "query": "test"}],
                    "board_instructions": [],
                    "response": "Checking...",
                    "token_usage": {"input": 100, "output": 20},
                }
            return {
                "delegations": [],
                "board_instructions": [],
                "response": "Done.",
                "token_usage": {"input": 150, "output": 30},
            }

        with patch("agents.facilitator.agent.FacilitatorAgent") as MockAgent:
            MockAgent.return_value.process = mock_process
            await pipeline.execute("idea-1")

        events = get_published_events()
        delegation_complete = [e for e in events if e["event_type"] == "ai.delegation.complete"]
        assert len(delegation_complete) == 1
        assert delegation_complete[0]["idea_id"] == "idea-1"
        assert delegation_complete[0]["delegation_type"] == "context_agent"

    @pytest.mark.asyncio
    async def test_no_delegation_no_reinvocation(self, _clear_pipeline_state, settings):
        """Pipeline does not re-invoke when no delegations requested."""
        settings.AI_MOCK_MODE = True
        from pathlib import Path
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        core_client = _mock_core_client()
        pipeline = ChatProcessingPipeline(core_client=core_client)

        call_count = 0

        async def mock_process(input_data):
            nonlocal call_count
            call_count += 1
            return {
                "delegations": [],
                "board_instructions": [],
                "response": "No delegation needed.",
                "token_usage": {"input": 100, "output": 20},
            }

        with patch("agents.facilitator.agent.FacilitatorAgent") as MockAgent:
            MockAgent.return_value.process = mock_process
            await pipeline.execute("idea-1")

        assert call_count == 1  # Only one Facilitator invocation

        events = get_published_events()
        delegation_complete = [e for e in events if e["event_type"] == "ai.delegation.complete"]
        assert len(delegation_complete) == 0

    @pytest.mark.asyncio
    async def test_context_agent_invoked_in_non_mock_mode(self, _clear_pipeline_state, settings):
        """In non-mock mode, pipeline invokes Context Agent with query."""
        settings.AI_MOCK_MODE = False
        from pathlib import Path
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        core_client = _mock_core_client()
        pipeline = ChatProcessingPipeline(core_client=core_client)

        context_agent_called = False
        context_agent_input = {}

        async def mock_facilitator_process(input_data):
            if input_data.get("delegation_results") is None:
                return {
                    "delegations": [{"delegation_type": "context_agent", "delegation_id": "d1", "query": "What ERP?"}],
                    "board_instructions": [],
                    "response": "Let me check...",
                    "token_usage": {"input": 100, "output": 20},
                }
            return {
                "delegations": [],
                "board_instructions": [],
                "response": "Based on findings...",
                "token_usage": {"input": 150, "output": 30},
            }

        async def mock_context_process(input_data):
            nonlocal context_agent_called, context_agent_input
            context_agent_called = True
            context_agent_input = input_data
            return {
                "response": "The company uses SAP for ERP.",
                "chunks_used": ["chunk-1", "chunk-2"],
            }

        with patch("agents.facilitator.agent.FacilitatorAgent") as MockFacilitator, \
             patch("agents.context_agent.agent.ContextAgent") as MockContextAgent:
            MockFacilitator.return_value.process = mock_facilitator_process
            MockContextAgent.return_value.process = mock_context_process
            result = await pipeline.execute("idea-1")

        assert result["status"] == "completed"
        assert context_agent_called is True
        assert context_agent_input["query"] == "What ERP?"
        assert context_agent_input["idea_id"] == "idea-1"

    @pytest.mark.asyncio
    async def test_context_agent_results_injected_into_facilitator(self, _clear_pipeline_state, settings):
        """Context Agent response is injected into second Facilitator invocation."""
        settings.AI_MOCK_MODE = False
        from pathlib import Path
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        core_client = _mock_core_client()
        pipeline = ChatProcessingPipeline(core_client=core_client)

        received_delegation_results = None

        async def mock_facilitator_process(input_data):
            nonlocal received_delegation_results
            if input_data.get("delegation_results") is None:
                return {
                    "delegations": [{"delegation_type": "context_agent", "delegation_id": "d1", "query": "What ERP?"}],
                    "board_instructions": [],
                    "response": "Checking...",
                    "token_usage": {"input": 100, "output": 20},
                }
            received_delegation_results = input_data["delegation_results"]
            return {
                "delegations": [],
                "board_instructions": [],
                "response": "SAP is the ERP.",
                "token_usage": {"input": 150, "output": 30},
            }

        async def mock_context_process(input_data):
            return {
                "response": "The company uses SAP for ERP.",
                "chunks_used": ["chunk-1"],
            }

        with patch("agents.facilitator.agent.FacilitatorAgent") as MockFacilitator, \
             patch("agents.context_agent.agent.ContextAgent") as MockContextAgent:
            MockFacilitator.return_value.process = mock_facilitator_process
            MockContextAgent.return_value.process = mock_context_process
            await pipeline.execute("idea-1")

        assert received_delegation_results is not None
        assert "context_agent_findings" in received_delegation_results
        assert "SAP for ERP" in received_delegation_results
        assert "1 knowledge base chunks" in received_delegation_results


# ── Context Extension delegation (M8) ──


class TestContextExtensionDelegation:
    @pytest.mark.asyncio
    async def test_context_extension_delegation_mock_mode(self, _clear_pipeline_state, settings):
        """In mock mode, context_extension delegation returns empty findings."""
        settings.AI_MOCK_MODE = True
        from pathlib import Path
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        core_client = _mock_core_client()
        pipeline = ChatProcessingPipeline(core_client=core_client)

        call_count = 0
        received_extension_results = None

        async def mock_process(input_data):
            nonlocal call_count, received_extension_results
            call_count += 1
            if call_count == 1:
                return {
                    "delegations": [{
                        "delegation_type": "context_extension",
                        "delegation_id": "d1",
                        "query": "What did Lisa say?",
                    }],
                    "board_instructions": [],
                    "response": "Let me check...",
                    "token_usage": {"input": 100, "output": 20},
                }
            received_extension_results = input_data.get("extension_results")
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
        assert call_count == 2
        assert received_extension_results is not None
        assert "mock mode" in received_extension_results.lower()

    @pytest.mark.asyncio
    async def test_context_extension_invoked_in_non_mock_mode(self, _clear_pipeline_state, settings):
        """In non-mock mode, pipeline invokes Context Extension Agent with query."""
        settings.AI_MOCK_MODE = False
        from pathlib import Path
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        core_client = _mock_core_client()
        pipeline = ChatProcessingPipeline(core_client=core_client)

        extension_agent_called = False
        extension_agent_input = {}

        async def mock_facilitator_process(input_data):
            if input_data.get("extension_results") is None:
                return {
                    "delegations": [{
                        "delegation_type": "context_extension",
                        "delegation_id": "d1",
                        "query": "What did Lisa say about signatures?",
                    }],
                    "board_instructions": [],
                    "response": "Let me check the history...",
                    "token_usage": {"input": 100, "output": 20},
                }
            return {
                "delegations": [],
                "board_instructions": [],
                "response": "Lisa mentioned digital signatures in message 3.",
                "token_usage": {"input": 150, "output": 30},
            }

        async def mock_extension_process(input_data):
            nonlocal extension_agent_called, extension_agent_input
            extension_agent_called = True
            extension_agent_input = input_data
            return {
                "response": "Lisa discussed digital signatures for contract approval.",
                "messages_cited": ["msg-5", "msg-12"],
            }

        with patch("agents.facilitator.agent.FacilitatorAgent") as MockFacilitator, \
             patch("agents.context_extension.agent.ContextExtensionAgent") as MockExtension:
            MockFacilitator.return_value.process = mock_facilitator_process
            MockExtension.return_value.process = mock_extension_process
            result = await pipeline.execute("idea-1")

        assert result["status"] == "completed"
        assert extension_agent_called is True
        assert extension_agent_input["query"] == "What did Lisa say about signatures?"
        assert extension_agent_input["idea_id"] == "idea-1"

    @pytest.mark.asyncio
    async def test_context_extension_results_injected_into_facilitator(self, _clear_pipeline_state, settings):
        """Context Extension response is injected into second Facilitator invocation."""
        settings.AI_MOCK_MODE = False
        from pathlib import Path
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        core_client = _mock_core_client()
        pipeline = ChatProcessingPipeline(core_client=core_client)

        received_extension_results = None

        async def mock_facilitator_process(input_data):
            nonlocal received_extension_results
            if input_data.get("extension_results") is None:
                return {
                    "delegations": [{
                        "delegation_type": "context_extension",
                        "delegation_id": "d1",
                        "query": "What did Lisa say?",
                    }],
                    "board_instructions": [],
                    "response": "Checking...",
                    "token_usage": {"input": 100, "output": 20},
                }
            received_extension_results = input_data["extension_results"]
            return {
                "delegations": [],
                "board_instructions": [],
                "response": "Lisa said X.",
                "token_usage": {"input": 150, "output": 30},
            }

        async def mock_extension_process(input_data):
            return {
                "response": "Lisa discussed digital signatures for contract approval.",
                "messages_cited": ["msg-5"],
            }

        with patch("agents.facilitator.agent.FacilitatorAgent") as MockFacilitator, \
             patch("agents.context_extension.agent.ContextExtensionAgent") as MockExtension:
            MockFacilitator.return_value.process = mock_facilitator_process
            MockExtension.return_value.process = mock_extension_process
            await pipeline.execute("idea-1")

        assert received_extension_results is not None
        assert "extension_results" in received_extension_results
        assert "digital signatures" in received_extension_results
        assert "1 cited messages" in received_extension_results

    @pytest.mark.asyncio
    async def test_context_extension_publishes_delegation_complete(self, _clear_pipeline_state, settings):
        """Pipeline publishes ai.delegation.complete after context extension handling."""
        settings.AI_MOCK_MODE = True
        from pathlib import Path
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        core_client = _mock_core_client()
        pipeline = ChatProcessingPipeline(core_client=core_client)

        async def mock_process(input_data):
            if input_data.get("extension_results") is None:
                return {
                    "delegations": [{"delegation_type": "context_extension", "delegation_id": "d1", "query": "test"}],
                    "board_instructions": [],
                    "response": "Checking...",
                    "token_usage": {"input": 100, "output": 20},
                }
            return {
                "delegations": [],
                "board_instructions": [],
                "response": "Done.",
                "token_usage": {"input": 150, "output": 30},
            }

        with patch("agents.facilitator.agent.FacilitatorAgent") as MockAgent:
            MockAgent.return_value.process = mock_process
            await pipeline.execute("idea-1")

        events = get_published_events()
        delegation_complete = [e for e in events if e["event_type"] == "ai.delegation.complete"]
        assert len(delegation_complete) == 1
        assert delegation_complete[0]["delegation_type"] == "context_extension"

    @pytest.mark.asyncio
    async def test_context_extension_failure_returns_error_message(self, _clear_pipeline_state, settings):
        """If Context Extension Agent fails, pipeline injects error message."""
        settings.AI_MOCK_MODE = False
        from pathlib import Path
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        core_client = _mock_core_client()
        pipeline = ChatProcessingPipeline(core_client=core_client)

        received_extension_results = None

        async def mock_facilitator_process(input_data):
            nonlocal received_extension_results
            if input_data.get("extension_results") is None:
                return {
                    "delegations": [{"delegation_type": "context_extension", "delegation_id": "d1", "query": "test"}],
                    "board_instructions": [],
                    "response": "Checking...",
                    "token_usage": {"input": 100, "output": 20},
                }
            received_extension_results = input_data["extension_results"]
            return {
                "delegations": [],
                "board_instructions": [],
                "response": "Sorry, couldn't retrieve that.",
                "token_usage": {"input": 150, "output": 30},
            }

        async def mock_extension_process(input_data):
            raise RuntimeError("gRPC GetFullChatHistory failed")

        with patch("agents.facilitator.agent.FacilitatorAgent") as MockFacilitator, \
             patch("agents.context_extension.agent.ContextExtensionAgent") as MockExtension:
            MockFacilitator.return_value.process = mock_facilitator_process
            MockExtension.return_value.process = mock_extension_process
            result = await pipeline.execute("idea-1")

        assert result["status"] == "completed"
        assert received_extension_results is not None
        assert "error" in received_extension_results.lower()


# ── Board Agent invocation (M8) ──


class TestBoardAgentInvocation:
    @pytest.mark.asyncio
    async def test_board_agent_invoked_with_instructions(self, _clear_pipeline_state, settings):
        """Pipeline Step 5 invokes Board Agent when board_instructions present."""
        settings.AI_MOCK_MODE = True
        from pathlib import Path
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        core_client = _mock_core_client()
        core_client.get_board_state.return_value = {"nodes": [{"id": "n1", "title": "Existing"}], "connections": []}
        pipeline = ChatProcessingPipeline(core_client=core_client)

        board_agent_called = False
        board_agent_input = {}

        async def mock_facilitator_process(input_data):
            return {
                "delegations": [],
                "board_instructions": [{"intent": "add_topic", "description": "Add pain points"}],
                "response": "I'll add that to the board.",
                "token_usage": {"input": 100, "output": 20},
            }

        async def mock_board_process(input_data):
            nonlocal board_agent_called, board_agent_input
            board_agent_called = True
            board_agent_input = input_data
            return {"mutations": [{"type": "create_node"}], "mutation_count": 1}

        with patch("agents.facilitator.agent.FacilitatorAgent") as MockFacilitator, \
             patch("agents.board_agent.agent.BoardAgent") as MockBoardAgent:
            MockFacilitator.return_value.process = mock_facilitator_process
            MockBoardAgent.return_value.process = mock_board_process
            result = await pipeline.execute("idea-1")

        assert result["status"] == "completed"
        assert board_agent_called is True
        # Board Agent receives fresh board state from gRPC
        assert board_agent_input["board_state"]["nodes"][0]["title"] == "Existing"
        assert len(board_agent_input["instructions"]) == 1
        assert board_agent_input["instructions"][0]["intent"] == "add_topic"
        # get_board_state called for fresh state
        core_client.get_board_state.assert_called_once_with("idea-1")

    @pytest.mark.asyncio
    async def test_board_agent_publishes_updated_event(self, _clear_pipeline_state, settings):
        """Board Agent mutations trigger ai.board.updated event."""
        settings.AI_MOCK_MODE = True
        from pathlib import Path
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        core_client = _mock_core_client()
        core_client.get_board_state.return_value = {"nodes": [], "connections": []}
        pipeline = ChatProcessingPipeline(core_client=core_client)

        async def mock_facilitator_process(input_data):
            return {
                "delegations": [],
                "board_instructions": [{"intent": "add_topic", "description": "Test"}],
                "response": "Done.",
                "token_usage": {"input": 100, "output": 20},
            }

        async def mock_board_process(input_data):
            return {"mutations": [{"type": "create_node"}], "mutation_count": 1}

        with patch("agents.facilitator.agent.FacilitatorAgent") as MockFacilitator, \
             patch("agents.board_agent.agent.BoardAgent") as MockBoardAgent:
            MockFacilitator.return_value.process = mock_facilitator_process
            MockBoardAgent.return_value.process = mock_board_process
            await pipeline.execute("idea-1")

        events = get_published_events()
        board_events = [e for e in events if e["event_type"] == "ai.board.updated"]
        assert len(board_events) == 1
        assert board_events[0]["idea_id"] == "idea-1"
        assert board_events[0]["mutation_count"] == 1

    @pytest.mark.asyncio
    async def test_no_board_event_when_no_instructions(self, _clear_pipeline_state, settings):
        """No ai.board.updated event when no board instructions."""
        settings.AI_MOCK_MODE = True
        from pathlib import Path
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        core_client = _mock_core_client()
        pipeline = ChatProcessingPipeline(core_client=core_client)

        async def mock_facilitator_process(input_data):
            return {
                "delegations": [],
                "board_instructions": [],
                "response": "No board changes needed.",
                "token_usage": {"input": 100, "output": 20},
            }

        with patch("agents.facilitator.agent.FacilitatorAgent") as MockFacilitator:
            MockFacilitator.return_value.process = mock_facilitator_process
            await pipeline.execute("idea-1")

        events = get_published_events()
        board_events = [e for e in events if e["event_type"] == "ai.board.updated"]
        assert len(board_events) == 0

    @pytest.mark.asyncio
    async def test_no_board_event_when_zero_mutations(self, _clear_pipeline_state, settings):
        """No ai.board.updated event when Board Agent returns 0 mutations."""
        settings.AI_MOCK_MODE = True
        from pathlib import Path
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        core_client = _mock_core_client()
        core_client.get_board_state.return_value = {"nodes": [], "connections": []}
        pipeline = ChatProcessingPipeline(core_client=core_client)

        async def mock_facilitator_process(input_data):
            return {
                "delegations": [],
                "board_instructions": [{"intent": "add_topic", "description": "Test"}],
                "response": "Trying to update board.",
                "token_usage": {"input": 100, "output": 20},
            }

        async def mock_board_process(input_data):
            return {"mutations": [], "mutation_count": 0}

        with patch("agents.facilitator.agent.FacilitatorAgent") as MockFacilitator, \
             patch("agents.board_agent.agent.BoardAgent") as MockBoardAgent:
            MockFacilitator.return_value.process = mock_facilitator_process
            MockBoardAgent.return_value.process = mock_board_process
            await pipeline.execute("idea-1")

        events = get_published_events()
        board_events = [e for e in events if e["event_type"] == "ai.board.updated"]
        assert len(board_events) == 0


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
