"""Tests for Admin Parameters endpoints — US-002.

Test IDs: T-11.3.01, API-ADMIN.01, API-ADMIN.02, API-ADMIN.07, API-ADMIN.08
"""

import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.admin_config.models import AdminParameter
from apps.authentication.models import User

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


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestParameterList(TestCase):
    """Integration tests for GET /api/admin/parameters."""

    def setUp(self):
        self.client = APIClient()
        self.admin = _create_user(ADMIN_ID, "admin@test.local", "Admin User", ["user", "admin"])
        self.regular = _create_user(USER_ID, "user@test.local", "Regular User", ["user"])
        self._login_as(self.admin)

    def _login_as(self, user: User):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    # --- API-ADMIN.01: GET /api/admin/parameters (happy path) ---

    def test_get_parameters_returns_array(self):
        """API-ADMIN.01: GET /api/admin/parameters returns 200 + array."""
        response = self.client.get("/api/admin/parameters")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        first = data[0]
        assert "key" in first
        assert "value" in first
        assert "default_value" in first
        assert "description" in first
        assert "data_type" in first
        assert "category" in first
        assert "updated_by" in first
        assert "updated_at" in first

    def test_get_parameters_ordered_by_key(self):
        """Parameters are returned ordered by key."""
        response = self.client.get("/api/admin/parameters")
        data = response.json()
        keys = [p["key"] for p in data]
        assert keys == sorted(keys)

    # --- API-ADMIN.02: GET /api/admin/parameters (authz) ---

    def test_non_admin_gets_403(self):
        """API-ADMIN.02: Non-admin user receives 403."""
        self._login_as(self.regular)
        response = self.client.get("/api/admin/parameters")
        assert response.status_code == 403


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestParameterUpdate(TestCase):
    """Integration tests for PATCH /api/admin/parameters/:key."""

    def setUp(self):
        self.client = APIClient()
        self.admin = _create_user(ADMIN_ID, "admin@test.local", "Admin User", ["user", "admin"])
        self.regular = _create_user(USER_ID, "user@test.local", "Regular User", ["user"])
        self._login_as(self.admin)

    def _login_as(self, user: User):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    # --- API-ADMIN.07: PATCH /api/admin/parameters/:key (happy path) ---

    def test_patch_parameter_updates_value(self):
        """API-ADMIN.07: PATCH updates parameter value and returns updated object."""
        response = self.client.patch(
            "/api/admin/parameters/debounce_timer",
            {"value": "5"},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "debounce_timer"
        assert data["value"] == "5"
        assert data["updated_by"] == str(ADMIN_ID)

    # --- T-11.3.01: Parameter update applies immediately ---

    def test_parameter_update_applies_runtime(self):
        """T-11.3.01: PATCH value, then GET returns updated value immediately."""
        self.client.patch(
            "/api/admin/parameters/debounce_timer",
            {"value": "7"},
            format="json",
        )
        param = AdminParameter.objects.get(key="debounce_timer")
        assert param.value == "7"

    def test_patch_integer_valid(self):
        """Integer parameter accepts valid integer string."""
        response = self.client.patch(
            "/api/admin/parameters/idle_timeout",
            {"value": "600"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["value"] == "600"

    def test_patch_float_valid(self):
        """Float parameter accepts valid float string."""
        response = self.client.patch(
            "/api/admin/parameters/context_rag_min_similarity",
            {"value": "0.85"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["value"] == "0.85"

    def test_patch_string_valid(self):
        """String parameter accepts any string."""
        response = self.client.patch(
            "/api/admin/parameters/default_app_language",
            {"value": "en"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["value"] == "en"

    # --- API-ADMIN.08: PATCH invalid data_type value → 400 ---

    def test_patch_integer_invalid_returns_400(self):
        """API-ADMIN.08: Invalid integer value returns 400."""
        response = self.client.patch(
            "/api/admin/parameters/debounce_timer",
            {"value": "not-a-number"},
            format="json",
        )
        assert response.status_code == 400

    def test_patch_float_invalid_returns_400(self):
        """Invalid float value returns 400."""
        response = self.client.patch(
            "/api/admin/parameters/context_rag_min_similarity",
            {"value": "abc"},
            format="json",
        )
        assert response.status_code == 400

    def test_patch_boolean_invalid_returns_400(self):
        """Invalid boolean value returns 400."""
        # First create a boolean parameter for testing
        AdminParameter.objects.update_or_create(
            key="test_bool_param",
            defaults={
                "value": "true",
                "default_value": "true",
                "description": "Test boolean",
                "data_type": "boolean",
                "category": "Application",
            },
        )
        response = self.client.patch(
            "/api/admin/parameters/test_bool_param",
            {"value": "yes"},
            format="json",
        )
        assert response.status_code == 400

    def test_patch_boolean_valid(self):
        """Boolean parameter accepts 'true' or 'false'."""
        AdminParameter.objects.update_or_create(
            key="test_bool_param",
            defaults={
                "value": "true",
                "default_value": "true",
                "description": "Test boolean",
                "data_type": "boolean",
                "category": "Application",
            },
        )
        response = self.client.patch(
            "/api/admin/parameters/test_bool_param",
            {"value": "false"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["value"] == "false"

    def test_patch_nonexistent_parameter_returns_404(self):
        """PATCH to nonexistent key returns 404."""
        response = self.client.patch(
            "/api/admin/parameters/nonexistent_key",
            {"value": "anything"},
            format="json",
        )
        assert response.status_code == 404

    def test_non_admin_gets_403_on_patch(self):
        """Non-admin user receives 403 on PATCH."""
        self._login_as(self.regular)
        response = self.client.patch(
            "/api/admin/parameters/debounce_timer",
            {"value": "5"},
            format="json",
        )
        assert response.status_code == 403
