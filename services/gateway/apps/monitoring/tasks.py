"""Celery periodic task: service health checks and alerting."""

from __future__ import annotations

import json
import logging
import os

import redis as redis_lib
from celery import shared_task

logger = logging.getLogger(__name__)

REDIS_KEY_PREFIX = "monitoring:health:"


def _store_result_in_redis(result: dict, ttl: int) -> None:
    """Store a health check result in Redis with TTL."""
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    r = redis_lib.from_url(redis_url, socket_timeout=5)
    key = f"{REDIS_KEY_PREFIX}{result['service_name']}"
    r.setex(key, ttl, json.dumps(result))


@shared_task(name="monitoring.health_check_task")
def health_check_task() -> dict:
    """Run all health checks, store results in Redis, and alert on failures.

    Reads configurable parameters:
    - health_check_interval: seconds between checks (default 60)
    - dlq_alert_threshold: DLQ depth that triggers alert (default 10)
    """
    from apps.admin_config.services import get_parameter
    from apps.monitoring.health_checks import run_all_checks

    health_check_interval = get_parameter("health_check_interval", default=60, cast=int)
    dlq_alert_threshold = get_parameter("dlq_alert_threshold", default=10, cast=int)
    ttl = health_check_interval * 2

    results = run_all_checks(dlq_alert_threshold=dlq_alert_threshold)

    alerts = []
    for result in results:
        result_dict = result.to_dict()

        # Store in Redis
        try:
            _store_result_in_redis(result_dict, ttl)
        except Exception:
            logger.exception("Failed to store health check result for %s in Redis", result.service_name)

        logger.info(
            "Health check: %s = %s%s",
            result.service_name,
            result.status,
            f" ({result.details})" if result.details else "",
        )

        if result.status == "unhealthy":
            alerts.append({
                "alert_type": "service_unhealthy",
                "service_name": result.service_name,
                "details": result.details,
                "timestamp": result.last_check,
            })

    # Publish alerts
    if alerts:
        from events.publisher import publish_event

        for alert in alerts:
            try:
                publish_event(event_type="monitoring.alert", payload=alert)
                logger.warning(
                    "Alert published: %s - %s: %s",
                    alert["alert_type"],
                    alert["service_name"],
                    alert["details"],
                )
            except Exception:
                logger.exception("Failed to publish monitoring alert for %s", alert["service_name"])

    summary = {
        "total_checks": len(results),
        "healthy": sum(1 for r in results if r.status == "healthy"),
        "unhealthy": sum(1 for r in results if r.status == "unhealthy"),
        "alerts_published": len(alerts),
    }
    logger.info("Health check sweep complete: %s", summary)
    return summary
