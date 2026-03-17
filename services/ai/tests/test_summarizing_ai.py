"""Tests for the Summarizing AI Agent (US-002 — hierarchical requirements).

Test IDs: T-4.1.01, T-4.1.02, T-4.2.01, T-4.2.02, T-4.8.01, T-4.9.01,
           AI-4.01, AI-4.02, AI-4.03
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.summarizing_ai.agent import (
    SummarizingAIAgent,
    _apply_mode_logic,
    _parse_response,
    _validate_structure,
)
from agents.summarizing_ai.prompt import build_system_prompt

# ── Helpers ──


def _make_input_data(
    mode: str = "full_generation",
    project_type: str = "software",
    chat_summary: str = "Users discussed automating invoice processing.",
    recent_messages: list | None = None,
    locked_items: dict | None = None,
    allow_information_gaps: bool = False,
    item_id: str | None = None,
) -> dict:
    if recent_messages is None:
        recent_messages = [
            {"sender_type": "user", "content": "We need to automate invoice processing."},
            {"sender_type": "ai", "ai_agent": "facilitator", "content": "What departments are involved?"},
            {"sender_type": "user", "content": "Accounts Payable and Finance."},
        ]
    if locked_items is None:
        locked_items = {}
    return {
        "mode": mode,
        "project_type": project_type,
        "chat_summary": chat_summary,
        "recent_messages": recent_messages,
        "locked_items": locked_items,
        "allow_information_gaps": allow_information_gaps,
        "item_id": item_id,
    }


def _make_software_response() -> dict:
    """A realistic hierarchical software response from the LLM."""
    return {
        "title": "Automated Invoice Processing System",
        "short_description": "A system to automate invoice processing at Commerz Real.",
        "structure": [
            {
                "epic_id": "epic-001",
                "title": "Invoice Intake",
                "description": "Automated capture of incoming invoices.",
                "stories": [
                    {
                        "story_id": "story-001",
                        "title": "As an AP clerk, I want to upload invoices so that they are processed automatically",
                        "description": "Upload interface for invoices.",
                        "acceptance_criteria": "- Upload accepts PDF\n- Confirmation shown",
                        "priority": "High",
                    }
                ],
            },
            {
                "epic_id": "epic-002",
                "title": "Approval Routing",
                "description": "Digital approval chains for invoices.",
                "stories": [
                    {
                        "story_id": "story-002",
                        "title": "As a manager, I want to approve invoices digitally so that I don't need paper",
                        "description": "Digital approval workflow.",
                        "acceptance_criteria": "- Approve/reject actions\n- Notification sent",
                        "priority": "High",
                    }
                ],
            },
        ],
        "readiness_evaluation": {
            "ready_for_development": True,
            "missing_information": [],
            "recommendation": "All epics have stories with acceptance criteria.",
        },
    }


def _make_non_software_response() -> dict:
    """A realistic hierarchical non-software response from the LLM."""
    return {
        "title": "Office Relocation Project",
        "short_description": "Plan and execute office relocation to new building.",
        "structure": [
            {
                "milestone_id": "ms-001",
                "title": "Site Preparation",
                "description": "Prepare the new office site for move-in.",
                "packages": [
                    {
                        "package_id": "wp-001",
                        "title": "IT Infrastructure Setup",
                        "description": "Network and server room setup.",
                        "deliverables": "- Network cabling\n- Server room ready",
                        "dependencies": "Lease agreement signed",
                    }
                ],
            },
        ],
        "readiness_evaluation": {
            "ready_for_execution": True,
            "missing_information": [],
            "recommendation": "All milestones have work packages with deliverables.",
        },
    }


class _MockSettings:
    """Minimal mock for prompt execution settings."""

    def __init__(self, service_id: str = "default") -> None:
        self.service_id = service_id
        self.max_tokens = 4000
        self.temperature = 0.3


# ── System Prompt Tests ──


class TestSystemPrompt:
    def test_prompt_includes_identity(self):
        input_data = _make_input_data()
        prompt = build_system_prompt(input_data)
        assert "requirements document generator" in prompt
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

    def test_prompt_includes_project_type_software(self):
        input_data = _make_input_data(project_type="software")
        prompt = build_system_prompt(input_data)
        assert "<project_type>software</project_type>" in prompt

    def test_prompt_includes_project_type_non_software(self):
        input_data = _make_input_data(project_type="non_software")
        prompt = build_system_prompt(input_data)
        assert "<project_type>non_software</project_type>" in prompt

    def test_prompt_software_output_format(self):
        input_data = _make_input_data(project_type="software")
        prompt = build_system_prompt(input_data)
        assert "epic_id" in prompt
        assert "stories" in prompt
        assert "acceptance_criteria" in prompt
        assert "ready_for_development" in prompt

    def test_prompt_non_software_output_format(self):
        input_data = _make_input_data(project_type="non_software")
        prompt = build_system_prompt(input_data)
        assert "milestone_id" in prompt
        assert "packages" in prompt
        assert "deliverables" in prompt
        assert "ready_for_execution" in prompt

    def test_prompt_full_generation_mode(self):
        input_data = _make_input_data(mode="full_generation", project_type="software")
        prompt = build_system_prompt(input_data)
        assert "epics" in prompt
        assert "user stories" in prompt
        assert "from scratch" in prompt

    def test_prompt_selective_regeneration_mode(self):
        input_data = _make_input_data(
            mode="selective_regeneration",
            locked_items={"epic-001": True, "story-002": True},
        )
        prompt = build_system_prompt(input_data)
        assert "unlocked" in prompt
        assert "epic-001" in prompt

    def test_prompt_item_regeneration_mode(self):
        input_data = _make_input_data(
            mode="item_regeneration",
            item_id="epic-001",
        )
        prompt = build_system_prompt(input_data)
        assert "epic-001" in prompt
        assert "ONLY the item" in prompt

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

    def test_prompt_includes_output_format(self):
        input_data = _make_input_data()
        prompt = build_system_prompt(input_data)
        assert "output_format" in prompt
        assert "JSON" in prompt

    def test_prompt_no_old_brd_sections(self):
        """Old 6-section BRD format references must not appear."""
        input_data = _make_input_data()
        prompt = build_system_prompt(input_data)
        assert "current_workflow" not in prompt
        assert "affected_department" not in prompt
        assert "core_capabilities" not in prompt
        assert "success_criteria" not in prompt.split("readiness_evaluation")[0]

    def test_prompt_empty_messages(self):
        input_data = _make_input_data(recent_messages=[])
        prompt = build_system_prompt(input_data)
        assert "(no recent messages)" in prompt

    def test_prompt_software_readiness_spec(self):
        input_data = _make_input_data(project_type="software")
        prompt = build_system_prompt(input_data)
        assert "epics have at least one user story" in prompt

    def test_prompt_non_software_readiness_spec(self):
        input_data = _make_input_data(project_type="non_software")
        prompt = build_system_prompt(input_data)
        assert "milestones have at least one work package" in prompt


# ── Response Parsing Tests ──


class TestResponseParsing:
    def test_parse_valid_software_json(self):
        response = json.dumps(_make_software_response())
        parsed = _parse_response(response, "software")
        assert parsed["title"] == "Automated Invoice Processing System"
        assert len(parsed["structure"]) == 2

    def test_parse_valid_non_software_json(self):
        response = json.dumps(_make_non_software_response())
        parsed = _parse_response(response, "non_software")
        assert parsed["title"] == "Office Relocation Project"
        assert len(parsed["structure"]) == 1

    def test_parse_json_in_code_block(self):
        resp = _make_software_response()
        response = f"```json\n{json.dumps(resp)}\n```"
        parsed = _parse_response(response, "software")
        assert parsed["title"] == "Automated Invoice Processing System"

    def test_parse_invalid_json_returns_fallback(self):
        parsed = _parse_response("This is not JSON at all", "software")
        assert parsed["title"] == "Not enough information."
        assert parsed["structure"] == []
        assert parsed["readiness_evaluation"]["ready_for_development"] is False

    def test_parse_invalid_json_non_software_fallback(self):
        parsed = _parse_response("not json", "non_software")
        assert parsed["title"] == "Not enough information."
        assert parsed["readiness_evaluation"]["ready_for_execution"] is False

    def test_parse_wrong_structure_type_returns_fallback(self):
        """Software response validated against non_software type fails."""
        response = json.dumps(_make_software_response())
        parsed = _parse_response(response, "non_software")
        # Software response has epic_id, not milestone_id — validation fails
        assert parsed["structure"] == []


# ── Structure Validation Tests ──


class TestStructureValidation:
    def test_valid_software_structure(self):
        resp = _make_software_response()
        assert _validate_structure(resp, "software") is True

    def test_valid_non_software_structure(self):
        resp = _make_non_software_response()
        assert _validate_structure(resp, "non_software") is True

    def test_missing_structure_key(self):
        assert _validate_structure({"title": "foo"}, "software") is False

    def test_structure_not_list(self):
        assert _validate_structure({"structure": "bad"}, "software") is False

    def test_software_missing_epic_id(self):
        resp = {"structure": [{"title": "no epic_id"}]}
        assert _validate_structure(resp, "software") is False

    def test_non_software_missing_milestone_id(self):
        resp = {"structure": [{"title": "no milestone_id"}]}
        assert _validate_structure(resp, "non_software") is False

    def test_empty_structure_is_valid(self):
        resp = {"structure": []}
        assert _validate_structure(resp, "software") is True


# ── T-4.1.01: Agent supports all 3 generation modes ──


class TestGenerationModes:
    """T-4.1.01: Agent supports all 3 generation modes."""

    def test_full_generation_returns_structure(self):
        """full_generation returns complete hierarchical structure."""
        resp = _make_software_response()
        input_data = _make_input_data(mode="full_generation")
        result = _apply_mode_logic(resp, input_data)
        assert len(result["structure"]) == 2
        assert result["title"] == "Automated Invoice Processing System"

    def test_selective_regeneration_preserves_locked_info(self):
        """AI-4.02: selective_regeneration notes locked items."""
        resp = _make_software_response()
        input_data = _make_input_data(
            mode="selective_regeneration",
            locked_items={"epic-001": True, "story-002": True},
        )
        result = _apply_mode_logic(resp, input_data)
        assert "epic-001" in result["locked_items_preserved"]
        assert "story-002" in result["locked_items_preserved"]

    def test_item_regeneration_tracks_target(self):
        """AI-4.03: item_regeneration tracks regenerated item ID."""
        resp = _make_software_response()
        input_data = _make_input_data(
            mode="item_regeneration",
            item_id="epic-001",
        )
        result = _apply_mode_logic(resp, input_data)
        assert result["regenerated_item_id"] == "epic-001"


# ── T-4.1.02: Hierarchical structure generated ──


class TestHierarchicalStructure:
    """T-4.1.02: full_generation produces hierarchical structure."""

    def test_software_has_epics_and_stories(self):
        resp = _make_software_response()
        input_data = _make_input_data(mode="full_generation", project_type="software")
        result = _apply_mode_logic(resp, input_data)
        assert "structure" in result
        for epic in result["structure"]:
            assert "epic_id" in epic
            assert "stories" in epic
            for story in epic["stories"]:
                assert "story_id" in story
                assert "acceptance_criteria" in story

    def test_non_software_has_milestones_and_packages(self):
        resp = _make_non_software_response()
        input_data = _make_input_data(mode="full_generation", project_type="non_software")
        result = _apply_mode_logic(resp, input_data)
        assert "structure" in result
        for ms in result["structure"]:
            assert "milestone_id" in ms
            assert "packages" in ms
            for pkg in ms["packages"]:
                assert "package_id" in pkg
                assert "deliverables" in pkg


# ── T-4.2.01: Insufficient data handling ──


class TestInsufficientData:
    """T-4.2.01: Empty chat → empty structure with not-ready evaluation."""

    def test_fallback_on_parse_failure_software(self):
        parsed = _parse_response("not json", "software")
        assert parsed["structure"] == []
        assert parsed["readiness_evaluation"]["ready_for_development"] is False

    def test_fallback_on_parse_failure_non_software(self):
        parsed = _parse_response("not json", "non_software")
        assert parsed["structure"] == []
        assert parsed["readiness_evaluation"]["ready_for_execution"] is False


# ── T-4.2.02: No fabrication when gaps disallowed ──


class TestNoFabrication:
    """T-4.2.02: System prompt enforces 'Not enough information' when gaps disallowed."""

    def test_prompt_no_todo_when_gaps_false(self):
        input_data = _make_input_data(allow_information_gaps=False)
        prompt = build_system_prompt(input_data)
        assert "no_gaps_mode" in prompt
        assert "Not enough information" in prompt
        assert "information_gaps_mode" not in prompt


# ── T-4.8.01: Readiness evaluation in output ──


class TestReadinessEvaluation:
    """T-4.8.01: Agent output includes readiness_evaluation."""

    def test_readiness_in_software_response(self):
        resp = _make_software_response()
        input_data = _make_input_data(mode="full_generation", project_type="software")
        result = _apply_mode_logic(resp, input_data)
        assert "readiness_evaluation" in result
        assert "ready_for_development" in result["readiness_evaluation"]

    def test_readiness_in_non_software_response(self):
        resp = _make_non_software_response()
        input_data = _make_input_data(mode="full_generation", project_type="non_software")
        result = _apply_mode_logic(resp, input_data)
        assert "readiness_evaluation" in result
        assert "ready_for_execution" in result["readiness_evaluation"]

    def test_readiness_defaults_when_missing_software(self):
        resp = _make_software_response()
        del resp["readiness_evaluation"]
        input_data = _make_input_data(mode="full_generation", project_type="software")
        result = _apply_mode_logic(resp, input_data)
        assert result["readiness_evaluation"]["ready_for_development"] is False

    def test_readiness_defaults_when_missing_non_software(self):
        resp = _make_non_software_response()
        del resp["readiness_evaluation"]
        input_data = _make_input_data(mode="full_generation", project_type="non_software")
        result = _apply_mode_logic(resp, input_data)
        assert result["readiness_evaluation"]["ready_for_execution"] is False


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
        assert "do NOT use /TODO" in prompt


# ── Mock Mode Tests ──


class TestMockMode:
    @pytest.mark.asyncio
    async def test_mock_mode_full_generation(self, settings):
        """Mock mode returns realistic fixture with hierarchical structure."""
        settings.AI_MOCK_MODE = True
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        agent = SummarizingAIAgent()
        result = await agent.process(_make_input_data(mode="full_generation"))

        assert "structure" in result
        assert isinstance(result["structure"], list)
        assert len(result["structure"]) > 0
        assert "readiness_evaluation" in result

    @pytest.mark.asyncio
    async def test_mock_mode_selective_regeneration(self, settings):
        """Mock mode with selective_regeneration tracks locked items."""
        settings.AI_MOCK_MODE = True
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        agent = SummarizingAIAgent()
        result = await agent.process(
            _make_input_data(
                mode="selective_regeneration",
                locked_items={"epic-001": True},
            )
        )

        assert "locked_items_preserved" in result
        assert "epic-001" in result["locked_items_preserved"]

    @pytest.mark.asyncio
    async def test_mock_mode_item_regeneration(self, settings):
        """Mock mode with item_regeneration tracks target item."""
        settings.AI_MOCK_MODE = True
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        agent = SummarizingAIAgent()
        result = await agent.process(
            _make_input_data(
                mode="item_regeneration",
                item_id="epic-001",
            )
        )

        assert result["regenerated_item_id"] == "epic-001"

    @pytest.mark.asyncio
    async def test_mock_mode_readiness_not_ready(self, settings):
        """Mock fixture returns readiness_evaluation with ready_for_development=false."""
        settings.AI_MOCK_MODE = True
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        agent = SummarizingAIAgent()
        result = await agent.process(_make_input_data(mode="full_generation"))

        evaluation = result["readiness_evaluation"]
        assert "ready_for_development" in evaluation
        # Fixture has ready_for_development: false
        assert evaluation["ready_for_development"] is False


# ── AI-4.01: SK Integration (mocked) ──


class TestSKIntegration:
    """AI-4.01: full_generation with sufficient data via mocked SK."""

    @pytest.mark.asyncio
    async def test_execute_calls_sk_and_returns_parsed(self):
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

        sw_response = _make_software_response()
        mock_message = AsyncMock()
        mock_message.__str__ = lambda self: json.dumps(sw_response)

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

        assert result["title"] == "Automated Invoice Processing System"
        assert len(result["structure"]) == 2
        assert result["readiness_evaluation"]["ready_for_development"] is True

    @pytest.mark.asyncio
    async def test_execute_uses_temperature_03_and_max_4000(self):
        """Agent uses temperature 0.3 and max_tokens 4000."""
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

        captured_settings = {}

        class _CapturingSettings:
            def __init__(self, service_id: str = "default") -> None:
                self.service_id = service_id
                self.max_tokens = 0
                self.temperature = 0.0
                captured_settings["instance"] = self

        sw_response = _make_software_response()
        mock_message = AsyncMock()
        mock_message.__str__ = lambda self: json.dumps(sw_response)

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
        assert captured_settings["instance"].max_tokens == 4000

    @pytest.mark.asyncio
    async def test_execute_non_software_project(self):
        """Agent handles non-software project type correctly."""
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

        ns_response = _make_non_software_response()
        mock_message = AsyncMock()
        mock_message.__str__ = lambda self: json.dumps(ns_response)

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
            result = await agent._execute(
                _make_input_data(mode="full_generation", project_type="non_software")
            )

        assert result["title"] == "Office Relocation Project"
        assert len(result["structure"]) == 1
        assert "milestone_id" in result["structure"][0]
