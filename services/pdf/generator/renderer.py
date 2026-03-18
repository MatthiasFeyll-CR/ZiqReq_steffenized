"""HTML-to-PDF rendering with WeasyPrint and attachment merging."""

from __future__ import annotations

import logging

import fitz  # PyMuPDF
from weasyprint import HTML

logger = logging.getLogger(__name__)


_TODO_MARKER = "/TODO"


class TodoMarkerError(Exception):
    """Raised when BRD content contains /TODO markers."""


def validate_no_todo_markers(content_fields: dict[str, str | None]) -> None:
    """Check that no section contains /TODO markers.

    Raises TodoMarkerError if any /TODO markers are found.
    """
    flagged: list[str] = []
    for field_name, value in content_fields.items():
        if value and _TODO_MARKER in value:
            flagged.append(field_name)

    if flagged:
        sections = ", ".join(flagged)
        raise TodoMarkerError(
            f"Cannot generate PDF: sections contain /TODO markers ({sections}). "
            "Please complete or disable information gaps."
        )


def render_pdf(html_string: str) -> bytes:
    """Convert an HTML string to PDF bytes using WeasyPrint.

    Returns raw PDF bytes (not base64 encoded).
    Raises ValueError if HTML is empty or rendering fails.
    """
    if not html_string or not html_string.strip():
        raise ValueError("Cannot render PDF from empty HTML")

    try:
        pdf_bytes: bytes = HTML(string=html_string).write_pdf()
        logger.info("PDF rendered successfully (%d bytes)", len(pdf_bytes))
        return pdf_bytes
    except Exception as exc:
        logger.error("PDF rendering failed: %s", exc)
        raise ValueError(f"PDF rendering failed: {exc}") from exc


def merge_attachments(brd_pdf_bytes: bytes, attachments: list[dict]) -> bytes:
    """Merge attachment files into the BRD PDF.

    Each attachment dict has: filename, content_type, file_data (bytes).
    PDFs are appended page-by-page. Images are inserted as full pages.
    Returns the merged PDF bytes, or the original on failure.
    """
    if not attachments:
        return brd_pdf_bytes

    try:
        doc = fitz.open(stream=brd_pdf_bytes, filetype="pdf")

        for att in attachments:
            try:
                content_type = att.get("content_type", "")
                file_data = att.get("file_data", b"")
                if not file_data:
                    continue

                if content_type == "application/pdf":
                    att_doc = fitz.open(stream=file_data, filetype="pdf")
                    doc.insert_pdf(att_doc)
                    att_doc.close()
                elif content_type.startswith("image/"):
                    page = doc.new_page(width=595, height=842)
                    img_rect = fitz.Rect(36, 36, 559, 806)
                    page.insert_image(img_rect, stream=file_data)
            except Exception as exc:
                logger.warning("Failed to merge attachment '%s': %s", att.get("filename", "unknown"), exc)

        output = doc.tobytes()
        doc.close()
        logger.info("Merged %d attachments into PDF (%d bytes)", len(attachments), len(output))
        return output
    except Exception as exc:
        logger.error("Attachment merge failed, returning unmerged PDF: %s", exc)
        return brd_pdf_bytes
