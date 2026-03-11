"""Notification service entry point — starts RabbitMQ event consumers."""

from __future__ import annotations

import json
import logging
import os
import signal
import sys
from typing import Any

import pika
from consumers.ai_events import handle_ai_event
from consumers.chat_events import handle_chat_event
from consumers.collaboration_events import handle_collaboration_event
from consumers.monitoring_events import handle_monitoring_event
from consumers.review_events import handle_review_event
from consumers.similarity_events import handle_similarity_event
from grpc_clients.gateway_client import GatewayClient
from pika.adapters.blocking_connection import BlockingChannel

logger = logging.getLogger(__name__)

BROKER_URL = os.environ.get("BROKER_URL", "amqp://guest:guest@localhost:5672/")
EXCHANGE_NAME = "ziqreq.events"

# Map routing key prefixes to handler functions
_ROUTE_HANDLERS: dict[str, Any] = {
    "notification.collaboration": handle_collaboration_event,
    "notification.review": handle_review_event,
    "notification.chat": handle_chat_event,
    "notification.ai": handle_ai_event,
    "notification.similarity": handle_similarity_event,
    "notification.monitoring": handle_monitoring_event,
}


def _resolve_handler(routing_key: str) -> Any:
    """Find the handler for a given routing key prefix."""
    for prefix, handler in _ROUTE_HANDLERS.items():
        if routing_key.startswith(prefix):
            return handler
    return None


def _on_message(
    gateway_client: GatewayClient,
    channel: BlockingChannel,
    method: pika.spec.Basic.Deliver,
    _properties: pika.spec.BasicProperties,
    body: bytes,
) -> None:
    """Process a single RabbitMQ message."""
    routing_key = method.routing_key or ""
    try:
        event = json.loads(body)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in message: %s", body[:200])
        channel.basic_ack(delivery_tag=method.delivery_tag)
        return

    handler = _resolve_handler(routing_key)
    if handler is None:
        logger.warning("No handler for routing key: %s", routing_key)
        channel.basic_ack(delivery_tag=method.delivery_tag)
        return

    try:
        handler(gateway_client, event)
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        logger.exception(
            "Error processing event (routing_key=%s): %s",
            routing_key,
            event,
        )
        # Negative-ack without requeue to avoid infinite loop
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def main() -> None:
    """Connect to RabbitMQ and start consuming notification events."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    gateway_address = os.environ.get("GATEWAY_GRPC_ADDRESS", "localhost:50054")
    gateway_client = GatewayClient(address=gateway_address)

    logger.info("Connecting to RabbitMQ at %s", BROKER_URL)
    params = pika.URLParameters(BROKER_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    # Declare exchange (idempotent)
    channel.exchange_declare(
        exchange=EXCHANGE_NAME,
        exchange_type="topic",
        durable=True,
    )

    # Declare queue for notification service
    queue_name = "notification_service"
    channel.queue_declare(queue=queue_name, durable=True)

    # Bind to all notification routing keys
    binding_keys = [
        "notification.collaboration.*",
        "notification.review.*",
        "notification.chat.*",
        "notification.ai.*",
        "notification.similarity.*",
        "notification.monitoring.*",
    ]
    for key in binding_keys:
        channel.queue_bind(
            exchange=EXCHANGE_NAME,
            queue=queue_name,
            routing_key=key,
        )
        logger.info("Bound queue %s to %s with key %s", queue_name, EXCHANGE_NAME, key)

    # Set prefetch to process one message at a time
    channel.basic_qos(prefetch_count=1)

    # Set up consumer callback
    def on_message_callback(
        ch: BlockingChannel,
        method: pika.spec.Basic.Deliver,
        properties: pika.spec.BasicProperties,
        body: bytes,
    ) -> None:
        _on_message(gateway_client, ch, method, properties, body)

    channel.basic_consume(
        queue=queue_name,
        on_message_callback=on_message_callback,
    )

    # Graceful shutdown on SIGINT/SIGTERM
    def _shutdown(signum: int, _frame: Any) -> None:
        logger.info("Received signal %d, shutting down...", signum)
        channel.stop_consuming()

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    logger.info("Notification service started, waiting for events...")

    try:
        channel.start_consuming()
    finally:
        gateway_client.close()
        connection.close()
        logger.info("Notification service stopped.")


if __name__ == "__main__":
    main()
