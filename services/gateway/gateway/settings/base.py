import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "insecure-dev-key-change-me")

DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "rest_framework",
    "channels",
    "apps.authentication",
    "apps.notifications",
    "apps.monitoring",
    "apps.admin_config",
    "apps.ideas",
    "apps.chat",
    "apps.board",
    "apps.collaboration",
    "apps.brd",
    "apps.review",
    "apps.similarity",
    "apps.admin_ai_context",
    "apps.websocket",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "middleware.error_handling.ErrorHandlingMiddleware",
]

ROOT_URLCONF = "gateway.urls"

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

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get("REDIS_URL", "redis://localhost:6379/0")],
        },
    }
}

ASGI_APPLICATION = "gateway.asgi.application"

USE_TZ = True
TIME_ZONE = "UTC"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# gRPC service addresses
CORE_GRPC_ADDRESS = os.environ.get("CORE_GRPC_ADDRESS", "localhost:50051")
AI_GRPC_ADDRESS = os.environ.get("AI_GRPC_ADDRESS", "localhost:50052")
PDF_GRPC_ADDRESS = os.environ.get("PDF_GRPC_ADDRESS", "localhost:50053")

# Message broker
BROKER_URL = os.environ.get("BROKER_URL", "amqp://guest:guest@localhost:5672/")
