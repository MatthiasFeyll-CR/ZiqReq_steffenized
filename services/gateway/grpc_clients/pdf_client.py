"""gRPC client for PDF service.

Provides typed methods for PdfService RPCs.
Full implementations will connect to the gRPC channel in later milestones.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class PdfClient:
    """gRPC client for PDF service."""

    def __init__(self, address: str = "localhost:50053") -> None:
        self.address = address

    def generate_pdf(
        self,
        idea_id: str,
        idea_title: str,
        sections: dict[str, str],
        generated_at: str = "",
    ) -> dict[str, Any]:
        logger.warning("PdfClient.generate_pdf stub called")
        return {"pdf_data": b"", "filename": "placeholder.pdf"}
