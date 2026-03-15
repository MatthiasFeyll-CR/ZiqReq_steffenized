"""Core service gRPC server setup.

Starts a gRPC server on port 50051. The CoreServicer stub has been removed
because all services access the shared PostgreSQL database directly.
The server process is kept for docker-compose compatibility.
"""

import logging
from concurrent import futures

import grpc

logger = logging.getLogger(__name__)

DEFAULT_PORT = 50051


def serve(port: int = DEFAULT_PORT) -> grpc.Server:
    """Create and start the Core gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    server.add_insecure_port(f"[::]:{port}")
    logger.info("Core gRPC server starting on port %d (no servicers registered — direct DB access)", port)
    server.start()
    return server


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    s = serve()
    logger.info("Core gRPC server started, waiting for termination...")
    s.wait_for_termination()
