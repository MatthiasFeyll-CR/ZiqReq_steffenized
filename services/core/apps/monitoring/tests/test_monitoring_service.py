"""Tests for Monitoring Backend Service — Celery Periodic Task (US-006).

Test IDs: T-11.5.01
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from apps.monitoring.health_checks import (
    HealthCheckResult,
    check_database_health,
)


class TestHealthCheckResult(TestCase):
    """Test HealthCheckResult dataclass."""

    def test_to_dict(self):
        result = HealthCheckResult(
            service_name="gateway",
            status="healthy",
            last_check="2026-01-01T00:00:00+00:00",
            details="OK",
        )
        d = result.to_dict()
        self.assertEqual(d["service_name"], "gateway")
        self.assertEqual(d["status"], "healthy")
        self.assertEqual(d["last_check"], "2026-01-01T00:00:00+00:00")
        self.assertEqual(d["details"], "OK")

    def test_to_dict_empty_details(self):
        result = HealthCheckResult(
            service_name="redis", status="unhealthy", last_check="2026-01-01T00:00:00+00:00"
        )
        d = result.to_dict()
        self.assertEqual(d["details"], "")


class TestIndividualHealthChecks(TestCase):
    """Test individual health check functions."""

    @override_settings(
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        }
    )
    def test_check_database_healthy(self):
        result = check_database_health()
        self.assertEqual(result.service_name, "database")
        self.assertEqual(result.status, "healthy")

    @patch("apps.monitoring.health_checks.grpc")
    def test_check_grpc_healthy(self, mock_grpc):
        from apps.monitoring.health_checks import check_grpc_health

        mock_channel = MagicMock()
        mock_grpc.insecure_channel.return_value = mock_channel
        mock_future = MagicMock()
        mock_grpc.channel_ready_future.return_value = mock_future

        result = check_grpc_health("ai", "localhost:50052")
        self.assertEqual(result.service_name, "ai")
        self.assertEqual(result.status, "healthy")
        mock_future.result.assert_called_once_with(timeout=5)
        mock_channel.close.assert_called_once()

    @patch("apps.monitoring.health_checks.grpc")
    def test_check_grpc_unhealthy(self, mock_grpc):
        from apps.monitoring.health_checks import check_grpc_health

        mock_grpc.insecure_channel.return_value = MagicMock()
        mock_future = MagicMock()
        mock_future.result.side_effect = Exception("Connection refused")
        mock_grpc.channel_ready_future.return_value = mock_future

        result = check_grpc_health("ai", "localhost:50052")
        self.assertEqual(result.service_name, "ai")
        self.assertEqual(result.status, "unhealthy")
        self.assertIn("Connection refused", result.details)

    @patch("apps.monitoring.health_checks.urllib.request.urlopen")
    def test_check_gateway_healthy(self, mock_urlopen):
        from apps.monitoring.health_checks import check_gateway_health

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = check_gateway_health()
        self.assertEqual(result.service_name, "gateway")
        self.assertEqual(result.status, "healthy")

    @patch("apps.monitoring.health_checks.urllib.request.urlopen")
    def test_check_gateway_unhealthy(self, mock_urlopen):
        from apps.monitoring.health_checks import check_gateway_health

        mock_urlopen.side_effect = Exception("Connection refused")

        result = check_gateway_health()
        self.assertEqual(result.service_name, "gateway")
        self.assertEqual(result.status, "unhealthy")

    def test_check_redis_healthy(self):
        with patch("apps.monitoring.health_checks.redis_lib") as mock_redis_mod:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_redis_mod.from_url.return_value = mock_client

            from apps.monitoring.health_checks import check_redis_health

            result = check_redis_health()
            self.assertEqual(result.service_name, "redis")
            self.assertEqual(result.status, "healthy")

    def test_check_redis_unhealthy(self):
        with patch("apps.monitoring.health_checks.redis_lib") as mock_redis_mod:
            mock_redis_mod.from_url.side_effect = Exception("Connection refused")

            from apps.monitoring.health_checks import check_redis_health

            result = check_redis_health()
            self.assertEqual(result.service_name, "redis")
            self.assertEqual(result.status, "unhealthy")

    @patch("apps.monitoring.health_checks.pika")
    def test_check_broker_healthy(self, mock_pika):
        from apps.monitoring.health_checks import check_broker_health

        result = check_broker_health()
        self.assertEqual(result.service_name, "broker")
        self.assertEqual(result.status, "healthy")
        mock_pika.BlockingConnection.assert_called_once()

    @patch("apps.monitoring.health_checks.pika")
    def test_check_broker_unhealthy(self, mock_pika):
        from apps.monitoring.health_checks import check_broker_health

        mock_pika.BlockingConnection.side_effect = Exception("Connection refused")

        result = check_broker_health()
        self.assertEqual(result.service_name, "broker")
        self.assertEqual(result.status, "unhealthy")

    def test_check_notification_healthy(self):
        import time

        with patch("apps.monitoring.health_checks.redis_lib") as mock_redis_mod:
            mock_client = MagicMock()
            mock_client.get.return_value = str(time.time()).encode()
            mock_redis_mod.from_url.return_value = mock_client

            from apps.monitoring.health_checks import check_notification_health

            result = check_notification_health()
            self.assertEqual(result.service_name, "notification")
            self.assertEqual(result.status, "healthy")

    def test_check_notification_no_heartbeat(self):
        with patch("apps.monitoring.health_checks.redis_lib") as mock_redis_mod:
            mock_client = MagicMock()
            mock_client.get.return_value = None
            mock_redis_mod.from_url.return_value = mock_client

            from apps.monitoring.health_checks import check_notification_health

            result = check_notification_health()
            self.assertEqual(result.service_name, "notification")
            self.assertEqual(result.status, "unhealthy")
            self.assertIn("No heartbeat", result.details)


class TestRunAllChecks(TestCase):
    """Test run_all_checks aggregation."""

    @patch("apps.monitoring.health_checks.check_dlq_health")
    @patch("apps.monitoring.health_checks.check_broker_health")
    @patch("apps.monitoring.health_checks.check_redis_health")
    @patch("apps.monitoring.health_checks.check_database_health")
    @patch("apps.monitoring.health_checks.check_notification_health")
    @patch("apps.monitoring.health_checks.check_pdf_health")
    @patch("apps.monitoring.health_checks.check_ai_health")
    @patch("apps.monitoring.health_checks.check_gateway_health")
    def test_run_all_checks_all_healthy(
        self,
        mock_gw,
        mock_ai,
        mock_pdf,
        mock_notif,
        mock_db,
        mock_redis,
        mock_broker,
        mock_dlq,
    ):
        from apps.monitoring.health_checks import run_all_checks

        for mock_fn, name in [
            (mock_gw, "gateway"),
            (mock_ai, "ai"),
            (mock_pdf, "pdf"),
            (mock_notif, "notification"),
            (mock_db, "database"),
            (mock_redis, "redis"),
            (mock_broker, "broker"),
            (mock_dlq, "dlq"),
        ]:
            mock_fn.return_value = HealthCheckResult(name, "healthy", "2026-01-01T00:00:00+00:00")

        results = run_all_checks(dlq_alert_threshold=10)
        self.assertEqual(len(results), 8)
        self.assertTrue(all(r.status == "healthy" for r in results))

    @patch("apps.monitoring.health_checks.check_dlq_health")
    @patch("apps.monitoring.health_checks.check_broker_health")
    @patch("apps.monitoring.health_checks.check_redis_health")
    @patch("apps.monitoring.health_checks.check_database_health")
    @patch("apps.monitoring.health_checks.check_notification_health")
    @patch("apps.monitoring.health_checks.check_pdf_health")
    @patch("apps.monitoring.health_checks.check_ai_health")
    @patch("apps.monitoring.health_checks.check_gateway_health")
    def test_run_all_checks_some_unhealthy(
        self,
        mock_gw,
        mock_ai,
        mock_pdf,
        mock_notif,
        mock_db,
        mock_redis,
        mock_broker,
        mock_dlq,
    ):
        from apps.monitoring.health_checks import run_all_checks

        mock_gw.return_value = HealthCheckResult("gateway", "healthy", "2026-01-01T00:00:00+00:00")
        mock_ai.return_value = HealthCheckResult("ai", "unhealthy", "2026-01-01T00:00:00+00:00", "gRPC down")
        mock_pdf.return_value = HealthCheckResult("pdf", "healthy", "2026-01-01T00:00:00+00:00")
        mock_notif.return_value = HealthCheckResult("notification", "healthy", "2026-01-01T00:00:00+00:00")
        mock_db.return_value = HealthCheckResult("database", "healthy", "2026-01-01T00:00:00+00:00")
        mock_redis.return_value = HealthCheckResult("redis", "healthy", "2026-01-01T00:00:00+00:00")
        mock_broker.return_value = HealthCheckResult("broker", "healthy", "2026-01-01T00:00:00+00:00")
        mock_dlq.return_value = HealthCheckResult("dlq", "healthy", "2026-01-01T00:00:00+00:00")

        results = run_all_checks(dlq_alert_threshold=10)
        unhealthy = [r for r in results if r.status == "unhealthy"]
        self.assertEqual(len(unhealthy), 1)
        self.assertEqual(unhealthy[0].service_name, "ai")


@override_settings(
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
)
class TestHealthCheckTask(TestCase):
    """Test the Celery health_check_task."""

    @patch("apps.monitoring.tasks._store_result_in_redis")
    @patch("apps.monitoring.health_checks.run_all_checks")
    @patch("apps.admin_config.services.get_parameter")
    def test_task_all_healthy_no_alerts(self, mock_get_param, mock_run_checks, mock_store):
        """All healthy → no alerts published."""
        from apps.monitoring.tasks import health_check_task

        mock_get_param.side_effect = lambda key, default=None, cast=str: {
            "health_check_interval": 60,
            "dlq_alert_threshold": 10,
        }.get(key, default)

        mock_run_checks.return_value = [
            HealthCheckResult("gateway", "healthy", "2026-01-01T00:00:00+00:00"),
            HealthCheckResult("database", "healthy", "2026-01-01T00:00:00+00:00"),
        ]

        result = health_check_task()
        self.assertEqual(result["total_checks"], 2)
        self.assertEqual(result["healthy"], 2)
        self.assertEqual(result["unhealthy"], 0)
        self.assertEqual(result["alerts_published"], 0)
        self.assertEqual(mock_store.call_count, 2)

    @patch("events.publisher.publish_event")
    @patch("apps.monitoring.tasks._store_result_in_redis")
    @patch("apps.monitoring.health_checks.run_all_checks")
    @patch("apps.admin_config.services.get_parameter")
    def test_task_unhealthy_publishes_alert(self, mock_get_param, mock_run_checks, mock_store, mock_publish):
        """T-11.5.01: Unhealthy service → monitoring.alert event published."""
        from apps.monitoring.tasks import health_check_task

        mock_get_param.side_effect = lambda key, default=None, cast=str: {
            "health_check_interval": 60,
            "dlq_alert_threshold": 10,
        }.get(key, default)

        mock_run_checks.return_value = [
            HealthCheckResult("gateway", "healthy", "2026-01-01T00:00:00+00:00"),
            HealthCheckResult("ai", "unhealthy", "2026-01-01T00:00:00+00:00", "gRPC down"),
            HealthCheckResult("database", "healthy", "2026-01-01T00:00:00+00:00"),
        ]

        result = health_check_task()
        self.assertEqual(result["total_checks"], 3)
        self.assertEqual(result["healthy"], 2)
        self.assertEqual(result["unhealthy"], 1)
        self.assertEqual(result["alerts_published"], 1)

        mock_publish.assert_called_once_with(
            event_type="monitoring.alert",
            payload={
                "alert_type": "service_unhealthy",
                "service_name": "ai",
                "details": "gRPC down",
                "timestamp": "2026-01-01T00:00:00+00:00",
            },
        )

    @patch("events.publisher.publish_event")
    @patch("apps.monitoring.tasks._store_result_in_redis")
    @patch("apps.monitoring.health_checks.run_all_checks")
    @patch("apps.admin_config.services.get_parameter")
    def test_task_multiple_unhealthy_publishes_multiple_alerts(
        self, mock_get_param, mock_run_checks, mock_store, mock_publish
    ):
        """Multiple unhealthy → multiple monitoring.alert events."""
        from apps.monitoring.tasks import health_check_task

        mock_get_param.side_effect = lambda key, default=None, cast=str: {
            "health_check_interval": 60,
            "dlq_alert_threshold": 10,
        }.get(key, default)

        mock_run_checks.return_value = [
            HealthCheckResult("ai", "unhealthy", "2026-01-01T00:00:00+00:00", "gRPC down"),
            HealthCheckResult("redis", "unhealthy", "2026-01-01T00:00:00+00:00", "Connection refused"),
        ]

        result = health_check_task()
        self.assertEqual(result["alerts_published"], 2)
        self.assertEqual(mock_publish.call_count, 2)

    @patch("apps.monitoring.tasks._store_result_in_redis")
    @patch("apps.monitoring.health_checks.run_all_checks")
    @patch("apps.admin_config.services.get_parameter")
    def test_task_stores_results_in_redis_with_ttl(self, mock_get_param, mock_run_checks, mock_store):
        """Health check results stored in Redis with TTL = 2 * interval."""
        from apps.monitoring.tasks import health_check_task

        mock_get_param.side_effect = lambda key, default=None, cast=str: {
            "health_check_interval": 30,
            "dlq_alert_threshold": 10,
        }.get(key, default)

        mock_run_checks.return_value = [
            HealthCheckResult("gateway", "healthy", "2026-01-01T00:00:00+00:00"),
        ]

        health_check_task()

        mock_store.assert_called_once()
        args = mock_store.call_args
        self.assertEqual(args[0][0]["service_name"], "gateway")
        self.assertEqual(args[0][1], 60)  # TTL = 2 * 30

    @patch("apps.monitoring.tasks._store_result_in_redis")
    @patch("apps.monitoring.health_checks.run_all_checks")
    @patch("apps.admin_config.services.get_parameter")
    def test_task_reads_configurable_parameters(self, mock_get_param, mock_run_checks, mock_store):
        """Task reads health_check_interval and dlq_alert_threshold from admin_parameters."""
        from apps.monitoring.tasks import health_check_task

        mock_get_param.side_effect = lambda key, default=None, cast=str: {
            "health_check_interval": 120,
            "dlq_alert_threshold": 5,
        }.get(key, default)

        mock_run_checks.return_value = []

        health_check_task()

        mock_run_checks.assert_called_once_with(dlq_alert_threshold=5)

    @patch("apps.monitoring.tasks._store_result_in_redis")
    @patch("apps.monitoring.health_checks.run_all_checks")
    @patch("apps.admin_config.services.get_parameter")
    def test_task_redis_store_failure_does_not_crash(self, mock_get_param, mock_run_checks, mock_store):
        """Redis store failure is logged but does not crash the task."""
        from apps.monitoring.tasks import health_check_task

        mock_get_param.side_effect = lambda key, default=None, cast=str: {
            "health_check_interval": 60,
            "dlq_alert_threshold": 10,
        }.get(key, default)

        mock_run_checks.return_value = [
            HealthCheckResult("gateway", "healthy", "2026-01-01T00:00:00+00:00"),
        ]
        mock_store.side_effect = Exception("Redis down")

        result = health_check_task()
        self.assertEqual(result["total_checks"], 1)
        self.assertEqual(result["healthy"], 1)


class TestStoreResultInRedis(TestCase):
    """Test _store_result_in_redis helper."""

    @patch("apps.monitoring.tasks.redis_lib")
    def test_store_result_sets_key_with_ttl(self, mock_redis_mod):
        from apps.monitoring.tasks import REDIS_KEY_PREFIX, _store_result_in_redis

        mock_client = MagicMock()
        mock_redis_mod.from_url.return_value = mock_client

        result_dict = {"service_name": "gateway", "status": "healthy", "last_check": "2026-01-01T00:00:00+00:00"}
        _store_result_in_redis(result_dict, ttl=120)

        expected_key = f"{REDIS_KEY_PREFIX}gateway"
        mock_client.setex.assert_called_once_with(
            expected_key, 120, json.dumps(result_dict)
        )
