"""gRPC servicer for the PDF service."""

from __future__ import annotations

import logging
from typing import Any

from services.pdf.generator.builder import BrdContent, build_html
from services.pdf.generator.renderer import (
    TodoMarkerError,
    render_pdf,
    validate_no_todo_markers,
)

logger = logging.getLogger(__name__)


class PdfServicer:
    """gRPC servicer for PDF generation.

    Implements GeneratePdf: accepts BRD content (6 sections + metadata),
    validates for /TODO markers, renders HTML to PDF via WeasyPrint,
    and returns raw PDF bytes.
    """

    def GeneratePdf(self, request: Any, context: Any) -> dict[str, Any]:
        """Generate a PDF from BRD content.

        Request fields:
            section_title, section_short_description, section_current_workflow,
            section_affected_department, section_core_capabilities,
            section_success_criteria, idea_title, generated_date

        Returns dict with pdf_bytes (bytes) or error_message (str).
        """
        idea_title = getattr(request, "idea_title", "") or ""
        logger.info("GeneratePdf request for idea: %s", idea_title)

        section_fields = {
            "section_title": getattr(request, "section_title", "") or "",
            "section_short_description": getattr(request, "section_short_description", "") or "",
            "section_current_workflow": getattr(request, "section_current_workflow", "") or "",
            "section_affected_department": getattr(request, "section_affected_department", "") or "",
            "section_core_capabilities": getattr(request, "section_core_capabilities", "") or "",
            "section_success_criteria": getattr(request, "section_success_criteria", "") or "",
        }

        try:
            validate_no_todo_markers(section_fields)
        except TodoMarkerError as exc:
            logger.warning("PDF generation rejected: %s", exc)
            return {"pdf_bytes": b"", "error_message": str(exc)}

        brd_content = BrdContent(
            **section_fields,
            idea_title=idea_title,
            generated_date=getattr(request, "generated_date", "") or "",
        )

        try:
            html_string = build_html(brd_content)
            pdf_bytes = render_pdf(html_string)
            logger.info(
                "PDF generated successfully for '%s' (%d bytes)",
                idea_title,
                len(pdf_bytes),
            )
            return {"pdf_bytes": pdf_bytes, "error_message": ""}
        except (ValueError, OSError) as exc:
            logger.error("PDF generation failed: %s", exc)
            return {"pdf_bytes": b"", "error_message": str(exc)}
