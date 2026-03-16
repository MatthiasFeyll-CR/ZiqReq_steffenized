import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "insecure-dev-key-change-me")

DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "apps.projects",
    "apps.chat",
    "apps.brd",
    "apps.review",
    "apps.collaboration",
    "apps.admin_config",
    "apps.monitoring",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "ziqreq"),
        "USER": os.environ.get("DB_USER", "ziqreq"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "ziqreq"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

USE_TZ = True
TIME_ZONE = "UTC"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ROOT_URLCONF = "core.urls"

# Celery
CELERY_BROKER_URL = os.environ.get("BROKER_URL", "amqp://guest:guest@localhost:5672/")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
CELERY_BEAT_SCHEDULE = {
"health-check-sweep": {
        "task": "monitoring.health_check_task",
        "schedule": 60.0,  # default: every 60 seconds (configurable via admin_parameters)
    },
    "soft-delete-cleanup": {
        "task": "projects.soft_delete_cleanup",
        "schedule": 86400.0,  # daily
    },
}

# gRPC addresses
GATEWAY_GRPC_ADDRESS = os.environ.get("GATEWAY_GRPC_ADDRESS", "localhost:50054")
AI_GRPC_ADDRESS = os.environ.get("AI_GRPC_ADDRESS", "localhost:50052")
PDF_GRPC_ADDRESS = os.environ.get("PDF_GRPC_ADDRESS", "localhost:50053")

# Message broker
BROKER_URL = os.environ.get("BROKER_URL", "amqp://guest:guest@localhost:5672/")
