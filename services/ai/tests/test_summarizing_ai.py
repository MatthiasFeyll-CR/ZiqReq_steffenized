"""Tests for the Summarizing AI Agent (US-001).

Test IDs: T-4.1.01, T-4.1.02, T-4.2.01, T-4.2.02, T-4.8.01, T-4.9.01,
           AI-4.01, AI-4.02, AI-4.03
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.summarizing_ai.agent import SummarizingAIAgent, _apply_mode_logic, _parse_response
from agents.summarizing_ai.prompt import (
    SECTION_KEYS,
    SECTION_LABELS,
    build_system_prompt,
)

# ── Helpers ──


def _make_input_data(
    mode: str = "full_generation",
    chat_summary: str = "Users discussed automating invoice processing.",
    recent_messages: list | None = None,
    locked_sections: list | None = None,
    allow_information_gaps: bool = False,
    section_name: str | None = None,
) -> dict:
    if recent_messages is None:
        recent_messages = [
            {"sender_type": "user", "content": "We need to automate invoice processing."},
            {"sender_type": "ai", "ai_agent": "facilitator", "content": "What departments are involved?"},
            {"sender_type": "user", "content": "Accounts Payable and Finance."},
        ]
    if locked_sections is None:
        locked_sections = []
    return {
        "mode": mode,
        "chat_summary": chat_summary,
        "recent_messages": recent_messages,
        "locked_sections": locked_sections,
        "allow_information_gaps": allow_information_gaps,
        "section_name": section_name,
    }


def _make_full_brd_response() -> dict:
    """A realistic full BRD response from the LLM."""
    return {
        "section_title": "Automated Invoice Processing System",
        "section_short_description": "A system to automate invoice processing at Commerz Real.",
        "section_current_workflow": "Invoices are manually processed by AP clerks. Pain points: slow, error-prone.",
        "section_affected_department": "Accounts Payable, Finance Controlling.",
        "section_core_capabilities": "OCR extraction, digital approval routing, SAP auto-population.",
        "section_success_criteria": "Processing time under 2 days, error rate below 2%.",
        "readiness_evaluation": {
            "title": "ready",
            "short_description": "ready",
            "current_workflow": "ready",
            "affected_department": "ready",
            "core_capabilities": "ready",
            "success_criteria": "ready",
        },
    }


class _MockSettings:
    """Minimal mock for prompt execution settings."""

    def __init__(self, service_id: str = "default") -> None:
        self.service_id = service_id
        self.max_tokens = 3000
        self.temperature = 0.3


# ── System Prompt Tests ──


class TestSystemPrompt:
    def test_prompt_includes_identity(self):
        input_data = _make_input_data()
        prompt = build_system_prompt(input_data)
        assert "Summarizing AI" in prompt
        assert "Commerz Real" in prompt

    def test_prompt_includes_critical_rule(self):
        input_data = _make_input_data()
        prompt = build_system_prompt(input_data)
        assert "NEVER FABRICATE" in prompt

    def test_prompt_includes_chat_summary(self):
        input_data = _make_input_data(chat_summary="Test summary content")
        prompt = build_system_prompt(input_data)
        assert "Test summary content" in prompt

    def test_prompt_includes_recent_messages(self):
        input_data = _make_input_data()
        prompt = build_system_prompt(input_data)
        assert "automate invoice processing" in prompt

    def test_prompt_full_generation_mode(self):
        input_data = _make_input_data(mode="full_generation")
        prompt = build_system_prompt(input_data)
        assert "ALL 6 sections" in prompt

    def test_prompt_selective_regeneration_mode(self):
        input_data = _make_input_data(
            mode="selective_regeneration",
            locked_sections=["title", "core_capabilities"],
        )
        prompt = build_system_prompt(input_data)
        assert "unlocked sections" in prompt
        assert "title" in prompt
        assert "core_capabilities" in prompt

    def test_prompt_section_regeneration_mode(self):
        input_data = _make_input_data(
            mode="section_regeneration",
            section_name="current_workflow",
        )
        prompt = build_system_prompt(input_data)
        assert "current_workflow" in prompt
        assert "ONLY the section" in prompt

    def test_prompt_gaps_allowed(self):
        input_data = _make_input_data(allow_information_gaps=True)
        prompt = build_system_prompt(input_data)
        assert "/TODO" in prompt
        assert "information_gaps_mode" in prompt

    def test_prompt_gaps_disallowed(self):
        input_data = _make_input_data(allow_information_gaps=False)
        prompt = build_system_prompt(input_data)
        assert "Not enough information" in prompt
        assert "no_gaps_mode" in prompt

    def test_prompt_includes_readiness_evaluation(self):
        input_data = _make_input_data()
        prompt = build_system_prompt(input_data)
        assert "readiness_evaluation" in prompt
        assert '"ready"' in prompt or "ready" in prompt
        assert '"insufficient"' in prompt or "insufficient" in prompt

    def test_prompt_includes_output_format(self):
        input_data = _make_input_data()
        prompt = build_system_prompt(input_data)
        assert "output_format" in prompt
        assert "JSON" in prompt

    def test_prompt_includes_all_six_sections(self):
        input_data = _make_input_data()
        prompt = build_system_prompt(input_data)
        for label in SECTION_LABELS.values():
            assert label in prompt

    def test_prompt_empty_messages(self):
        input_data = _make_input_data(recent_messages=[])
        prompt = build_system_prompt(input_data)
        assert "(no recent messages)" in prompt


# ── Response Parsing Tests ──


class TestResponseParsing:
    def test_parse_valid_json(self):
        response = json.dumps(_make_full_brd_response())
        parsed = _parse_response(response)
        assert parsed["section_title"] == "Automated Invoice Processing System"

    def test_parse_json_in_code_block(self):
        brd = _make_full_brd_response()
        response = f"```json\n{json.dumps(brd)}\n```"
        parsed = _parse_response(response)
        assert parsed["section_title"] == "Automated Invoice Processing System"

    def test_parse_invalid_json_returns_fallback(self):
        parsed = _parse_response("This is not JSON at all")
        # Should return fallback with all sections = 'Not enough information.'
        for key in SECTION_KEYS:
            assert parsed[f"section_{key}"] == "Not enough information."
        assert all(
            v == "insufficient"
            for v in parsed["readiness_evaluation"].values()
        )


# ── T-4.1.01: Agent supports all 3 generation modes ──


class TestGenerationModes:
    """T-4.1.01: Agent supports all 3 generation modes."""

    def test_full_generation_returns_all_sections(self):
        """full_generation → all 6 sections present."""
        brd = _make_full_brd_response()
        input_data = _make_input_data(mode="full_generation")
        result = _apply_mode_logic(brd, input_data)

        for key in SECTION_KEYS:
            assert result[f"section_{key}"] is not None

    def test_selective_regeneration_skips_locked(self):
        """AI-4.02: selective_regeneration respects locks — locked sections are None."""
        brd = _make_full_brd_response()
        input_data = _make_input_data(
            mode="selective_regeneration",
            locked_sections=["title", "core_capabilities"],
        )
        result = _apply_mode_logic(brd, input_data)

        assert result["section_title"] is None
        assert result["section_core_capabilities"] is None
        # Unlocked sections should have content
        assert result["section_short_description"] is not None
        assert result["section_current_workflow"] is not None

    def test_section_regeneration_only_target(self):
        """AI-4.03: section_regeneration returns only the specified section."""
        brd = _make_full_brd_response()
        input_data = _make_input_data(
            mode="section_regeneration",
            section_name="current_workflow",
        )
        result = _apply_mode_logic(brd, input_data)

        assert result["section_current_workflow"] is not None
        # All other sections should be None
        assert result["section_title"] is None
        assert result["section_short_description"] is None
        assert result["section_affected_department"] is None
        assert result["section_core_capabilities"] is None
        assert result["section_success_criteria"] is None


# ── T-4.1.02: All 6 sections generated ──


class TestAllSectionsGenerated:
    """T-4.1.02: full_generation produces all 6 sections."""

    def test_output_contains_all_six_section_fields(self):
        brd = _make_full_brd_response()
        input_data = _make_input_data(mode="full_generation")
        result = _apply_mode_logic(brd, input_data)

        expected_fields = [f"section_{key}" for key in SECTION_KEYS]
        for field in expected_fields:
            assert field in result, f"Missing field: {field}"


# ── T-4.2.01: Insufficient sections show 'Not enough information' ──


class TestInsufficientSections:
    """T-4.2.01: Empty chat → 'Not enough information'."""

    def test_fallback_on_parse_failure(self):
        parsed = _parse_response("not json")
        for key in SECTION_KEYS:
            assert parsed[f"section_{key}"] == "Not enough information."

    def test_readiness_all_insufficient_on_fallback(self):
        parsed = _parse_response("not json")
        for key in SECTION_KEYS:
            assert parsed["readiness_evaluation"][key] == "insufficient"


# ── T-4.2.02: No fabrication when gaps disallowed ──


class TestNoFabrication:
    """T-4.2.02: System prompt enforces 'Not enough information' when gaps disallowed."""

    def test_prompt_no_todo_when_gaps_false(self):
        input_data = _make_input_data(allow_information_gaps=False)
        prompt = build_system_prompt(input_data)
        assert "no_gaps_mode" in prompt
        assert "Not enough information" in prompt
        # Should NOT contain information_gaps_mode instructions
        assert "information_gaps_mode" not in prompt


# ── T-4.8.01: Readiness evaluation in output ──


class TestReadinessEvaluation:
    """T-4.8.01: Agent output includes readiness_evaluation."""

    def test_readiness_in_full_generation(self):
        brd = _make_full_brd_response()
        input_data = _make_input_data(mode="full_generation")
        result = _apply_mode_logic(brd, input_data)

        assert "readiness_evaluation" in result
        evaluation = result["readiness_evaluation"]
        for key in SECTION_KEYS:
            assert key in evaluation
            assert evaluation[key] in ("ready", "insufficient")

    def test_readiness_defaults_to_insufficient(self):
        """When readiness_evaluation is missing, defaults to all insufficient."""
        brd = _make_full_brd_response()
        del brd["readiness_evaluation"]
        input_data = _make_input_data(mode="full_generation")
        result = _apply_mode_logic(brd, input_data)

        assert "readiness_evaluation" in result
        for key in SECTION_KEYS:
            assert result["readiness_evaluation"][key] == "insufficient"

    def test_readiness_mixed_statuses(self):
        """Fixture returns mixed ready/insufficient statuses."""
        brd = _make_full_brd_response()
        brd["readiness_evaluation"]["success_criteria"] = "insufficient"
        brd["readiness_evaluation"]["affected_department"] = "insufficient"
        input_data = _make_input_data(mode="full_generation")
        result = _apply_mode_logic(brd, input_data)

        assert result["readiness_evaluation"]["title"] == "ready"
        assert result["readiness_evaluation"]["success_criteria"] == "insufficient"
        assert result["readiness_evaluation"]["affected_department"] == "insufficient"


# ── T-4.9.01: /TODO markers when gaps allowed ──


class TestTodoMarkers:
    """T-4.9.01: allow_information_gaps=true → /TODO markers in prompt."""

    def test_prompt_instructs_todo_markers_when_gaps_true(self):
        input_data = _make_input_data(allow_information_gaps=True)
        prompt = build_system_prompt(input_data)
        assert "/TODO" in prompt

    def test_prompt_no_todo_markers_when_gaps_false(self):
        input_data = _make_input_data(allow_information_gaps=False)
        prompt = build_system_prompt(input_data)
        # The prompt in no_gaps_mode should mention NOT using /TODO
        assert "do NOT use /TODO" in prompt


# ── Mock Mode Tests ──


class TestMockMode:
    @pytest.mark.asyncio
    async def test_mock_mode_full_generation(self, settings):
        """Mock mode returns realistic fixture with all 6 sections."""
        settings.AI_MOCK_MODE = True
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        agent = SummarizingAIAgent()
        result = await agent.process(_make_input_data(mode="full_generation"))

        for key in SECTION_KEYS:
            assert result[f"section_{key}"] is not None
        assert "readiness_evaluation" in result

    @pytest.mark.asyncio
    async def test_mock_mode_selective_regeneration(self, settings):
        """Mock mode with selective_regeneration respects locks."""
        settings.AI_MOCK_MODE = True
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        agent = SummarizingAIAgent()
        result = await agent.process(
            _make_input_data(
                mode="selective_regeneration",
                locked_sections=["title", "core_capabilities"],
            )
        )

        assert result["section_title"] is None
        assert result["section_core_capabilities"] is None
        assert result["section_short_description"] is not None

    @pytest.mark.asyncio
    async def test_mock_mode_section_regeneration(self, settings):
        """Mock mode with section_regeneration returns only target section."""
        settings.AI_MOCK_MODE = True
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        agent = SummarizingAIAgent()
        result = await agent.process(
            _make_input_data(
                mode="section_regeneration",
                section_name="current_workflow",
            )
        )

        assert result["section_current_workflow"] is not None
        assert result["section_title"] is None

    @pytest.mark.asyncio
    async def test_mock_mode_readiness_has_mixed_statuses(self, settings):
        """Mock fixture returns mixed ready/insufficient statuses."""
        settings.AI_MOCK_MODE = True
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        agent = SummarizingAIAgent()
        result = await agent.process(_make_input_data(mode="full_generation"))

        evaluation = result["readiness_evaluation"]
        statuses = set(evaluation.values())
        # Fixture has 5 ready and 1 insufficient
        assert "ready" in statuses
        assert "insufficient" in statuses


# ── AI-4.01: SK Integration (mocked) ──


class TestSKIntegration:
    """AI-4.01: full_generation with sufficient data via mocked SK."""

    @pytest.mark.asyncio
    async def test_execute_calls_sk_and_returns_parsed(self):
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

        brd_response = _make_full_brd_response()
        mock_message = AsyncMock()
        mock_message.__str__ = lambda self: json.dumps(brd_response)

        with (
            patch("agents.summarizing_ai.agent.get_deployment", return_value="test-deploy"),
            patch("agents.summarizing_ai.agent.create_kernel") as mock_kernel_factory,
        ):
            mock_service = AsyncMock(spec=AzureChatCompletion)
            mock_service.get_prompt_execution_settings_class.return_value = _MockSettings
            mock_service.get_chat_message_contents = AsyncMock(return_value=[mock_message])

            mock_kernel = MagicMock()
            mock_kernel.get_service.return_value = mock_service
            mock_kernel_factory.return_value = mock_kernel

            agent = SummarizingAIAgent()
            result = await agent._execute(_make_input_data(mode="full_generation"))

        assert result["section_title"] == "Automated Invoice Processing System"
        assert result["readiness_evaluation"]["title"] == "ready"
        for key in SECTION_KEYS:
            assert result[f"section_{key}"] is not None

    @pytest.mark.asyncio
    async def test_execute_uses_temperature_03(self):
        """Agent uses temperature 0.3 for deterministic output."""
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

        captured_settings = {}

        class _CapturingSettings:
            def __init__(self, service_id: str = "default") -> None:
                self.service_id = service_id
                self.max_tokens = 0
                self.temperature = 0.0
                captured_settings["instance"] = self

        brd_response = _make_full_brd_response()
        mock_message = AsyncMock()
        mock_message.__str__ = lambda self: json.dumps(brd_response)

        with (
            patch("agents.summarizing_ai.agent.get_deployment", return_value="test-deploy"),
            patch("agents.summarizing_ai.agent.create_kernel") as mock_kernel_factory,
        ):
            mock_service = AsyncMock(spec=AzureChatCompletion)
            mock_service.get_prompt_execution_settings_class.return_value = _CapturingSettings
            mock_service.get_chat_message_contents = AsyncMock(return_value=[mock_message])

            mock_kernel = MagicMock()
            mock_kernel.get_service.return_value = mock_service
            mock_kernel_factory.return_value = mock_kernel

            agent = SummarizingAIAgent()
            await agent._execute(_make_input_data())

        assert captured_settings["instance"].temperature == 0.3
        assert captured_settings["instance"].max_tokens == 3000
