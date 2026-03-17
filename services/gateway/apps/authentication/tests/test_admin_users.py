"""Tests for Admin Users Search endpoint — US-004.

Test IDs: API-ADMIN.11, API-ADMIN.12
"""

import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.projects.models import ChatMessage, Project
from apps.review.models import ReviewTimelineEntry

ADMIN_ID = uuid.UUID("00000000-0000-0000-0000-c00000000001")
USER_ID = uuid.UUID("00000000-0000-0000-0000-c00000000002")
USER2_ID = uuid.UUID("00000000-0000-0000-0000-c00000000003")


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
class TestAdminUsersSearch(TestCase):
    """Integration tests for GET /api/admin/users/search."""

    def setUp(self):
        self.client = APIClient()
        self.admin = _create_user(ADMIN_ID, "admin@test.local", "Admin User", ["user", "admin"])
        self.alice = _create_user(USER_ID, "alice@example.com", "Alice Smith", ["user"])
        self.bob = _create_user(USER2_ID, "bob@example.com", "Bob Jones", ["user", "reviewer"])
        self._login_as(self.admin)

    def _login_as(self, user: User):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    # --- API-ADMIN.11: GET /api/admin/users/search (happy path) ---

    def test_search_returns_200(self):
        """API-ADMIN.11: GET /api/admin/users/search returns 200 + results."""
        response = self.client.get("/api/admin/users/search", {"q": "alice"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["display_name"] == "Alice Smith"

    def test_search_by_email(self):
        """Search matches email case-insensitively."""
        response = self.client.get("/api/admin/users/search", {"q": "BOB@EXAMPLE"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["email"] == "bob@example.com"

    def test_search_by_display_name_case_insensitive(self):
        """Search matches display_name case-insensitively."""
        response = self.client.get("/api/admin/users/search", {"q": "ALICE"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["display_name"] == "Alice Smith"

    def test_empty_query_returns_all_users(self):
        """Empty query returns all users."""
        response = self.client.get("/api/admin/users/search")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3  # admin + alice + bob

    def test_results_ordered_by_display_name(self):
        """Results are ordered alphabetically by display_name."""
        response = self.client.get("/api/admin/users/search")
        assert response.status_code == 200
        data = response.json()
        names = [u["display_name"] for u in data]
        assert names == sorted(names)

    def test_result_includes_stats_fields(self):
        """Each result includes id, email, first_name, last_name, display_name, roles, and stats."""
        response = self.client.get("/api/admin/users/search", {"q": "alice"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        user = data[0]
        for field in ["id", "email", "first_name", "last_name", "display_name", "roles",
                       "project_count", "review_count", "contribution_count"]:
            assert field in user, f"Missing field: {field}"

    def test_project_count_owner(self):
        """project_count counts projects where user is owner."""
        Project.objects.create(
            id=uuid.uuid4(), title="Project 1", owner_id=self.alice.id,
        )
        Project.objects.create(
            id=uuid.uuid4(), title="Project 2", owner_id=self.alice.id,
        )
        response = self.client.get("/api/admin/users/search", {"q": "alice"})
        data = response.json()
        assert data[0]["project_count"] == 2

    def test_project_count_excludes_deleted(self):
        """project_count excludes soft-deleted projects."""
        from django.utils import timezone
        Project.objects.create(
            id=uuid.uuid4(), title="Deleted Project", owner_id=self.alice.id,
            deleted_at=timezone.now(),
        )
        response = self.client.get("/api/admin/users/search", {"q": "alice"})
        data = response.json()
        assert data[0]["project_count"] == 0

    def test_review_count(self):
        """review_count counts review_timeline_entries authored by user."""
        project = Project.objects.create(
            id=uuid.uuid4(), title="Project", owner_id=self.admin.id,
        )
        ReviewTimelineEntry.objects.create(
            id=uuid.uuid4(), project_id=project.id, entry_type="comment",
            author_id=self.alice.id, content="Review comment",
        )
        ReviewTimelineEntry.objects.create(
            id=uuid.uuid4(), project_id=project.id, entry_type="state_change",
            author_id=self.alice.id,
        )
        response = self.client.get("/api/admin/users/search", {"q": "alice"})
        data = response.json()
        assert data[0]["review_count"] == 2

    def test_contribution_count_chat_messages(self):
        """contribution_count includes chat messages sent by user."""
        project = Project.objects.create(
            id=uuid.uuid4(), title="Project", owner_id=self.alice.id,
        )
        ChatMessage.objects.create(
            id=uuid.uuid4(), project_id=project.id, sender_type="user",
            sender_id=self.alice.id, content="Hello",
        )
        ChatMessage.objects.create(
            id=uuid.uuid4(), project_id=project.id, sender_type="user",
            sender_id=self.alice.id, content="World",
        )
        # AI messages should not count
        ChatMessage.objects.create(
            id=uuid.uuid4(), project_id=project.id, sender_type="ai",
            sender_id=None, content="AI response",
        )
        response = self.client.get("/api/admin/users/search", {"q": "alice"})
        data = response.json()
        assert data[0]["contribution_count"] >= 2

    def test_zero_stats_when_no_activity(self):
        """Stats default to 0 when user has no activity."""
        response = self.client.get("/api/admin/users/search", {"q": "alice"})
        data = response.json()
        assert data[0]["project_count"] == 0
        assert data[0]["review_count"] == 0
        assert data[0]["contribution_count"] == 0


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestAdminUsersSearchAuthz(TestCase):
    """Authorization tests for GET /api/admin/users/search."""

    def setUp(self):
        self.client = APIClient()
        self.regular = _create_user(USER_ID, "user@test.local", "Regular User", ["user"])
        self._login_as(self.regular)

    def _login_as(self, user: User):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    # --- API-ADMIN.12: GET /api/admin/users/search (authz) ---

    def test_non_admin_returns_403(self):
        """API-ADMIN.12: Non-admin user receives 403."""
        response = self.client.get("/api/admin/users/search")
        assert response.status_code == 403
        data = response.json()
        assert data["error"] == "FORBIDDEN"
