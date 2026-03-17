import uuid

from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.projects.models import ChatMessage, Project, ProjectCollaborator

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
class TestProjectsCRUD(TestCase):
    """Integration tests for the Projects CRUD API."""

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

    # --- API-IDEA.01: Create project with first message ---

    def test_create_project_with_first_message(self):
        """API-IDEA.01: POST /api/projects creates project, returns 201 + project object."""
        response = self.client.post(
            "/api/projects/",
            {"first_message": "My project"},
            format="json",
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["state"] == "open"
        assert data["title"] == ""
        # Verify ChatMessage was created
        project_id = data["id"]
        assert ChatMessage.objects.filter(project_id=project_id).exists()
        msg = ChatMessage.objects.get(project_id=project_id)
        assert msg.content == "My project"
        assert msg.sender_type == "user"
        assert msg.sender_id == self.user1.id

    # --- API-IDEA.02: Empty first_message validation ---

    def test_create_project_empty_first_message(self):
        """API-IDEA.02: POST /api/projects with empty first_message returns 400."""
        response = self.client.post(
            "/api/projects/",
            {"first_message": ""},
            format="json",
        )
        assert response.status_code == 400

    # --- API-IDEA.03: Unauthenticated request ---

    def test_create_project_unauthenticated(self):
        """API-IDEA.03: POST /api/projects without auth returns 401."""
        client = APIClient()  # fresh client, no session
        response = client.post(
            "/api/projects/",
            {"first_message": "My project"},
            format="json",
        )
        assert response.status_code == 401

    # --- API-IDEA.04: List user's projects ---

    def test_list_projects(self):
        """API-IDEA.04: GET /api/projects returns paginated results."""
        Project.objects.create(owner_id=self.user1.id, title="Project 1")
        Project.objects.create(owner_id=self.user1.id, title="Project 2")

        response = self.client.get("/api/projects/")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "count" in data
        assert data["count"] == 2
        assert len(data["results"]) == 2

    # --- API-IDEA.05: Filter trash ---

    def test_filter_trash(self):
        """API-IDEA.05: GET /api/projects?filter=trash returns only trashed projects."""
        Project.objects.create(owner_id=self.user1.id, title="Active")
        Project.objects.create(owner_id=self.user1.id, title="Trashed", deleted_at=timezone.now())

        response = self.client.get("/api/projects/?filter=trash")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["title"] == "Trashed"
        assert data["results"][0]["deleted_at"] is not None

    # --- API-IDEA.06: Get project as owner ---

    def test_get_project_as_owner(self):
        """API-IDEA.06: GET /api/projects/:id returns full project state for owner."""
        project = Project.objects.create(owner_id=self.user1.id, title="My Project")

        response = self.client.get(f"/api/projects/{project.id}/")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(project.id)
        assert data["title"] == "My Project"
        assert data["state"] == "open"

    # --- API-IDEA.07: Non-owner gets read-only access ---

    def test_get_project_non_owner_read_only(self):
        """API-IDEA.07: GET /api/projects/:id as non-owner returns 200 with read_only=True."""
        project = Project.objects.create(owner_id=self.user1.id, title="Private Project")
        self._login_as(self.user2)

        response = self.client.get(f"/api/projects/{project.id}/")
        assert response.status_code == 200
        data = response.json()
        assert data["read_only"] is True

    # --- API-IDEA.08: Non-existent UUID ---

    def test_get_project_not_found(self):
        """API-IDEA.08: GET /api/projects/:invalid-uuid returns 404."""
        fake_id = str(uuid.uuid4())
        response = self.client.get(f"/api/projects/{fake_id}/")
        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "NOT_FOUND"

    # --- API-IDEA.11: Soft delete ---

    def test_soft_delete(self):
        """API-IDEA.11: DELETE /api/projects/:id sets deleted_at, returns 200."""
        project = Project.objects.create(owner_id=self.user1.id, title="Delete Me")

        response = self.client.delete(f"/api/projects/{project.id}/")
        assert response.status_code == 200

        project.refresh_from_db()
        assert project.deleted_at is not None

    # --- API-IDEA.12: Restore from trash ---

    def test_restore_from_trash(self):
        """API-IDEA.12: POST /api/projects/:id/restore clears deleted_at, returns 200."""
        project = Project.objects.create(
            owner_id=self.user1.id, title="Restore Me", deleted_at=timezone.now()
        )

        response = self.client.post(f"/api/projects/{project.id}/restore")
        assert response.status_code == 200

        project.refresh_from_db()
        assert project.deleted_at is None

    # --- T-9.3.01: Soft delete moves to trash ---

    def test_soft_delete_appears_in_trash(self):
        """T-9.3.01: Soft delete sets deleted_at, project appears in trash list."""
        project = Project.objects.create(owner_id=self.user1.id, title="Trash Test")

        self.client.delete(f"/api/projects/{project.id}/")

        response = self.client.get("/api/projects/?filter=trash")
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["id"] == str(project.id)

    # --- T-9.3.02: Restore clears deleted_at ---

    def test_restore_clears_deleted_at(self):
        """T-9.3.02: POST /api/projects/:id/restore clears deleted_at."""
        project = Project.objects.create(
            owner_id=self.user1.id, title="Restore Check", deleted_at=timezone.now()
        )

        self.client.post(f"/api/projects/{project.id}/restore")

        project.refresh_from_db()
        assert project.deleted_at is None

        # Verify it no longer appears in trash
        response = self.client.get("/api/projects/?filter=trash")
        data = response.json()
        assert data["count"] == 0

    # --- T-9.4.01: Search by title ---

    def test_search_by_title(self):
        """T-9.4.01: GET /api/projects?search=keyword returns filtered results."""
        Project.objects.create(owner_id=self.user1.id, title="Machine Learning Project")
        Project.objects.create(owner_id=self.user1.id, title="Web Development")

        response = self.client.get("/api/projects/?search=machine")
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["title"] == "Machine Learning Project"

    # --- T-9.4.02: Filter by state ---

    def test_filter_by_state(self):
        """T-9.4.02: GET /api/projects?state=open returns only open projects."""
        Project.objects.create(owner_id=self.user1.id, title="Open Project", state="open")
        Project.objects.create(owner_id=self.user1.id, title="Review Project", state="in_review")

        response = self.client.get("/api/projects/?state=open")
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["title"] == "Open Project"

    # --- Ownership filter tests ---

    def test_filter_my_projects(self):
        """GET /api/projects?filter=my_projects returns owned projects only."""
        Project.objects.create(owner_id=self.user1.id, title="My Project")
        other_project = Project.objects.create(owner_id=self.user2.id, title="Other Project")
        ProjectCollaborator.objects.create(project=other_project, user_id=self.user1.id)

        response = self.client.get("/api/projects/?filter=my_projects")
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["title"] == "My Project"

    def test_filter_collaborating(self):
        """GET /api/projects?filter=collaborating returns only collaborating projects."""
        Project.objects.create(owner_id=self.user1.id, title="My Project")
        other_project = Project.objects.create(owner_id=self.user2.id, title="Collab Project")
        ProjectCollaborator.objects.create(project=other_project, user_id=self.user1.id)

        response = self.client.get("/api/projects/?filter=collaborating")
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["title"] == "Collab Project"

    def test_unauthenticated_list_returns_401(self):
        """Unauthenticated GET /api/projects returns 401."""
        client = APIClient()
        response = client.get("/api/projects/")
        assert response.status_code == 401
