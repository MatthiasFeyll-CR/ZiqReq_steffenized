"""gRPC servicer for the PDF service."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

import grpc

from services.pdf.generator.builder import BrdContent, build_html
from services.pdf.generator.renderer import (
    TodoMarkerError,
    render_pdf,
    validate_no_todo_markers,
)


# Ensure proto directory is on sys.path for generated imports
def _find_proto_dir() -> str:
    current = Path(__file__).resolve().parent
    while current != current.parent:
        candidate = current / "proto"
        if candidate.is_dir():
            return str(candidate)
        current = current.parent
    return ""

_proto_dir = _find_proto_dir()
if _proto_dir and _proto_dir not in sys.path:
    sys.path.insert(0, _proto_dir)

import pdf_pb2  # noqa: E402
import pdf_pb2_grpc  # noqa: E402

logger = logging.getLogger(__name__)

# Section key mapping: proto sections map keys → builder field names
_SECTION_KEY_TO_FIELD = {
    "title": "section_title",
    "short_description": "section_short_description",
    "current_workflow": "section_current_workflow",
    "affected_department": "section_affected_department",
    "core_capabilities": "section_core_capabilities",
    "success_criteria": "section_success_criteria",
}


class PdfServicer(pdf_pb2_grpc.PdfServiceServicer):
    """gRPC servicer for PDF generation.

    Implements GeneratePdf: accepts BRD content (6 sections + metadata),
    validates for /TODO markers, renders HTML to PDF via WeasyPrint,
    and returns raw PDF bytes.
    """

    def GeneratePdf(self, request: Any, context: Any) -> Any:
        """Generate a PDF from BRD content."""
        project_title = request.project_title or ""
        project_id = request.project_id or ""
        logger.info("GeneratePdf request for project: %s (id=%s)", project_title, project_id)

        # Map sections from proto map to builder fields
        sections = dict(request.sections)
        section_fields = {}
        for key, field in _SECTION_KEY_TO_FIELD.items():
            section_fields[field] = sections.get(key, "")

        try:
            validate_no_todo_markers(section_fields)
        except TodoMarkerError as exc:
            logger.warning("PDF generation rejected: %s", exc)
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(exc))
            return pdf_pb2.PdfGenerationResponse(pdf_data=b"", filename="")

        brd_content = BrdContent(
            **section_fields,
            project_title=project_title,
            generated_date=request.generated_at or "",
        )

        try:
            html_string = build_html(brd_content)
            pdf_bytes = render_pdf(html_string)
            logger.info(
                "PDF generated successfully for '%s' (%d bytes)",
                project_title,
                len(pdf_bytes),
            )
            filename = f"brd-{project_id}.pdf" if project_id else "brd.pdf"
            return pdf_pb2.PdfGenerationResponse(
                pdf_data=pdf_bytes,
                filename=filename,
            )
        except (ValueError, OSError) as exc:
            logger.error("PDF generation failed: %s", exc)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(exc))
            return pdf_pb2.PdfGenerationResponse(pdf_data=b"", filename="")
