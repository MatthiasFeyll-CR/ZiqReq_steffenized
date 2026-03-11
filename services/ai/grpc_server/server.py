"""AI service gRPC server setup.

Starts a gRPC server on port 50052 serving AiService RPCs.
Full wiring with generated proto code will be done in later milestones.
"""

import logging
from concurrent import futures

import grpc
try:
    from services.ai.grpc_server.servicers.context_servicer import AiContextServicer
    from services.ai.grpc_server.servicers.processing_servicer import AiProcessingServicer
except ModuleNotFoundError:
    from grpc_server.servicers.context_servicer import AiContextServicer
    from grpc_server.servicers.processing_servicer import AiProcessingServicer

logger = logging.getLogger(__name__)

DEFAULT_PORT = 50052


def serve(port: int = DEFAULT_PORT) -> grpc.Server:
    """Create and start the AI gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    _processing = AiProcessingServicer()
    _context = AiContextServicer()
    # add_AiServiceServicer_to_server(servicer, server) — wired in later milestones
    server.add_insecure_port(f"[::]:{port}")
    logger.info("AI gRPC server starting on port %d", port)
    server.start()
    return server


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    s = serve()
    logger.info("AI gRPC server started, waiting for termination...")
    s.wait_for_termination()
