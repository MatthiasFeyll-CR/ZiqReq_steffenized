"""AI service entry point — starts gRPC server + event consumers with Django ORM initialized."""

import logging
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_service.settings.development")
django.setup()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    from grpc_server.server import serve

    server = serve()
    logging.getLogger(__name__).info("AI service started, waiting for termination...")
    server.wait_for_termination()


if __name__ == "__main__":
    main()
