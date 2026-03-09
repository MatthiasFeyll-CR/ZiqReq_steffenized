"""Core service gRPC server setup.

Starts a gRPC server on port 50051 serving CoreService RPCs.
Full wiring with generated proto code will be done in later milestones.
"""

import logging
from concurrent import futures

import grpc
from services.core.grpc_server.servicers.core_servicer import CoreServicer

logger = logging.getLogger(__name__)

DEFAULT_PORT = 50051


def serve(port: int = DEFAULT_PORT) -> grpc.Server:
    """Create and start the Core gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    _servicer = CoreServicer()
    # add_CoreServiceServicer_to_server(servicer, server) — wired in later milestones
    server.add_insecure_port(f"[::]:{port}")
    logger.info("Core gRPC server starting on port %d", port)
    server.start()
    return server


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    s = serve()
    logger.info("Core gRPC server started, waiting for termination...")
    s.wait_for_termination()
