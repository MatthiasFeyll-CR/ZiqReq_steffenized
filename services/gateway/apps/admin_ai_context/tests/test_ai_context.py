"""Tests for Admin AI Context endpoints — US-001, US-005, US-004.

Test IDs: T-11.2.01, T-11.2.02, API-ADMIN.03, API-ADMIN.04, API-ADMIN.05, API-ADMIN.06,
           T-3.4.01, T-3.4.02
"""

import json
import uuid
from unittest.mock import MagicMock, patch

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

    @patch("apps.admin_ai_context.views._get_ai_client")
    def test_patch_company_context(self, mock_get_client):
        """API-ADMIN.06 / T-11.2.02: PATCH updates company context sections + free_text."""
        mock_get_client.return_value = MagicMock()
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

    @patch("apps.admin_ai_context.views._get_ai_client")
    def test_get_after_patch_returns_updated_company_context(self, mock_get_client):
        """T-11.2.02: Sections + free_text persist after PATCH."""
        mock_get_client.return_value = MagicMock()
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

    @patch("apps.admin_ai_context.views._get_ai_client")
    def test_patch_partial_update_sections_only(self, mock_get_client):
        """PATCH with only sections updates sections, keeps free_text default."""
        mock_get_client.return_value = MagicMock()
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


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestCompanyContextReindexing(TestCase):
    """Tests for US-005: Context re-indexing trigger on company context PATCH."""

    def setUp(self):
        self.client = APIClient()
        self.admin = _create_user(ADMIN_ID, "admin@test.local", "Admin User", ["user", "admin"])
        self.client.post("/api/auth/dev-login", {"user_id": str(ADMIN_ID)}, format="json")

    @patch("apps.admin_ai_context.views._get_ai_client")
    def test_patch_triggers_grpc_reindex(self, mock_get_client):
        """US-005: PATCH company context triggers AI gRPC update_context_agent_bucket."""
        mock_client = MagicMock()
        mock_client.update_context_agent_bucket.return_value = {"status": "accepted"}
        mock_get_client.return_value = mock_client

        response = self.client.patch(
            "/api/admin/ai-context/company",
            {"sections": {"domain": "fintech"}, "free_text": "company info"},
            format="json",
        )
        assert response.status_code == 200

        mock_client.update_context_agent_bucket.assert_called_once()
        call_kwargs = mock_client.update_context_agent_bucket.call_args
        assert json.loads(call_kwargs.kwargs["sections_json"]) == {"domain": "fintech"}
        assert call_kwargs.kwargs["free_text"] == "company info"
        assert call_kwargs.kwargs["updated_by_id"] == str(ADMIN_ID)

    @patch("apps.admin_ai_context.views._get_ai_client")
    def test_patch_returns_500_on_grpc_failure(self, mock_get_client):
        """US-005: gRPC failure returns 500 with error details."""
        mock_client = MagicMock()
        mock_client.update_context_agent_bucket.side_effect = Exception("gRPC unavailable")
        mock_get_client.return_value = mock_client

        response = self.client.patch(
            "/api/admin/ai-context/company",
            {"sections": {"key": "val"}, "free_text": "text"},
            format="json",
        )
        assert response.status_code == 500
        data = response.json()
        assert data["error"] == "REINDEX_FAILED"

    @patch("apps.admin_ai_context.views._get_ai_client")
    def test_get_does_not_trigger_grpc(self, mock_get_client):
        """US-005: GET company context does NOT trigger gRPC."""
        response = self.client.get("/api/admin/ai-context/company")
        assert response.status_code == 200
        mock_get_client.assert_not_called()


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestFacilitatorContextType(TestCase):
    """US-004: Facilitator context endpoints support ?type= query param.

    Test IDs: T-3.4.01, T-3.4.02
    """

    def setUp(self):
        self.client = APIClient()
        self.admin = _create_user(ADMIN_ID, "admin@test.local", "Admin User", ["user", "admin"])
        self._login_as(self.admin)

    def _login_as(self, user: User):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    def test_get_facilitator_global_type(self):
        """GET with ?type=global returns bucket with context_type=global."""
        response = self.client.get("/api/admin/ai-context/facilitator?type=global")
        assert response.status_code == 200
        data = response.json()
        assert data["context_type"] == "global"

    def test_get_facilitator_software_type(self):
        """GET with ?type=software returns bucket with context_type=software."""
        response = self.client.get("/api/admin/ai-context/facilitator?type=software")
        assert response.status_code == 200
        data = response.json()
        assert data["context_type"] == "software"

    def test_get_facilitator_non_software_type(self):
        """GET with ?type=non_software returns bucket with context_type=non_software."""
        response = self.client.get("/api/admin/ai-context/facilitator?type=non_software")
        assert response.status_code == 200
        data = response.json()
        assert data["context_type"] == "non_software"

    def test_get_facilitator_default_is_global(self):
        """GET without ?type defaults to global."""
        response = self.client.get("/api/admin/ai-context/facilitator")
        assert response.status_code == 200
        data = response.json()
        assert data["context_type"] == "global"

    def test_patch_facilitator_software_type(self):
        """PATCH with ?type=software updates the software bucket."""
        response = self.client.patch(
            "/api/admin/ai-context/facilitator?type=software",
            {"content": "Software-specific guidance"},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Software-specific guidance"
        assert data["context_type"] == "software"

        # Verify global bucket is NOT changed
        global_resp = self.client.get("/api/admin/ai-context/facilitator?type=global")
        assert global_resp.json()["content"] != "Software-specific guidance"

    def test_three_independent_facilitator_buckets(self):
        """T-3.4.02: Three independent buckets can be updated separately."""
        for ct in ("global", "software", "non_software"):
            self.client.patch(
                f"/api/admin/ai-context/facilitator?type={ct}",
                {"content": f"Content for {ct}"},
                format="json",
            )

        for ct in ("global", "software", "non_software"):
            resp = self.client.get(f"/api/admin/ai-context/facilitator?type={ct}")
            assert resp.json()["content"] == f"Content for {ct}"

    def test_unique_constraint_prevents_duplicate(self):
        """T-3.4.01: UNIQUE constraint on context_type prevents duplicates."""
        from django.db import IntegrityError

        from apps.admin_ai_context.models import FacilitatorContextBucket

        # Ensure global bucket exists
        self.client.get("/api/admin/ai-context/facilitator?type=global")

        # Try to create a duplicate — should raise IntegrityError
        try:
            FacilitatorContextBucket.objects.create(context_type="global", content="dup")
            assert False, "Expected IntegrityError"
        except IntegrityError:
            pass  # Expected


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestCompanyContextType(TestCase):
    """US-004: Company context endpoints support ?type= query param."""

    def setUp(self):
        self.client = APIClient()
        self.admin = _create_user(ADMIN_ID, "admin@test.local", "Admin User", ["user", "admin"])
        self._login_as(self.admin)

    def _login_as(self, user: User):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    def test_get_company_software_type(self):
        """GET with ?type=software returns software company bucket."""
        response = self.client.get("/api/admin/ai-context/company?type=software")
        assert response.status_code == 200
        data = response.json()
        assert data["context_type"] == "software"

    @patch("apps.admin_ai_context.views._get_ai_client")
    def test_patch_company_non_software_type(self, mock_get_client):
        """PATCH with ?type=non_software updates the non_software bucket."""
        mock_get_client.return_value = MagicMock()
        response = self.client.patch(
            "/api/admin/ai-context/company?type=non_software",
            {"sections": {"domain": "construction"}, "free_text": "site info"},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["context_type"] == "non_software"
        assert data["sections"] == {"domain": "construction"}
