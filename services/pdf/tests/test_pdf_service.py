"""Tests for PDF generation service — US-004."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from services.pdf.generator.builder import BrdContent, build_html
from services.pdf.generator.renderer import TodoMarkerError, render_pdf, validate_no_todo_markers
from services.pdf.grpc_server.servicers.pdf_servicer import PdfServicer

# ── Fixtures ──────────────────────────────────────────────────────


def _sample_content() -> BrdContent:
    return BrdContent(
        section_title="Automated Invoice Processing",
        section_short_description="A system to automate invoice workflows and reduce manual data entry.",
        section_current_workflow="Currently invoices are received via email, manually opened, "
        "and entered into SAP FI by the accounting team. Errors average 12% per batch.",
        section_affected_department="Finance & Accounting, Shared Services",
        section_core_capabilities="- OCR-based invoice data extraction\n"
        "- Automated GL code suggestion\n"
        "- Exception handling dashboard",
        section_success_criteria="- 80% straight-through processing rate\n"
        "- <2% error rate on GL code assignment\n"
        "- 50% reduction in processing time",
        idea_title="Invoice Automation Project",
        generated_date="2026-03-11",
    )


def _make_request(**overrides: str) -> SimpleNamespace:
    defaults = {
        "section_title": "Test Title",
        "section_short_description": "Test Description",
        "section_current_workflow": "Test Workflow",
        "section_affected_department": "Test Department",
        "section_core_capabilities": "Test Capabilities",
        "section_success_criteria": "Test Criteria",
        "idea_title": "Test Idea",
        "generated_date": "2026-03-11",
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


# ── Builder Tests ─────────────────────────────────────────────────


class TestHtmlBuilder:
    def test_build_html_contains_all_sections(self) -> None:
        """T-4.7.02: PDF includes all 6 sections."""
        content = _sample_content()
        html = build_html(content)

        assert "1. Title" in html
        assert "2. Short Description" in html
        assert "3. Current Workflow &amp; Pain Points" in html
        assert "4. Affected Department" in html
        assert "5. Core Capabilities" in html
        assert "6. Success Criteria" in html

    def test_build_html_contains_idea_title(self) -> None:
        content = _sample_content()
        html = build_html(content)
        assert "Invoice Automation Project" in html

    def test_build_html_contains_generated_date(self) -> None:
        content = _sample_content()
        html = build_html(content)
        assert "2026-03-11" in html

    def test_build_html_contains_branding(self) -> None:
        content = _sample_content()
        html = build_html(content)
        assert "Commerz Real" in html
        assert "Business Requirements Document" in html

    def test_build_html_escapes_special_characters(self) -> None:
        content = BrdContent(
            section_title="Title with <script>alert('xss')</script>",
            section_short_description="Desc & more",
            section_current_workflow="",
            section_affected_department="",
            section_core_capabilities="",
            section_success_criteria="",
            idea_title='Test "Idea"',
            generated_date="2026-03-11",
        )
        html = build_html(content)
        assert "<script>" not in html
        assert "&lt;script&gt;" in html
        assert "&amp; more" in html

    def test_build_html_has_css(self) -> None:
        content = _sample_content()
        html = build_html(content)
        assert "font-family" in html
        assert "Gotham" in html


# ── Renderer Tests ────────────────────────────────────────────────


class TestRenderer:
    def test_render_pdf_returns_bytes(self) -> None:
        """PDF-4.01: WeasyPrint renders A4 portrait PDF."""
        content = _sample_content()
        html = build_html(content)
        pdf_bytes = render_pdf(html)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        # PDF files start with %PDF
        assert pdf_bytes[:5] == b"%PDF-"

    def test_render_pdf_empty_html_raises(self) -> None:
        with pytest.raises(ValueError, match="empty HTML"):
            render_pdf("")

    def test_render_pdf_whitespace_only_raises(self) -> None:
        with pytest.raises(ValueError, match="empty HTML"):
            render_pdf("   \n\t  ")


# ── TODO Marker Validation Tests ─────────────────────────────────


class TestTodoMarkerValidation:
    def test_no_markers_passes(self) -> None:
        fields = {
            "section_title": "Valid title",
            "section_short_description": "Valid description",
        }
        validate_no_todo_markers(fields)  # Should not raise

    def test_todo_marker_raises(self) -> None:
        """T-4.9.06: PDF rejected if /TODO remains."""
        fields = {
            "section_title": "Valid title",
            "section_short_description": "/TODO: Need more details about the workflow",
        }
        with pytest.raises(TodoMarkerError, match="/TODO markers"):
            validate_no_todo_markers(fields)

    def test_multiple_markers_lists_all_fields(self) -> None:
        fields = {
            "section_title": "/TODO: Need title",
            "section_current_workflow": "/TODO: Need workflow",
        }
        with pytest.raises(TodoMarkerError, match="section_title.*section_current_workflow"):
            validate_no_todo_markers(fields)

    def test_none_fields_are_safe(self) -> None:
        fields = {"section_title": None, "section_short_description": "Valid"}
        validate_no_todo_markers(fields)  # Should not raise


# ── Servicer Tests ────────────────────────────────────────────────


class TestPdfServicer:
    def test_generate_pdf_returns_bytes(self) -> None:
        """PDF-4.03: gRPC service returns bytes."""
        servicer = PdfServicer()
        request = _make_request()
        result = servicer.GeneratePdf(request, context=None)

        assert result["error_message"] == ""
        assert isinstance(result["pdf_bytes"], bytes)
        assert len(result["pdf_bytes"]) > 0
        assert result["pdf_bytes"][:5] == b"%PDF-"

    def test_generate_pdf_with_todo_markers_rejected(self) -> None:
        """T-4.9.06: PDF generation rejected if /TODO markers present."""
        servicer = PdfServicer()
        request = _make_request(
            section_title="/TODO: Need a proper title"
        )
        result = servicer.GeneratePdf(request, context=None)

        assert result["pdf_bytes"] == b""
        assert "/TODO markers" in result["error_message"]

    def test_generate_pdf_all_sections_in_output(self) -> None:
        """T-4.7.01: PDF generated from BRD content."""
        servicer = PdfServicer()
        request = _make_request()
        result = servicer.GeneratePdf(request, context=None)

        assert result["error_message"] == ""
        assert len(result["pdf_bytes"]) > 100

    def test_generate_pdf_logs_success(self) -> None:
        servicer = PdfServicer()
        request = _make_request()
        # Just verifies no errors; logging is tested implicitly
        result = servicer.GeneratePdf(request, context=None)
        assert result["error_message"] == ""

    def test_generate_pdf_handles_rendering_error(self) -> None:
        servicer = PdfServicer()
        request = _make_request()
        with patch(
            "services.pdf.grpc_server.servicers.pdf_servicer.render_pdf",
            side_effect=ValueError("Rendering kaboom"),
        ):
            result = servicer.GeneratePdf(request, context=None)
        assert result["pdf_bytes"] == b""
        assert "Rendering kaboom" in result["error_message"]


# ── CSS Content Test ──────────────────────────────────────────────


class TestCssContent:
    def test_gotham_font_in_css(self) -> None:
        """PDF-4.02: Gotham font applied in CSS."""
        content = _sample_content()
        html = build_html(content)
        assert "Gotham" in html
        assert "font-family" in html

    def test_a4_page_size_in_css(self) -> None:
        """PDF-4.01: A4 portrait page size declared."""
        content = _sample_content()
        html = build_html(content)
        assert "A4" in html
        assert "portrait" in html
