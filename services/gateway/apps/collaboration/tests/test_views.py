import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.collaboration.models import CollaborationInvitation
from apps.projects.models import Project

USER_1_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
USER_2_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
USER_3_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")


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
class TestInvitationsList(TestCase):
    """Integration tests for GET /api/invitations."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = _create_user(USER_1_ID, "user1@test.local", "Test User1")
        self.user2 = _create_user(USER_2_ID, "user2@test.local", "Test User2")
        self.user3 = _create_user(USER_3_ID, "user3@test.local", "Test User3")
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.user1.id)},
            format="json",
        )

    def test_list_pending_invitations(self):
        """GET /api/invitations returns pending invitations for current user."""
        project = Project.objects.create(owner_id=self.user2.id, title="Cool Project")
        CollaborationInvitation.objects.create(
            project_id=project.id,
            inviter_id=self.user2.id,
            invitee_id=self.user1.id,
            status="pending",
        )

        response = self.client.get("/api/invitations/")
        assert response.status_code == 200
        data = response.json()
        assert "invitations" in data
        assert len(data["invitations"]) == 1

        inv = data["invitations"][0]
        assert "id" in inv
        assert inv["project_id"] == str(project.id)
        assert inv["project_title"] == "Cool Project"
        assert inv["inviter"]["id"] == str(self.user2.id)
        assert inv["inviter"]["display_name"] == "Test User2"
        assert "created_at" in inv

    def test_only_pending_returned(self):
        """Only pending invitations are returned, not accepted/declined/revoked."""
        project = Project.objects.create(owner_id=self.user2.id, title="Project A")
        CollaborationInvitation.objects.create(
            project_id=project.id,
            inviter_id=self.user2.id,
            invitee_id=self.user1.id,
            status="pending",
        )
        CollaborationInvitation.objects.create(
            project_id=project.id,
            inviter_id=self.user3.id,
            invitee_id=self.user1.id,
            status="accepted",
        )
        CollaborationInvitation.objects.create(
            project_id=project.id,
            inviter_id=self.user2.id,
            invitee_id=self.user1.id,
            status="declined",
        )

        response = self.client.get("/api/invitations/")
        data = response.json()
        assert len(data["invitations"]) == 1
        assert data["invitations"][0]["inviter"]["id"] == str(self.user2.id)

    def test_empty_list_if_no_pending(self):
        """Empty list returned when no pending invitations exist."""
        response = self.client.get("/api/invitations/")
        assert response.status_code == 200
        data = response.json()
        assert data["invitations"] == []

    def test_unauthenticated_returns_401(self):
        """Unauthenticated request returns 401."""
        client = APIClient()
        response = client.get("/api/invitations/")
        assert response.status_code == 401

    def test_does_not_return_other_users_invitations(self):
        """Invitations for other users are not returned."""
        project = Project.objects.create(owner_id=self.user3.id, title="Other Project")
        CollaborationInvitation.objects.create(
            project_id=project.id,
            inviter_id=self.user3.id,
            invitee_id=self.user2.id,
            status="pending",
        )

        response = self.client.get("/api/invitations/")
        data = response.json()
        assert len(data["invitations"]) == 0
