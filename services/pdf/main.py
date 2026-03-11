"""PDF service entry point — starts gRPC server."""

from __future__ import annotations

import logging
import sys


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    # Add parent path so services.pdf imports work
    sys.path.insert(0, "/app")

    from services.pdf.grpc_server.server import serve

    server = serve()
    logging.getLogger(__name__).info("PDF service started, waiting for termination...")
    server.wait_for_termination()


if __name__ == "__main__":
    main()
