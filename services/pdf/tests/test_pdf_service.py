"""Tests for PDF generation service — type-specific templates."""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from services.pdf.generator.builder import (
    RequirementsDocumentContent,
    build_html,
    parse_structure_json,
)
from services.pdf.generator.renderer import render_pdf
from services.pdf.grpc_server.servicers.pdf_servicer import PdfServicer

# ── Fixtures ──────────────────────────────────────────────────────


def _software_structure() -> list[dict]:
    return [
        {
            "id": "epic-0001-aaaa-bbbb-ccccddddeeee",
            "type": "epic",
            "title": "User Authentication",
            "description": "Handle user authentication and authorization.",
            "children": [
                {
                    "id": "story-0001-aaaa-bbbb-ccccddddeeee",
                    "type": "user_story",
                    "title": "As a user, I want to log in so that I can access my account",
                    "description": "Login with email and password",
                    "acceptance_criteria": "- User can enter email\n- User can enter password\n- Invalid credentials show error",
                    "priority": "High",
                },
                {
                    "id": "story-0002-aaaa-bbbb-ccccddddeeee",
                    "type": "user_story",
                    "title": "As a user, I want to reset my password",
                    "description": "Password reset via email link",
                    "acceptance_criteria": "- Reset link sent to email\n- Link expires after 24h",
                    "priority": "Medium",
                },
            ],
        }
    ]


def _non_software_structure() -> list[dict]:
    return [
        {
            "id": "ms-0001-aaaa-bbbb-ccccddddeeee",
            "type": "milestone",
            "title": "Phase 1: Planning",
            "description": "Initial planning and requirements gathering.",
            "children": [
                {
                    "id": "wp-0001-aaaa-bbbb-ccccddddeeee",
                    "type": "work_package",
                    "title": "Stakeholder Interviews",
                    "description": "Interview all key stakeholders",
                    "deliverables": "- Interview notes\n- Summary report",
                    "dependencies": "Project kickoff completed",
                },
            ],
        }
    ]


def _sample_software_content() -> RequirementsDocumentContent:
    return RequirementsDocumentContent(
        project_type="software",
        title="Invoice Automation Project",
        short_description="A system to automate invoice workflows.",
        structure=_software_structure(),
        generated_date="2026-03-17",
    )


def _sample_non_software_content() -> RequirementsDocumentContent:
    return RequirementsDocumentContent(
        project_type="non_software",
        title="Office Relocation Project",
        short_description="Relocate headquarters to new building.",
        structure=_non_software_structure(),
        generated_date="2026-03-17",
    )


def _make_request(
    project_type: str = "software",
    title: str = "Test Project",
    short_description: str = "Test Description",
    structure: list | None = None,
    **overrides: str,
) -> SimpleNamespace:
    if structure is None:
        structure = _software_structure() if project_type == "software" else _non_software_structure()
    return SimpleNamespace(
        project_id=overrides.get("project_id", "test-project-id"),
        project_type=project_type,
        title=title,
        short_description=short_description,
        structure_json=json.dumps(structure),
        generated_date=overrides.get("generated_date", "2026-03-17"),
    )


def _mock_context():
    return MagicMock()


# ── Builder Tests — Software ─────────────────────────────────────


class TestHtmlBuilderSoftware:
    def test_build_html_contains_software_doc_type(self) -> None:
        """T-4.7.01: Software projects generate Software Requirements Document."""
        content = _sample_software_content()
        result = build_html(content)
        assert "Software Requirements Document" in result

    def test_build_html_contains_epic_section(self) -> None:
        """T-4.7.01: Each epic renders as a section."""
        content = _sample_software_content()
        result = build_html(content)
        assert "Epic: User Authentication" in result

    def test_build_html_contains_story_table(self) -> None:
        """T-4.7.01: User story table with correct columns."""
        content = _sample_software_content()
        result = build_html(content)
        assert "story-00" in result
        assert "As a user, I want to log in" in result
        assert "Acceptance Criteria" in result
        assert "Priority" in result

    def test_build_html_contains_priority_badges(self) -> None:
        content = _sample_software_content()
        result = build_html(content)
        assert "priority-high" in result
        assert "priority-medium" in result

    def test_build_html_contains_project_title(self) -> None:
        content = _sample_software_content()
        result = build_html(content)
        assert "Invoice Automation Project" in result

    def test_build_html_contains_generated_date(self) -> None:
        content = _sample_software_content()
        result = build_html(content)
        assert "2026-03-17" in result

    def test_build_html_contains_branding(self) -> None:
        content = _sample_software_content()
        result = build_html(content)
        assert "Commerz Real" in result

    def test_build_html_escapes_special_characters(self) -> None:
        content = RequirementsDocumentContent(
            project_type="software",
            title='Test "Project" <script>',
            short_description="Desc & more",
            structure=[],
            generated_date="2026-03-17",
        )
        result = build_html(content)
        assert "<script>" not in result
        assert "&lt;script&gt;" in result
        assert "&amp; more" in result

    def test_build_html_has_css(self) -> None:
        """PDF-4.02: Gotham font applied in CSS."""
        content = _sample_software_content()
        result = build_html(content)
        assert "font-family" in result
        assert "Gotham" in result


