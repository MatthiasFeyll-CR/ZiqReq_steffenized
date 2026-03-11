"""Model tier routing (default/cheap/escalated).

Reads admin-configurable deployment names at runtime, falling back to
environment variables when admin params are empty.
"""

from __future__ import annotations

import logging
import os

from grpc_clients.core_client import CoreClient

logger = logging.getLogger(__name__)

_TIER_ENV_FALLBACKS: dict[str, str] = {
    "default": "AZURE_OPENAI_DEFAULT_DEPLOYMENT",
    "cheap": "AZURE_OPENAI_CHEAP_DEPLOYMENT",
    "escalated": "AZURE_OPENAI_ESCALATED_DEPLOYMENT",
}

_TIER_ADMIN_KEYS: dict[str, str] = {
    "default": "default_ai_model",
    "escalated": "escalated_ai_model",
}


def get_deployment(tier: str = "default") -> str:
    """Resolve the Azure OpenAI deployment name for *tier*.

    Resolution order:
      1. Admin parameter (for default/escalated) — allows runtime config.
      2. Environment variable fallback.

    Raises ValueError if no deployment can be resolved.
    """
    admin_key = _TIER_ADMIN_KEYS.get(tier)
    if admin_key:
        value = _get_admin_param(admin_key)
        if value:
            return value

    env_key = _TIER_ENV_FALLBACKS.get(tier)
    if env_key:
        value = os.environ.get(env_key, "")
        if value:
            return value

    raise ValueError(f"No deployment configured for tier '{tier}'")


def _get_admin_param(key: str) -> str:
    """Read a single admin parameter from Core service.

    Returns empty string on any failure so callers fall through to env vars.
    """
    try:
        client = CoreClient()
        result = client.get_admin_parameter(key)
        return result.get("value", "")
    except Exception:
        logger.debug("Could not read admin param %s — falling back to env", key)
        return ""
