"""PDF service gRPC server setup.

Starts a gRPC server on port 50053 serving PdfService RPCs.
"""

import logging
import sys
from concurrent import futures
from pathlib import Path

import grpc

from services.pdf.grpc_server.servicers.pdf_servicer import PdfServicer

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

import pdf_pb2_grpc  # noqa: E402

logger = logging.getLogger(__name__)

DEFAULT_PORT = 50053


def serve(port: int = DEFAULT_PORT) -> grpc.Server:
    """Create and start the PDF gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = PdfServicer()
    pdf_pb2_grpc.add_PdfServiceServicer_to_server(servicer, server)
    server.add_insecure_port(f"[::]:{port}")
    logger.info("PDF gRPC server starting on port %d", port)
    server.start()
    return server


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    s = serve()
    logger.info("PDF gRPC server started, waiting for termination...")
    s.wait_for_termination()
