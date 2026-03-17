"""gRPC servicer for the PDF service."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

import grpc

from services.pdf.generator.builder import (
    RequirementsDocumentContent,
    build_html,
    parse_structure_json,
)
from services.pdf.generator.renderer import render_pdf


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


class PdfServicer(pdf_pb2_grpc.PdfServiceServicer):
    """gRPC servicer for PDF generation.

    Implements GeneratePdf: accepts requirements document content
    (project_type, title, short_description, structure_json),
    renders type-specific HTML to PDF via WeasyPrint,
    and returns raw PDF bytes.
    """

    def GeneratePdf(self, request: Any, context: Any) -> Any:
        """Generate a PDF from requirements document content."""
        title = request.title or ""
        project_id = request.project_id or ""
        project_type = request.project_type or "software"
        logger.info("GeneratePdf request for project: %s (id=%s, type=%s)", title, project_id, project_type)

        structure = parse_structure_json(request.structure_json)

        doc_content = RequirementsDocumentContent(
            project_type=project_type,
            title=title,
            short_description=request.short_description or "",
            structure=structure,
            generated_date=request.generated_date or "",
        )

        try:
            html_string = build_html(doc_content)
            pdf_bytes = render_pdf(html_string)
            logger.info(
                "PDF generated successfully for '%s' (%d bytes)",
                title,
                len(pdf_bytes),
            )
            filename = f"requirements-{project_id}.pdf" if project_id else "requirements.pdf"
            return pdf_pb2.PdfGenerationResponse(
                pdf_data=pdf_bytes,
                filename=filename,
            )
        except (ValueError, OSError) as exc:
            logger.error("PDF generation failed: %s", exc)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(exc))
            return pdf_pb2.PdfGenerationResponse(pdf_data=b"", filename="")
