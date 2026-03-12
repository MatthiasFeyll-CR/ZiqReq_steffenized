"""RabbitMQ subscriber for AI events.

Connects to the ziqreq.events topic exchange, binds to ai.# routing keys,
and dispatches incoming messages to the AIEventConsumer for processing
(persist via Core gRPC + broadcast via WebSocket).

Run as a standalone background process alongside the gateway:
    python events/rabbitmq_subscriber.py
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path

# Ensure app root is on sys.path so Django imports work
_app_root = str(Path(__file__).resolve().parent.parent)
if _app_root not in sys.path:
    sys.path.insert(0, _app_root)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gateway.settings.development")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

import django  # noqa: E402

django.setup()

import pika  # noqa: E402

from events.consumers import AIEventConsumer  # noqa: E402

logger = logging.getLogger(__name__)

BROKER_URL = os.environ.get("BROKER_URL", "amqp://guest:guest@localhost:5672/")
EXCHANGE_NAME = "ziqreq.events"
QUEUE_NAME = "gateway.ai_events"
BINDING_KEYS = [
    "ai.chat_response.ready",
    "ai.reaction.ready",
    "ai.title.updated",
    "ai.processing.complete",
    "ai.brd.ready",
]

RECONNECT_DELAY = 5  # seconds


def _on_message(consumer: AIEventConsumer, ch, method, properties, body):
    """Handle a single message from RabbitMQ."""
    try:
        event = json.loads(body)
        logger.info(
            "Received AI event: type=%s, id=%s",
            event.get("event_type"),
            event.get("event_id"),
        )
        asyncio.run(consumer.process_event(event))
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        logger.exception("Failed to process AI event, nacking")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def run():
    """Connect to RabbitMQ and start consuming AI events."""
    consumer = AIEventConsumer()
    consumer.start()

    while True:
        try:
            logger.info("Connecting to RabbitMQ at %s", BROKER_URL)
            params = pika.URLParameters(BROKER_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()

            channel.exchange_declare(
                exchange=EXCHANGE_NAME,
                exchange_type="topic",
                durable=True,
            )

            channel.queue_declare(queue=QUEUE_NAME, durable=True)

            for key in BINDING_KEYS:
                channel.queue_bind(
                    exchange=EXCHANGE_NAME,
                    queue=QUEUE_NAME,
                    routing_key=key,
                )

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(
                queue=QUEUE_NAME,
                on_message_callback=lambda ch, method, props, body: _on_message(
                    consumer, ch, method, props, body
                ),
            )

            logger.info(
                "AI event subscriber started, listening on %s",
                ", ".join(BINDING_KEYS),
            )
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError:
            logger.warning(
                "RabbitMQ connection lost, reconnecting in %ds...",
                RECONNECT_DELAY,
            )
            time.sleep(RECONNECT_DELAY)
        except KeyboardInterrupt:
            logger.info("AI event subscriber shutting down")
            break
        except Exception:
            logger.exception(
                "Unexpected error in AI event subscriber, reconnecting in %ds...",
                RECONNECT_DELAY,
            )
            time.sleep(RECONNECT_DELAY)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    run()
