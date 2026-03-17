import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.projects.models import Project, ProjectCollaborator

USER_1_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
USER_2_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
USER_3_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")
USER_4_ID = uuid.UUID("00000000-0000-0000-0000-000000000004")


def _create_user(user_id: uuid.UUID, email: str, display_name: str) -> User:
    return User.objects.create(
        id=user_id,
        email=email,
        first_name=display_name.split()[0],
        last_name=display_name.split()[-1],
        display_name=display_name,
        roles=["user"],
    )


def _login(client: APIClient, user_id: uuid.UUID):
    client.post("/api/auth/dev-login", {"user_id": str(user_id)}, format="json")


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestListCollaborators(TestCase):
    """API-COLLAB.01: GET /api/projects/:id/collaborators — list owner, co-owner, collaborators."""

    def setUp(self):
        self.client = APIClient()
        self.owner = _create_user(USER_1_ID, "owner@test.local", "Owner User")
        self.collab = _create_user(USER_2_ID, "collab@test.local", "Collab User")
        self.project = Project.objects.create(owner_id=self.owner.id, title="Test Project")
        ProjectCollaborator.objects.create(project=self.project, user_id=self.collab.id)
        _login(self.client, self.owner.id)

    def test_list_collaborators_returns_owner_and_collaborators(self):
        response = self.client.get(f"/api/projects/{self.project.id}/collaborators")
        assert response.status_code == 200
        data = response.json()
        assert data["owner"]["id"] == str(self.owner.id)
        assert len(data["collaborators"]) == 1
        assert data["collaborators"][0]["id"] == str(self.collab.id)

    def test_project_not_found(self):
        response = self.client.get(f"/api/projects/{uuid.uuid4()}/collaborators")
        assert response.status_code == 404


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestRemoveCollaborator(TestCase):
    """API-COLLAB.02: DELETE /api/projects/:id/collaborators/:userId — owner removes collaborator."""

    def setUp(self):
        self.client = APIClient()
        self.owner = _create_user(USER_1_ID, "owner@test.local", "Owner User")
        self.collab = _create_user(USER_2_ID, "collab@test.local", "Collab User")
        self.project = Project.objects.create(owner_id=self.owner.id, title="Test Project")
        ProjectCollaborator.objects.create(project=self.project, user_id=self.collab.id)
        _login(self.client, self.owner.id)

    def test_remove_collaborator_success(self):
        response = self.client.delete(
            f"/api/projects/{self.project.id}/collaborators/{self.collab.id}"
        )
        assert response.status_code == 204
        assert not ProjectCollaborator.objects.filter(
            project_id=self.project.id, user_id=self.collab.id
        ).exists()

    def test_non_owner_cannot_remove(self):
        _login(self.client, self.collab.id)
        other = _create_user(USER_3_ID, "other@test.local", "Other User")
        ProjectCollaborator.objects.create(project=self.project, user_id=other.id)
        response = self.client.delete(
            f"/api/projects/{self.project.id}/collaborators/{other.id}"
        )
        assert response.status_code == 403

    def test_remove_nonexistent_collaborator(self):
        fake_user = uuid.uuid4()
        response = self.client.delete(
            f"/api/projects/{self.project.id}/collaborators/{fake_user}"
        )
        assert response.status_code == 404


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestTransferOwnership(TestCase):
    """API-COLLAB.03: POST /api/projects/:id/transfer-ownership — transfer ownership."""

    def setUp(self):
        self.client = APIClient()
        self.owner = _create_user(USER_1_ID, "owner@test.local", "Owner User")
        self.collab = _create_user(USER_2_ID, "collab@test.local", "Collab User")
        self.project = Project.objects.create(owner_id=self.owner.id, title="Test Project")
        ProjectCollaborator.objects.create(project=self.project, user_id=self.collab.id)
        _login(self.client, self.owner.id)

    def test_transfer_ownership_success(self):
        response = self.client.post(
            f"/api/projects/{self.project.id}/transfer-ownership",
            {"new_owner_id": str(self.collab.id)},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Ownership transferred"

        self.project.refresh_from_db()
        assert self.project.owner_id == self.collab.id

        # Previous owner should be collaborator now
        assert ProjectCollaborator.objects.filter(
            project_id=self.project.id, user_id=self.owner.id
        ).exists()
        # New owner should no longer be in collaborators table
        assert not ProjectCollaborator.objects.filter(
            project_id=self.project.id, user_id=self.collab.id
        ).exists()

    def test_non_owner_cannot_transfer(self):
        _login(self.client, self.collab.id)
        response = self.client.post(
            f"/api/projects/{self.project.id}/transfer-ownership",
            {"new_owner_id": str(self.owner.id)},
            format="json",
        )
        assert response.status_code == 403

    def test_cannot_transfer_to_self(self):
        response = self.client.post(
            f"/api/projects/{self.project.id}/transfer-ownership",
            {"new_owner_id": str(self.owner.id)},
            format="json",
        )
        assert response.status_code == 400

    def test_cannot_transfer_to_non_collaborator(self):
        other = _create_user(USER_3_ID, "other@test.local", "Other User")
        response = self.client.post(
            f"/api/projects/{self.project.id}/transfer-ownership",
            {"new_owner_id": str(other.id)},
            format="json",
        )
        assert response.status_code == 400


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestLeaveProject(TestCase):
    """API-COLLAB.04: POST /api/projects/:id/leave — collaborator/co-owner leave."""

    def setUp(self):
        self.client = APIClient()
        self.owner = _create_user(USER_1_ID, "owner@test.local", "Owner User")
        self.collab = _create_user(USER_2_ID, "collab@test.local", "Collab User")
        self.project = Project.objects.create(
            owner_id=self.owner.id, title="Test Project", visibility="collaborating"
        )
        ProjectCollaborator.objects.create(project=self.project, user_id=self.collab.id)

    def test_collaborator_can_leave(self):
        _login(self.client, self.collab.id)
        response = self.client.post(f"/api/projects/{self.project.id}/leave")
        assert response.status_code == 200
        assert response.json()["message"] == "You have left the project"
        assert not ProjectCollaborator.objects.filter(
            project_id=self.project.id, user_id=self.collab.id
        ).exists()

    def test_owner_cannot_leave(self):
        """Owner gets 400 when trying to leave."""
        _login(self.client, self.owner.id)
        response = self.client.post(f"/api/projects/{self.project.id}/leave")
        assert response.status_code == 400

    def test_non_collaborator_cannot_leave(self):
        other = _create_user(USER_4_ID, "other@test.local", "Other User")
        _login(self.client, other.id)
        response = self.client.post(f"/api/projects/{self.project.id}/leave")
        assert response.status_code == 400
