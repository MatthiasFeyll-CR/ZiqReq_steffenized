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

# Ensure the app root is on sys.path so "grpc_server" package is importable
_app_root = str(Path(__file__).resolve().parent.parent)
if _app_root not in sys.path:
    sys.path.insert(0, _app_root)

# Ensure proto directory is on sys.path for generated imports
def _find_proto_dir() -> str:
    """Search upward from this file for a 'proto' directory."""
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

import gateway_pb2_grpc  # noqa: E402

try:
    from services.gateway.grpc_server.servicers.gateway_servicer import GatewayServicer  # noqa: E402
except ModuleNotFoundError:
    from grpc_server.servicers.gateway_servicer import GatewayServicer  # noqa: E402

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
