"""Monitoring dashboard aggregate stats — US-003."""

import logging

from django.db.models import Count

from apps.authentication.models import User
from apps.ideas.models import Idea

logger = logging.getLogger(__name__)

# Redis key patterns for health checks (set by Celery periodic task in US-006)
HEALTH_KEY_PREFIX = "monitoring:health:"
HEALTH_SERVICES = ["gateway", "ai", "pdf", "notification", "database", "redis", "broker", "dlq"]

# Redis key patterns for AI processing stats
AI_STATS_PREFIX = "monitoring:ai:"


def _get_presence_registry() -> dict:
    """Import and return the WebSocket presence registry."""
    try:
        from apps.websocket.consumers import _presence_registry
        return _presence_registry
    except ImportError:
        logger.warning("WebSocket consumers not available; returning empty presence")
        return {}


def get_active_connections() -> int:
    """Count total active WebSocket connections across all groups."""
    registry = _get_presence_registry()
    # Each group -> {user_id: set(channel_names)}
    # Count unique channel names across all groups
    all_channels: set[str] = set()
    for user_channels in registry.values():
        for channels in user_channels.values():
            all_channels.update(channels)
    return len(all_channels)


def get_online_users() -> int:
    """Count unique users with at least one active WebSocket connection."""
    registry = _get_presence_registry()
    all_users: set[str] = set()
    for user_channels in registry.values():
        all_users.update(user_channels.keys())
    return len(all_users)


def get_ideas_by_state() -> dict[str, int]:
    """Count ideas grouped by state."""
    counts = (
        Idea.objects.filter(deleted_at__isnull=True)
        .values("state")
        .annotate(count=Count("id"))
    )
    result = {"open": 0, "in_review": 0, "accepted": 0, "dropped": 0, "rejected": 0}
    for row in counts:
        if row["state"] in result:
            result[row["state"]] = row["count"]
    return result


def get_active_users() -> int:
    """Count total non-deleted users."""
    return User.objects.count()


def get_ai_processing_stats() -> dict[str, int]:
    """Get AI processing stats from Redis. Returns defaults if Redis unavailable."""
    try:
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection("default")
        request_count = int(redis_conn.get(f"{AI_STATS_PREFIX}request_count") or 0)
        success_count = int(redis_conn.get(f"{AI_STATS_PREFIX}success_count") or 0)
        failure_count = int(redis_conn.get(f"{AI_STATS_PREFIX}failure_count") or 0)
        return {
            "request_count": request_count,
            "success_count": success_count,
            "failure_count": failure_count,
        }
    except Exception:
        logger.warning("Redis unavailable for AI stats; returning zeros")
        return {"request_count": 0, "success_count": 0, "failure_count": 0}


def get_system_health() -> dict[str, dict]:
    """Get system health from Redis. Returns 'unknown' status if no data."""
    default_entry = {"status": "unknown", "last_check": None}
    try:
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection("default")
        result = {}
        for service in HEALTH_SERVICES:
            raw_status = redis_conn.get(f"{HEALTH_KEY_PREFIX}{service}:status")
            raw_ts = redis_conn.get(f"{HEALTH_KEY_PREFIX}{service}:last_check")
            if raw_status:
                status_str = raw_status.decode() if isinstance(raw_status, bytes) else str(raw_status)
                ts_str = raw_ts.decode() if isinstance(raw_ts, bytes) and raw_ts else None
                result[service] = {"status": status_str, "last_check": ts_str}
            else:
                result[service] = dict(default_entry)
        return result
    except Exception:
        logger.warning("Redis unavailable for health checks; returning unknowns")
        return {svc: dict(default_entry) for svc in HEALTH_SERVICES}


def get_dashboard_stats() -> dict:
    """Aggregate all monitoring dashboard stats."""
    return {
        "active_connections": get_active_connections(),
        "ideas_by_state": get_ideas_by_state(),
        "active_users": get_active_users(),
        "online_users": get_online_users(),
        "ai_processing": get_ai_processing_stats(),
        "system_health": get_system_health(),
    }