# ── Builder Tests — Non-Software ─────────────────────────────────


class TestHtmlBuilderNonSoftware:
    def test_build_html_contains_project_doc_type(self) -> None:
        """T-4.7.02: Non-software projects generate Project Requirements Document."""
        content = _sample_non_software_content()
        result = build_html(content)
        assert "Project Requirements Document" in result

    def test_build_html_contains_milestone_section(self) -> None:
        content = _sample_non_software_content()
        result = build_html(content)
        assert "Milestone: Phase 1: Planning" in result

    def test_build_html_contains_work_package_table(self) -> None:
        content = _sample_non_software_content()
        result = build_html(content)
        assert "wp-0001-" in result
        assert "Stakeholder Interviews" in result
        assert "Deliverables" in result
        assert "Dependencies" in result

    def test_build_html_contains_deliverables_list(self) -> None:
        content = _sample_non_software_content()
        result = build_html(content)
        assert "Interview notes" in result
        assert "Summary report" in result


# ── parse_structure_json Tests ───────────────────────────────────


class TestParseStructureJson:
    def test_parses_valid_json(self) -> None:
        data = [{"id": "1", "title": "Test"}]
        result = parse_structure_json(json.dumps(data))
        assert result == data

    def test_returns_empty_list_for_empty_string(self) -> None:
        assert parse_structure_json("") == []

    def test_returns_empty_list_for_invalid_json(self) -> None:
        assert parse_structure_json("not json") == []

    def test_returns_empty_list_for_non_list(self) -> None:
        assert parse_structure_json('{"key": "value"}') == []


# ── Renderer Tests ────────────────────────────────────────────────


class TestRenderer:
    def test_render_pdf_returns_bytes(self) -> None:
        """PDF-4.01: WeasyPrint renders A4 portrait PDF."""
        content = _sample_software_content()
        result_html = build_html(content)
        pdf_bytes = render_pdf(result_html)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:5] == b"%PDF-"

    def test_render_pdf_empty_html_raises(self) -> None:
        with pytest.raises(ValueError, match="empty HTML"):
            render_pdf("")

    def test_render_pdf_whitespace_only_raises(self) -> None:
        with pytest.raises(ValueError, match="empty HTML"):
            render_pdf("   \n\t  ")


# ── Servicer Tests ────────────────────────────────────────────────


class TestPdfServicer:
    def test_generate_pdf_software_returns_bytes(self) -> None:
        """PDF-4.03: gRPC service returns bytes for software project."""
        servicer = PdfServicer()
        request = _make_request(project_type="software")
        ctx = _mock_context()
        result = servicer.GeneratePdf(request, context=ctx)

        assert isinstance(result.pdf_data, bytes)
        assert len(result.pdf_data) > 0
        assert result.pdf_data[:5] == b"%PDF-"

    def test_generate_pdf_non_software_returns_bytes(self) -> None:
        """PDF-4.03: gRPC service returns bytes for non-software project."""
        servicer = PdfServicer()
        request = _make_request(project_type="non_software")
        ctx = _mock_context()
        result = servicer.GeneratePdf(request, context=ctx)

        assert isinstance(result.pdf_data, bytes)
        assert len(result.pdf_data) > 0
        assert result.pdf_data[:5] == b"%PDF-"

    def test_generate_pdf_empty_structure(self) -> None:
        """PDF generation works with empty structure."""
        servicer = PdfServicer()
        request = _make_request(structure=[])
        ctx = _mock_context()
        result = servicer.GeneratePdf(request, context=ctx)
        assert len(result.pdf_data) > 0

    def test_generate_pdf_handles_rendering_error(self) -> None:
        servicer = PdfServicer()
        request = _make_request()
        ctx = _mock_context()
        with patch(
            "services.pdf.grpc_server.servicers.pdf_servicer.render_pdf",
            side_effect=ValueError("Rendering kaboom"),
        ):
            result = servicer.GeneratePdf(request, context=ctx)
        assert result.pdf_data == b""
        ctx.set_code.assert_called_once()


# ── CSS Content Test ──────────────────────────────────────────────


class TestCssContent:
    def test_gotham_font_in_css(self) -> None:
        """PDF-4.02: Gotham font applied in CSS."""
        content = _sample_software_content()
        result = build_html(content)
        assert "Gotham" in result
        assert "font-family" in result

    def test_a4_page_size_in_css(self) -> None:
        """PDF-4.01: A4 portrait page size declared."""
        content = _sample_software_content()
        result = build_html(content)
        assert "A4" in result
        assert "portrait" in result
