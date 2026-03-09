"""Gateway gRPC server setup.

Starts a gRPC server on port 50054 serving GatewayService RPCs
(notification service callbacks).
Full wiring with generated proto code will be done in later milestones.
"""

import logging
from concurrent import futures

import grpc
from services.gateway.grpc_server.servicers.gateway_servicer import (
    GatewayServicer,
)

logger = logging.getLogger(__name__)

DEFAULT_PORT = 50054


def serve(port: int = DEFAULT_PORT) -> grpc.Server:
    """Create and start the Gateway gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    _servicer = GatewayServicer()
    # add_GatewayServiceServicer_to_server(servicer, server) — wired in later milestones
    server.add_insecure_port(f"[::]:{port}")
    logger.info("Gateway gRPC server starting on port %d", port)
    server.start()
    return server


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    s = serve()
    logger.info("Gateway gRPC server started, waiting for termination...")
    s.wait_for_termination()
