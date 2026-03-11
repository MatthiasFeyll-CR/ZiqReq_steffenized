"""Tests for Admin Monitoring Dashboard Endpoint — US-003.

Test IDs: T-11.4.01, API-ADMIN.09, API-ADMIN.10
"""

import uuid
from collections import defaultdict
from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.ideas.models import Idea

ADMIN_ID = uuid.UUID("00000000-0000-0000-0000-b00000000001")
USER_ID = uuid.UUID("00000000-0000-0000-0000-b00000000002")


def _create_user(
    user_id: uuid.UUID, email: str, display_name: str, roles: list[str] | None = None
) -> User:
    return User.objects.create(
        id=user_id,
        email=email,
        first_name=display_name.split()[0],
        last_name=display_name.split()[-1],
        display_name=display_name,
        roles=roles or ["user"],
    )


def _mock_redis_unavailable(*args, **kwargs):
    raise ImportError("django_redis not available in test")


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestMonitoringDashboard(TestCase):
    """Integration tests for monitoring dashboard endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.admin = _create_user(ADMIN_ID, "admin@test.local", "Admin User", ["user", "admin"])
        self.regular = _create_user(USER_ID, "user@test.local", "Regular User", ["user"])
        self._login_as(self.admin)

    def _login_as(self, user: User):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    # --- API-ADMIN.09: GET /api/admin/monitoring (happy path) ---

    def test_get_monitoring_dashboard_returns_200(self):
        """API-ADMIN.09: GET /api/admin/monitoring returns 200 with stats object."""
        response = self.client.get("/api/admin/monitoring")
        assert response.status_code == 200

    def test_dashboard_contains_all_required_fields(self):
        """API-ADMIN.09: Response contains all required top-level fields."""
        response = self.client.get("/api/admin/monitoring")
        data = response.json()
        assert "active_connections" in data
        assert "ideas_by_state" in data
        assert "active_users" in data
        assert "online_users" in data
        assert "ai_processing" in data
        assert "system_health" in data

    def test_ideas_by_state_contains_all_states(self):
        """T-11.4.01: ideas_by_state has all expected state keys."""
        response = self.client.get("/api/admin/monitoring")
        ideas = response.json()["ideas_by_state"]
        for state in ["open", "in_review", "accepted", "dropped", "rejected"]:
            assert state in ideas
            assert isinstance(ideas[state], int)

    def test_ideas_by_state_counts_correctly(self):
        """T-11.4.01: ideas_by_state counts match actual idea records."""
        # Create ideas in various states
        Idea.objects.create(title="Open 1", state="open", owner_id=ADMIN_ID)
        Idea.objects.create(title="Open 2", state="open", owner_id=ADMIN_ID)
        Idea.objects.create(title="Review 1", state="in_review", owner_id=ADMIN_ID)
        Idea.objects.create(title="Accepted 1", state="accepted", owner_id=USER_ID)

        response = self.client.get("/api/admin/monitoring")
        ideas = response.json()["ideas_by_state"]
        assert ideas["open"] == 2
        assert ideas["in_review"] == 1
        assert ideas["accepted"] == 1
        assert ideas["dropped"] == 0
        assert ideas["rejected"] == 0

    def test_deleted_ideas_not_counted(self):
        """ideas_by_state excludes soft-deleted ideas."""
        from django.utils import timezone
        Idea.objects.create(title="Deleted", state="open", owner_id=ADMIN_ID, deleted_at=timezone.now())
        Idea.objects.create(title="Active", state="open", owner_id=ADMIN_ID)

        response = self.client.get("/api/admin/monitoring")
        assert response.json()["ideas_by_state"]["open"] == 1

    def test_active_users_count(self):
        """T-11.4.01: active_users returns total user count."""
        response = self.client.get("/api/admin/monitoring")
        # setUp creates 2 users (admin + regular)
        assert response.json()["active_users"] == 2

    def test_ai_processing_has_required_fields(self):
        """T-11.4.01: ai_processing has request_count, success_count, failure_count."""
        response = self.client.get("/api/admin/monitoring")
        ai = response.json()["ai_processing"]
        assert "request_count" in ai
        assert "success_count" in ai
        assert "failure_count" in ai

    def test_system_health_has_all_services(self):
        """T-11.4.01: system_health has entries for all monitored services."""
        response = self.client.get("/api/admin/monitoring")
        health = response.json()["system_health"]
        for svc in ["gateway", "ai", "pdf", "notification", "database", "redis", "broker", "dlq"]:
            assert svc in health
            assert "status" in health[svc]
            assert "last_check" in health[svc]

    def test_active_connections_with_empty_registry(self):
        """active_connections is 0 when no WebSocket connections exist."""
        response = self.client.get("/api/admin/monitoring")
        assert response.json()["active_connections"] == 0

    def test_online_users_with_empty_registry(self):
        """online_users is 0 when no WebSocket connections exist."""
        response = self.client.get("/api/admin/monitoring")
        assert response.json()["online_users"] == 0

    def test_active_connections_with_presence(self):
        """active_connections counts unique channels from presence registry."""
        mock_registry = defaultdict(lambda: defaultdict(set))
        mock_registry["group1"]["user1"] = {"ch1", "ch2"}
        mock_registry["group2"]["user2"] = {"ch3"}

        with patch("apps.monitoring.services._get_presence_registry", return_value=mock_registry):
            response = self.client.get("/api/admin/monitoring")
            assert response.json()["active_connections"] == 3

    def test_online_users_with_presence(self):
        """online_users counts unique user IDs from presence registry."""
        mock_registry = defaultdict(lambda: defaultdict(set))
        mock_registry["group1"]["user1"] = {"ch1"}
        mock_registry["group2"]["user1"] = {"ch1"}  # same user, different group
        mock_registry["group2"]["user2"] = {"ch2"}

        with patch("apps.monitoring.services._get_presence_registry", return_value=mock_registry):
            response = self.client.get("/api/admin/monitoring")
            assert response.json()["online_users"] == 2

    # --- API-ADMIN.10: Authz — Non-admin gets 403 ---

    def test_non_admin_gets_403(self):
        """API-ADMIN.10: Non-admin user receives 403 on GET /api/admin/monitoring."""
        self._login_as(self.regular)
        response = self.client.get("/api/admin/monitoring")
        assert response.status_code == 403
