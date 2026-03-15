import uuid

from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.ideas.models import ChatMessage, Idea, IdeaCollaborator

USER_1_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
USER_2_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")


def _create_user(user_id: uuid.UUID, email: str, display_name: str) -> User:
    return User.objects.create(
        id=user_id,
        email=email,
        first_name=display_name.split()[0],
        last_name=display_name.split()[-1],
        display_name=display_name,
        roles=["user"],
    )


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestIdeasCRUD(TestCase):
    """Integration tests for the Ideas CRUD API."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = _create_user(USER_1_ID, "user1@test.local", "Test User1")
        self.user2 = _create_user(USER_2_ID, "user2@test.local", "Test User2")
        # Login as user1 via dev-login to set up session
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.user1.id)},
            format="json",
        )

    def _login_as(self, user: User):
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(user.id)},
            format="json",
        )

    # --- API-IDEA.01: Create idea with first message ---

    def test_create_idea_with_first_message(self):
        """API-IDEA.01: POST /api/ideas creates idea, returns 201 + idea object."""
        response = self.client.post(
            "/api/ideas/",
            {"first_message": "My idea"},
            format="json",
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["state"] == "open"
        assert data["title"] == ""
        # Verify ChatMessage was created
        idea_id = data["id"]
        assert ChatMessage.objects.filter(idea_id=idea_id).exists()
        msg = ChatMessage.objects.get(idea_id=idea_id)
        assert msg.content == "My idea"
        assert msg.sender_type == "user"
        assert msg.sender_id == self.user1.id

    # --- API-IDEA.02: Empty first_message validation ---

    def test_create_idea_empty_first_message(self):
        """API-IDEA.02: POST /api/ideas with empty first_message returns 400."""
        response = self.client.post(
            "/api/ideas/",
            {"first_message": ""},
            format="json",
        )
        assert response.status_code == 400

    # --- API-IDEA.03: Unauthenticated request ---

    def test_create_idea_unauthenticated(self):
        """API-IDEA.03: POST /api/ideas without auth returns 401."""
        client = APIClient()  # fresh client, no session
        response = client.post(
            "/api/ideas/",
            {"first_message": "My idea"},
            format="json",
        )
        assert response.status_code == 401

    # --- API-IDEA.04: List user's ideas ---

    def test_list_ideas(self):
        """API-IDEA.04: GET /api/ideas returns paginated results."""
        Idea.objects.create(owner_id=self.user1.id, title="Idea 1")
        Idea.objects.create(owner_id=self.user1.id, title="Idea 2")

        response = self.client.get("/api/ideas/")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "count" in data
        assert data["count"] == 2
        assert len(data["results"]) == 2

    # --- API-IDEA.05: Filter trash ---

    def test_filter_trash(self):
        """API-IDEA.05: GET /api/ideas?filter=trash returns only trashed ideas."""
        Idea.objects.create(owner_id=self.user1.id, title="Active")
        Idea.objects.create(owner_id=self.user1.id, title="Trashed", deleted_at=timezone.now())

        response = self.client.get("/api/ideas/?filter=trash")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["title"] == "Trashed"
        assert data["results"][0]["deleted_at"] is not None

    # --- API-IDEA.06: Get idea as owner ---

    def test_get_idea_as_owner(self):
        """API-IDEA.06: GET /api/ideas/:id returns full idea state for owner."""
        idea = Idea.objects.create(owner_id=self.user1.id, title="My Idea")

        response = self.client.get(f"/api/ideas/{idea.id}/")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(idea.id)
        assert data["title"] == "My Idea"
        assert data["state"] == "open"

    # --- API-IDEA.07: Non-owner gets read-only access ---

    def test_get_idea_non_owner_read_only(self):
        """API-IDEA.07: GET /api/ideas/:id as non-owner returns 200 with read_only=True."""
        idea = Idea.objects.create(owner_id=self.user1.id, title="Private Idea")
        self._login_as(self.user2)

        response = self.client.get(f"/api/ideas/{idea.id}/")
        assert response.status_code == 200
        data = response.json()
        assert data["read_only"] is True

    # --- API-IDEA.08: Non-existent UUID ---

    def test_get_idea_not_found(self):
        """API-IDEA.08: GET /api/ideas/:invalid-uuid returns 404."""
        fake_id = str(uuid.uuid4())
        response = self.client.get(f"/api/ideas/{fake_id}/")
        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "NOT_FOUND"

    # --- API-IDEA.11: Soft delete ---

    def test_soft_delete(self):
        """API-IDEA.11: DELETE /api/ideas/:id sets deleted_at, returns 200."""
        idea = Idea.objects.create(owner_id=self.user1.id, title="Delete Me")

        response = self.client.delete(f"/api/ideas/{idea.id}/")
        assert response.status_code == 200

        idea.refresh_from_db()
        assert idea.deleted_at is not None

    # --- API-IDEA.12: Restore from trash ---

    def test_restore_from_trash(self):
        """API-IDEA.12: POST /api/ideas/:id/restore clears deleted_at, returns 200."""
        idea = Idea.objects.create(
            owner_id=self.user1.id, title="Restore Me", deleted_at=timezone.now()
        )

        response = self.client.post(f"/api/ideas/{idea.id}/restore")
        assert response.status_code == 200

        idea.refresh_from_db()
        assert idea.deleted_at is None

    # --- T-9.3.01: Soft delete moves to trash ---

    def test_soft_delete_appears_in_trash(self):
        """T-9.3.01: Soft delete sets deleted_at, idea appears in trash list."""
        idea = Idea.objects.create(owner_id=self.user1.id, title="Trash Test")

        self.client.delete(f"/api/ideas/{idea.id}/")

        response = self.client.get("/api/ideas/?filter=trash")
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["id"] == str(idea.id)

    # --- T-9.3.02: Restore clears deleted_at ---

    def test_restore_clears_deleted_at(self):
        """T-9.3.02: POST /api/ideas/:id/restore clears deleted_at."""
        idea = Idea.objects.create(
            owner_id=self.user1.id, title="Restore Check", deleted_at=timezone.now()
        )

        self.client.post(f"/api/ideas/{idea.id}/restore")

        idea.refresh_from_db()
        assert idea.deleted_at is None

        # Verify it no longer appears in trash
        response = self.client.get("/api/ideas/?filter=trash")
        data = response.json()
        assert data["count"] == 0

    # --- T-9.4.01: Search by title ---

    def test_search_by_title(self):
        """T-9.4.01: GET /api/ideas?search=keyword returns filtered results."""
        Idea.objects.create(owner_id=self.user1.id, title="Machine Learning Project")
        Idea.objects.create(owner_id=self.user1.id, title="Web Development")

        response = self.client.get("/api/ideas/?search=machine")
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["title"] == "Machine Learning Project"

    # --- T-9.4.02: Filter by state ---

    def test_filter_by_state(self):
        """T-9.4.02: GET /api/ideas?state=open returns only open ideas."""
        Idea.objects.create(owner_id=self.user1.id, title="Open Idea", state="open")
        Idea.objects.create(owner_id=self.user1.id, title="Review Idea", state="in_review")

        response = self.client.get("/api/ideas/?state=open")
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["title"] == "Open Idea"

    # --- Ownership filter tests ---

    def test_filter_my_ideas(self):
        """GET /api/ideas?filter=my_ideas returns owned ideas only."""
        Idea.objects.create(owner_id=self.user1.id, title="My Idea")
        other_idea = Idea.objects.create(owner_id=self.user2.id, title="Other Idea")
        IdeaCollaborator.objects.create(idea=other_idea, user_id=self.user1.id)

        response = self.client.get("/api/ideas/?filter=my_ideas")
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["title"] == "My Idea"

    def test_filter_collaborating(self):
        """GET /api/ideas?filter=collaborating returns only collaborating ideas."""
        Idea.objects.create(owner_id=self.user1.id, title="My Idea")
        other_idea = Idea.objects.create(owner_id=self.user2.id, title="Collab Idea")
        IdeaCollaborator.objects.create(idea=other_idea, user_id=self.user1.id)

        response = self.client.get("/api/ideas/?filter=collaborating")
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["title"] == "Collab Idea"

    def test_unauthenticated_list_returns_401(self):
        """Unauthenticated GET /api/ideas returns 401."""
        client = APIClient()
        response = client.get("/api/ideas/")
        assert response.status_code == 401
