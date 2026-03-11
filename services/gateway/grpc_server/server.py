"""Gateway gRPC server setup.

Starts a gRPC server on port 50054 serving GatewayService RPCs
(notification service callbacks).
"""

import logging
import os
import sys
from concurrent import futures
from pathlib import Path

import django
import grpc

# Ensure proto directory is on sys.path for generated imports
_proto_dir = str(Path(__file__).resolve().parents[2] / ".." / ".." / "proto")
_proto_dir = str(Path(_proto_dir).resolve())
if _proto_dir not in sys.path:
    sys.path.insert(0, _proto_dir)

import gateway_pb2_grpc  # noqa: E402
from services.gateway.grpc_server.servicers.gateway_servicer import (  # noqa: E402
    GatewayServicer,
)

logger = logging.getLogger(__name__)

DEFAULT_PORT = 50054


def serve(port: int = DEFAULT_PORT) -> grpc.Server:
    """Create and start the Gateway gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = GatewayServicer()
    gateway_pb2_grpc.add_GatewayServiceServicer_to_server(servicer, server)
    server.add_insecure_port(f"[::]:{port}")
    logger.info("Gateway gRPC server starting on port %d", port)
    server.start()
    return server


if __name__ == "__main__":
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "gateway.settings.development"
    )
    django.setup()
    logging.basicConfig(level=logging.INFO)
    s = serve()
    logger.info("Gateway gRPC server started, waiting for termination...")
    s.wait_for_termination()
