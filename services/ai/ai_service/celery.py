"""Celery application for the AI service.

Uses RabbitMQ as the message broker (same instance used for event publishing).
"""

from __future__ import annotations

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_service.settings.base")

app = Celery("ai_service")

app.config_from_object({
    "broker_url": os.environ.get("BROKER_URL", "amqp://guest:guest@localhost:5672/"),
    "result_backend": None,
    "task_serializer": "json",
    "accept_content": ["json"],
    "task_always_eager": os.environ.get("CELERY_ALWAYS_EAGER", "false").lower() == "true",
})

app.autodiscover_tasks(["tasks"])
