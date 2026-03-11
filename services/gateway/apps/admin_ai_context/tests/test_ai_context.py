"""Tests for Admin AI Context endpoints — US-001.

Test IDs: T-11.2.01, T-11.2.02, API-ADMIN.03, API-ADMIN.04, API-ADMIN.05, API-ADMIN.06
"""

import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User

ADMIN_ID = uuid.UUID("00000000-0000-0000-0000-a00000000001")
USER_ID = uuid.UUID("00000000-0000-0000-0000-a00000000002")


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
class TestFacilitatorContext(TestCase):
    """Integration tests for facilitator AI context endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.admin = _create_user(ADMIN_ID, "admin@test.local", "Admin User", ["user", "admin"])
        self.regular = _create_user(USER_ID, "user@test.local", "Regular User", ["user"])
        self._login_as(self.admin)

    def _login_as(self, user: User):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    # --- API-ADMIN.03: GET facilitator context (happy path) ---

    def test_get_facilitator_context(self):
        """API-ADMIN.03: GET /api/admin/ai-context/facilitator returns bucket object."""
        response = self.client.get("/api/admin/ai-context/facilitator")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "content" in data
        assert "updated_by" in data
        assert "updated_at" in data

    # --- API-ADMIN.04: PATCH facilitator context (happy path) ---

    def test_patch_facilitator_context(self):
        """API-ADMIN.04 / T-11.2.01: PATCH updates facilitator content."""
        response = self.client.patch(
            "/api/admin/ai-context/facilitator",
            {"content": "new table of contents"},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "new table of contents"
        assert data["updated_by"] == str(ADMIN_ID)

    def test_get_after_patch_returns_updated_content(self):
        """T-11.2.01: Content persists after PATCH."""
        self.client.patch(
            "/api/admin/ai-context/facilitator",
            {"content": "updated content"},
            format="json",
        )
        response = self.client.get("/api/admin/ai-context/facilitator")
        assert response.status_code == 200
        assert response.json()["content"] == "updated content"

    # --- Authz: non-admin gets 403 ---

    def test_non_admin_gets_403_on_facilitator_get(self):
        """Non-admin user receives 403 on GET facilitator context."""
        self._login_as(self.regular)
        response = self.client.get("/api/admin/ai-context/facilitator")
        assert response.status_code == 403

    def test_non_admin_gets_403_on_facilitator_patch(self):
        """Non-admin user receives 403 on PATCH facilitator context."""
        self._login_as(self.regular)
        response = self.client.patch(
            "/api/admin/ai-context/facilitator",
            {"content": "hack"},
            format="json",
        )
        assert response.status_code == 403


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestCompanyContext(TestCase):
    """Integration tests for company (context agent) AI context endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.admin = _create_user(ADMIN_ID, "admin@test.local", "Admin User", ["user", "admin"])
        self.regular = _create_user(USER_ID, "user@test.local", "Regular User", ["user"])
        self._login_as(self.admin)

    def _login_as(self, user: User):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    # --- API-ADMIN.05: GET company context (happy path) ---

    def test_get_company_context(self):
        """API-ADMIN.05: GET /api/admin/ai-context/company returns bucket object."""
        response = self.client.get("/api/admin/ai-context/company")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "sections" in data
        assert "free_text" in data
        assert "updated_by" in data
        assert "updated_at" in data

    # --- API-ADMIN.06: PATCH company context (happy path) ---

    def test_patch_company_context(self):
        """API-ADMIN.06 / T-11.2.02: PATCH updates company context sections + free_text."""
        response = self.client.patch(
            "/api/admin/ai-context/company",
            {"sections": {"apps": ["App1", "App2"]}, "free_text": "extra info"},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sections"] == {"apps": ["App1", "App2"]}
        assert data["free_text"] == "extra info"
        assert data["updated_by"] == str(ADMIN_ID)

    def test_get_after_patch_returns_updated_company_context(self):
        """T-11.2.02: Sections + free_text persist after PATCH."""
        self.client.patch(
            "/api/admin/ai-context/company",
            {"sections": {"domain": "fintech"}, "free_text": "notes"},
            format="json",
        )
        response = self.client.get("/api/admin/ai-context/company")
        assert response.status_code == 200
        data = response.json()
        assert data["sections"] == {"domain": "fintech"}
        assert data["free_text"] == "notes"

    def test_patch_partial_update_sections_only(self):
        """PATCH with only sections updates sections, keeps free_text default."""
        response = self.client.patch(
            "/api/admin/ai-context/company",
            {"sections": {"key": "val"}},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["sections"] == {"key": "val"}

    # --- Authz: non-admin gets 403 ---

    def test_non_admin_gets_403_on_company_get(self):
        """Non-admin user receives 403 on GET company context."""
        self._login_as(self.regular)
        response = self.client.get("/api/admin/ai-context/company")
        assert response.status_code == 403

    def test_non_admin_gets_403_on_company_patch(self):
        """Non-admin user receives 403 on PATCH company context."""
        self._login_as(self.regular)
        response = self.client.patch(
            "/api/admin/ai-context/company",
            {"sections": {}, "free_text": "hack"},
            format="json",
        )
        assert response.status_code == 403
