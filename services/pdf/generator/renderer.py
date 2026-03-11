"""HTML-to-PDF rendering with WeasyPrint."""

from __future__ import annotations

import logging

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
