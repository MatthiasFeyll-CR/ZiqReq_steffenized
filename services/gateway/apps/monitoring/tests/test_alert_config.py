"""Tests for Alert Configuration + Dispatch — US-007.

Tests alert config GET/PATCH endpoints and notification dispatch.
"""

import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.monitoring.models import MonitoringAlertConfig

ADMIN_ID = uuid.UUID("00000000-0000-0000-0000-c00000000001")
ADMIN2_ID = uuid.UUID("00000000-0000-0000-0000-c00000000002")
USER_ID = uuid.UUID("00000000-0000-0000-0000-c00000000003")


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


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestAlertConfigGet(TestCase):
    """Tests for GET /api/admin/monitoring/alerts."""

    def setUp(self):
        self.client = APIClient()
        self.admin = _create_user(ADMIN_ID, "admin@test.local", "Admin User", ["user", "admin"])
        self.regular = _create_user(USER_ID, "user@test.local", "Regular User", ["user"])
        self._login_as(self.admin)

    def _login_as(self, user: User):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    def test_get_returns_200(self):
        """GET /api/admin/monitoring/alerts returns 200."""
        response = self.client.get("/api/admin/monitoring/alerts")
        assert response.status_code == 200

    def test_get_returns_user_id_and_is_active(self):
        """GET response contains user_id and is_active fields."""
        response = self.client.get("/api/admin/monitoring/alerts")
        data = response.json()
        assert "user_id" in data
        assert "is_active" in data
        assert data["user_id"] == str(ADMIN_ID)
        assert data["is_active"] is False

    def test_get_creates_config_on_first_access(self):
        """GET creates a MonitoringAlertConfig row if none exists (upsert)."""
        assert MonitoringAlertConfig.objects.filter(user_id=ADMIN_ID).count() == 0
        response = self.client.get("/api/admin/monitoring/alerts")
        assert response.status_code == 200
        assert MonitoringAlertConfig.objects.filter(user_id=ADMIN_ID).count() == 1

    def test_get_returns_existing_config(self):
        """GET returns existing config if already created."""
        MonitoringAlertConfig.objects.create(user_id=ADMIN_ID, is_active=True)
        response = self.client.get("/api/admin/monitoring/alerts")
        data = response.json()
        assert data["is_active"] is True

    def test_non_admin_gets_403(self):
        """Non-admin user receives 403 on GET /api/admin/monitoring/alerts."""
        self._login_as(self.regular)
        response = self.client.get("/api/admin/monitoring/alerts")
        assert response.status_code == 403


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestAlertConfigPatch(TestCase):
    """Tests for PATCH /api/admin/monitoring/alerts."""

    def setUp(self):
        self.client = APIClient()
        self.admin = _create_user(ADMIN_ID, "admin@test.local", "Admin User", ["user", "admin"])
        self.regular = _create_user(USER_ID, "user@test.local", "Regular User", ["user"])
        self._login_as(self.admin)

    def _login_as(self, user: User):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    def test_patch_opt_in(self):
        """PATCH with is_active=true opts the admin in."""
        response = self.client.patch(
            "/api/admin/monitoring/alerts",
            {"is_active": True},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True
        assert data["user_id"] == str(ADMIN_ID)

    def test_patch_opt_out(self):
        """PATCH with is_active=false opts the admin out."""
        MonitoringAlertConfig.objects.create(user_id=ADMIN_ID, is_active=True)
        response = self.client.patch(
            "/api/admin/monitoring/alerts",
            {"is_active": False},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_patch_persists_to_db(self):
        """PATCH updates the database record."""
        self.client.patch(
            "/api/admin/monitoring/alerts",
            {"is_active": True},
            format="json",
        )
        config = MonitoringAlertConfig.objects.get(user_id=ADMIN_ID)
        assert config.is_active is True

    def test_patch_creates_config_if_missing(self):
        """PATCH creates config row if none exists."""
        assert MonitoringAlertConfig.objects.filter(user_id=ADMIN_ID).count() == 0
        self.client.patch(
            "/api/admin/monitoring/alerts",
            {"is_active": True},
            format="json",
        )
        assert MonitoringAlertConfig.objects.filter(user_id=ADMIN_ID).count() == 1

    def test_patch_missing_is_active_returns_400(self):
        """PATCH without is_active field returns 400."""
        response = self.client.patch(
            "/api/admin/monitoring/alerts",
            {},
            format="json",
        )
        assert response.status_code == 400

    def test_non_admin_gets_403(self):
        """Non-admin user receives 403 on PATCH /api/admin/monitoring/alerts."""
        self._login_as(self.regular)
        response = self.client.patch(
            "/api/admin/monitoring/alerts",
            {"is_active": True},
            format="json",
        )
        assert response.status_code == 403

    def test_each_admin_has_own_config(self):
        """Different admins have independent alert configs."""
        admin2 = _create_user(ADMIN2_ID, "admin2@test.local", "Admin Two", ["user", "admin"])

        # Admin 1 opts in
        self.client.patch(
            "/api/admin/monitoring/alerts",
            {"is_active": True},
            format="json",
        )

        # Admin 2 opts out (default)
        self._login_as(admin2)
        response = self.client.get("/api/admin/monitoring/alerts")
        assert response.json()["is_active"] is False

        # Verify admin 1 is still opted in
        self._login_as(self.admin)
        response = self.client.get("/api/admin/monitoring/alerts")
        assert response.json()["is_active"] is True


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestAlertDispatchIntegration(TestCase):
    """Tests for monitoring alert email dispatch logic."""

    def setUp(self):
        self.admin = _create_user(ADMIN_ID, "admin@test.local", "Admin User", ["user", "admin"])
        self.admin2 = _create_user(ADMIN2_ID, "admin2@test.local", "Admin Two", ["user", "admin"])

    def test_opted_in_admins_queryable(self):
        """MonitoringAlertConfig.objects.filter(is_active=True) returns opted-in admins."""
        MonitoringAlertConfig.objects.create(user_id=ADMIN_ID, is_active=True)
        MonitoringAlertConfig.objects.create(user_id=ADMIN2_ID, is_active=False)

        opted_in = MonitoringAlertConfig.objects.filter(is_active=True)
        assert opted_in.count() == 1
        assert opted_in.first().user_id == ADMIN_ID

    def test_no_opted_in_admins(self):
        """No opted-in admins returns empty queryset."""
        MonitoringAlertConfig.objects.create(user_id=ADMIN_ID, is_active=False)
        opted_in = MonitoringAlertConfig.objects.filter(is_active=True)
        assert opted_in.count() == 0
