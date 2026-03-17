"""gRPC client for PDF service."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any

import grpc


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


class PdfClient:
    """gRPC client for PDF service."""

    def __init__(self, address: str | None = None) -> None:
        self.address = address or os.environ.get("PDF_GRPC_ADDRESS", "localhost:50053")
        self._channel: grpc.Channel | None = None
        self._stub: pdf_pb2_grpc.PdfServiceStub | None = None

    def _ensure_channel(self) -> pdf_pb2_grpc.PdfServiceStub:
        if self._stub is None:
            self._channel = grpc.insecure_channel(self.address)
            self._stub = pdf_pb2_grpc.PdfServiceStub(self._channel)
        return self._stub

    def generate_pdf(
        self,
        project_id: str,
        project_type: str = "software",
        title: str = "",
        short_description: str = "",
        structure_json: str = "[]",
        generated_date: str = "",
    ) -> dict[str, Any]:
        stub = self._ensure_channel()
        request = pdf_pb2.PdfGenerationRequest(
            project_id=project_id,
            project_type=project_type,
            title=title,
            short_description=short_description,
            structure_json=structure_json,
            generated_date=generated_date,
        )
        response = stub.GeneratePdf(request)
        logger.info(
            "PDF generated for project %s: %d bytes",
            project_id,
            len(response.pdf_data),
        )
        return {"pdf_data": response.pdf_data, "filename": response.filename}

    def close(self) -> None:
        if self._channel is not None:
            self._channel.close()
            self._channel = None
            self._stub = None
