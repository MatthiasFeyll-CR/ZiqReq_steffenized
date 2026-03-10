import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "insecure-dev-key-change-me")

DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "apps.context",
    "apps.embedding",
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

# Azure OpenAI
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01")
AZURE_OPENAI_DEFAULT_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEFAULT_DEPLOYMENT", "")
AZURE_OPENAI_CHEAP_DEPLOYMENT = os.environ.get("AZURE_OPENAI_CHEAP_DEPLOYMENT", "")
AZURE_OPENAI_ESCALATED_DEPLOYMENT = os.environ.get("AZURE_OPENAI_ESCALATED_DEPLOYMENT", "")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "")

# Mock mode for E2E testing
AI_MOCK_MODE = os.environ.get("AI_MOCK_MODE", "false").lower() == "true"

# gRPC
CORE_GRPC_ADDRESS = os.environ.get("CORE_GRPC_ADDRESS", "localhost:50051")

# Message broker
BROKER_URL = os.environ.get("BROKER_URL", "amqp://guest:guest@localhost:5672/")

# Admin parameter defaults (used when Core service is unreachable)
ADMIN_PARAM_DEFAULTS: dict[str, str] = {
    "default_ai_model": AZURE_OPENAI_DEFAULT_DEPLOYMENT,
    "escalated_ai_model": AZURE_OPENAI_ESCALATED_DEPLOYMENT,
    "ai_processing_timeout": "60",
    "recent_message_count": "20",
    "context_compression_threshold": "60",
}

# Validate required Azure OpenAI env vars (warn at import time, skip in mock mode)
if not AI_MOCK_MODE:
    import logging as _logging

    _logger = _logging.getLogger("ai_service.settings")
    _missing = [
        v
        for v in ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY")
        if not os.environ.get(v)
    ]
    if _missing:
        _logger.warning(
            "Missing required Azure OpenAI env vars: %s. "
            "AI features will fail until these are set.",
            ", ".join(_missing),
        )
