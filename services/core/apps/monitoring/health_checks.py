"""Health check functions for each service/infrastructure component."""

from __future__ import annotations

import base64
import json
import logging
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone

import grpc
import pika
import redis as redis_lib

logger = logging.getLogger(__name__)


@dataclass
class HealthCheckResult:
    service_name: str
    status: str  # "healthy" or "unhealthy"
    last_check: str  # ISO 8601 timestamp
    details: str = ""

    def to_dict(self) -> dict:
        return {
            "service_name": self.service_name,
            "status": self.status,
            "last_check": self.last_check,
            "details": self.details,
        }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def check_gateway_health() -> HealthCheckResult:
    """Check gateway service via HTTP health endpoint."""
    gateway_url = os.environ.get("GATEWAY_HEALTH_URL", "http://localhost:8000/api/health")
    try:
        req = urllib.request.Request(gateway_url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                return HealthCheckResult("gateway", "healthy", _now_iso())
            return HealthCheckResult("gateway", "unhealthy", _now_iso(), f"HTTP {resp.status}")
    except Exception as e:
        return HealthCheckResult("gateway", "unhealthy", _now_iso(), str(e))


def check_grpc_health(service_name: str, address: str) -> HealthCheckResult:
    """Check a gRPC service by attempting to connect."""
    try:
        channel = grpc.insecure_channel(address)
        future = grpc.channel_ready_future(channel)
        future.result(timeout=5)
        channel.close()
        return HealthCheckResult(service_name, "healthy", _now_iso())
    except Exception as e:
        return HealthCheckResult(service_name, "unhealthy", _now_iso(), str(e))


def check_ai_health() -> HealthCheckResult:
    """Check AI gRPC service health."""
    address = os.environ.get("AI_GRPC_ADDRESS", "localhost:50052")
    return check_grpc_health("ai", address)


def check_pdf_health() -> HealthCheckResult:
    """Check PDF gRPC service health."""
    address = os.environ.get("PDF_GRPC_ADDRESS", "localhost:50053")
    return check_grpc_health("pdf", address)


def check_notification_health() -> HealthCheckResult:
    """Check notification consumer heartbeat via Redis key."""
    try:
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        r = redis_lib.from_url(redis_url, socket_timeout=5)
        heartbeat = r.get("notification:heartbeat")
        if heartbeat:
            ts = float(heartbeat)
            age = time.time() - ts
            if age < 120:  # heartbeat within 2 minutes
                return HealthCheckResult("notification", "healthy", _now_iso())
            return HealthCheckResult(
                "notification", "unhealthy", _now_iso(), f"Heartbeat stale ({age:.0f}s old)"
            )
        return HealthCheckResult("notification", "unhealthy", _now_iso(), "No heartbeat found")
    except Exception as e:
        return HealthCheckResult("notification", "unhealthy", _now_iso(), str(e))


def check_database_health() -> HealthCheckResult:
    """Check database connectivity via Django ORM."""
    try:
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return HealthCheckResult("database", "healthy", _now_iso())
    except Exception as e:
        return HealthCheckResult("database", "unhealthy", _now_iso(), str(e))


def check_redis_health() -> HealthCheckResult:
    """Check Redis connectivity via PING."""
    try:
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        r = redis_lib.from_url(redis_url, socket_timeout=5)
        if r.ping():
            return HealthCheckResult("redis", "healthy", _now_iso())
        return HealthCheckResult("redis", "unhealthy", _now_iso(), "PING returned False")
    except Exception as e:
        return HealthCheckResult("redis", "unhealthy", _now_iso(), str(e))


def check_broker_health() -> HealthCheckResult:
    """Check message broker (RabbitMQ) connectivity."""
    try:
        broker_url = os.environ.get("BROKER_URL", "amqp://guest:guest@localhost:5672/")
        params = pika.URLParameters(broker_url)
        params.socket_timeout = 5
        connection = pika.BlockingConnection(params)
        connection.close()
        return HealthCheckResult("broker", "healthy", _now_iso())
    except Exception as e:
        return HealthCheckResult("broker", "unhealthy", _now_iso(), str(e))


def check_dlq_health(alert_threshold: int = 10) -> HealthCheckResult:
    """Check DLQ message counts via RabbitMQ management API."""
    try:
        mgmt_url = os.environ.get(
            "RABBITMQ_MGMT_URL", "http://localhost:15672"
        )
        broker_url = os.environ.get("BROKER_URL", "amqp://guest:guest@localhost:5672/")
        # Extract credentials from broker URL
        user = "guest"
        password = "guest"
        if "@" in broker_url:
            cred_part = broker_url.split("//")[1].split("@")[0]
            if ":" in cred_part:
                user, password = cred_part.split(":", 1)

        api_url = f"{mgmt_url}/api/queues"
        credentials = base64.b64encode(f"{user}:{password}".encode()).decode()
        req = urllib.request.Request(api_url)
        req.add_header("Authorization", f"Basic {credentials}")

        with urllib.request.urlopen(req, timeout=5) as resp:
            queues = json.loads(resp.read())

        total_dlq_messages = 0
        for queue in queues:
            if queue.get("name", "").endswith(".dlq"):
                total_dlq_messages += queue.get("messages", 0)

        if total_dlq_messages > alert_threshold:
            return HealthCheckResult(
                "dlq", "unhealthy", _now_iso(),
                f"DLQ depth {total_dlq_messages} exceeds threshold {alert_threshold}",
            )
        return HealthCheckResult("dlq", "healthy", _now_iso(), f"DLQ depth: {total_dlq_messages}")
    except Exception as e:
        return HealthCheckResult("dlq", "unhealthy", _now_iso(), str(e))


def run_all_checks(dlq_alert_threshold: int = 10) -> list[HealthCheckResult]:
    """Run all health checks and return results."""
    checks = [
        check_gateway_health,
        check_ai_health,
        check_pdf_health,
        check_notification_health,
        check_database_health,
        check_redis_health,
        check_broker_health,
    ]
    results = []
    for check_fn in checks:
        try:
            result = check_fn()
        except Exception as e:
            result = HealthCheckResult(
                check_fn.__name__.replace("check_", "").replace("_health", ""),
                "unhealthy",
                _now_iso(),
                f"Unexpected error: {e}",
            )
        results.append(result)

    # DLQ check with threshold
    try:
        results.append(check_dlq_health(dlq_alert_threshold))
    except Exception as e:
        results.append(HealthCheckResult("dlq", "unhealthy", _now_iso(), f"Unexpected error: {e}"))

    return results
