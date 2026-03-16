import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.collaboration.models import CollaborationInvitation
from apps.projects.models import Project, ProjectCollaborator

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
class TestSendInvitation(TestCase):
    """API-INVITE.01: POST /api/projects/:id/collaborators/invite — owner sends invitation."""

    def setUp(self):
        self.client = APIClient()
        self.owner = _create_user(USER_1_ID, "owner@test.local", "Owner User")
        self.invitee = _create_user(USER_2_ID, "invitee@test.local", "Invitee User")
        self.other = _create_user(USER_3_ID, "other@test.local", "Other User")
        self.project = Project.objects.create(owner_id=self.owner.id, title="Test Project")
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.owner.id)},
            format="json",
        )

    def test_send_invitation_success(self):
        response = self.client.post(
            f"/api/projects/{self.project.id}/collaborators/invite",
            {"invitee_id": str(self.invitee.id)},
            format="json",
        )
        assert response.status_code == 201
        data = response.json()
        assert "invitation_id" in data
        assert data["status"] == "pending"

        inv = CollaborationInvitation.objects.get(id=data["invitation_id"])
        assert inv.project_id == self.project.id
        assert inv.inviter_id == self.owner.id
        assert inv.invitee_id == self.invitee.id
        assert inv.status == "pending"

    def test_non_owner_cannot_invite(self):
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.invitee.id)},
            format="json",
        )
        response = self.client.post(
            f"/api/projects/{self.project.id}/collaborators/invite",
            {"invitee_id": str(self.other.id)},
            format="json",
        )
        assert response.status_code == 403

    def test_cannot_self_invite(self):
        response = self.client.post(
            f"/api/projects/{self.project.id}/collaborators/invite",
            {"invitee_id": str(self.owner.id)},
            format="json",
        )
        assert response.status_code == 400

    def test_cannot_invite_existing_collaborator(self):
        ProjectCollaborator.objects.create(project=self.project, user_id=self.invitee.id)
        response = self.client.post(
            f"/api/projects/{self.project.id}/collaborators/invite",
            {"invitee_id": str(self.invitee.id)},
            format="json",
        )
        assert response.status_code == 400

    def test_cannot_duplicate_pending_invitation(self):
        self.client.post(
            f"/api/projects/{self.project.id}/collaborators/invite",
            {"invitee_id": str(self.invitee.id)},
            format="json",
        )
        response = self.client.post(
            f"/api/projects/{self.project.id}/collaborators/invite",
            {"invitee_id": str(self.invitee.id)},
            format="json",
        )
        assert response.status_code == 400

    def test_idea_not_found(self):
        fake_id = uuid.uuid4()
        response = self.client.post(
            f"/api/projects/{fake_id}/collaborators/invite",
            {"invitee_id": str(self.invitee.id)},
            format="json",
        )
        assert response.status_code == 404


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestAcceptInvitation(TestCase):
    """API-INVITE.02: POST /api/invitations/:id/accept — invitee accepts."""

    def setUp(self):
        self.client = APIClient()
        self.owner = _create_user(USER_1_ID, "owner@test.local", "Owner User")
        self.invitee = _create_user(USER_2_ID, "invitee@test.local", "Invitee User")
        self.project = Project.objects.create(
            owner_id=self.owner.id, title="Test Project", visibility="private"
        )
        self.invitation = CollaborationInvitation.objects.create(
            project_id=self.project.id,
            inviter_id=self.owner.id,
            invitee_id=self.invitee.id,
            status="pending",
        )
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.invitee.id)},
            format="json",
        )

    def test_accept_invitation_success(self):
        response = self.client.post(f"/api/invitations/{self.invitation.id}/accept")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Invitation accepted"

        self.invitation.refresh_from_db()
        assert self.invitation.status == "accepted"
        assert self.invitation.responded_at is not None

        assert ProjectCollaborator.objects.filter(
            project_id=self.project.id, user_id=self.invitee.id
        ).exists()

    def test_first_accept_transitions_visibility(self):
        self.client.post(f"/api/invitations/{self.invitation.id}/accept")
        self.project.refresh_from_db()
        assert self.project.visibility == "collaborating"

    def test_non_invitee_cannot_accept(self):
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.owner.id)},
            format="json",
        )
        response = self.client.post(f"/api/invitations/{self.invitation.id}/accept")
        assert response.status_code == 403

    def test_cannot_accept_non_pending(self):
        self.invitation.status = "declined"
        self.invitation.save()
        response = self.client.post(f"/api/invitations/{self.invitation.id}/accept")
        assert response.status_code == 400


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestDeclineInvitation(TestCase):
    """API-INVITE.03: POST /api/invitations/:id/decline — invitee declines."""

    def setUp(self):
        self.client = APIClient()
        self.owner = _create_user(USER_1_ID, "owner@test.local", "Owner User")
        self.invitee = _create_user(USER_2_ID, "invitee@test.local", "Invitee User")
        self.project = Project.objects.create(owner_id=self.owner.id, title="Test Project")
        self.invitation = CollaborationInvitation.objects.create(
            project_id=self.project.id,
            inviter_id=self.owner.id,
            invitee_id=self.invitee.id,
            status="pending",
        )
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.invitee.id)},
            format="json",
        )

    def test_decline_invitation_success(self):
        response = self.client.post(f"/api/invitations/{self.invitation.id}/decline")
        assert response.status_code == 200

        self.invitation.refresh_from_db()
        assert self.invitation.status == "declined"
        assert self.invitation.responded_at is not None

    def test_non_invitee_cannot_decline(self):
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.owner.id)},
            format="json",
        )
        response = self.client.post(f"/api/invitations/{self.invitation.id}/decline")
        assert response.status_code == 403


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestRevokeInvitation(TestCase):
    """API-INVITE.04: POST /api/invitations/:id/revoke — owner revokes."""

    def setUp(self):
        self.client = APIClient()
        self.owner = _create_user(USER_1_ID, "owner@test.local", "Owner User")
        self.invitee = _create_user(USER_2_ID, "invitee@test.local", "Invitee User")
        self.project = Project.objects.create(owner_id=self.owner.id, title="Test Project")
        self.invitation = CollaborationInvitation.objects.create(
            project_id=self.project.id,
            inviter_id=self.owner.id,
            invitee_id=self.invitee.id,
            status="pending",
        )
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.owner.id)},
            format="json",
        )

    def test_revoke_invitation_success(self):
        response = self.client.post(f"/api/invitations/{self.invitation.id}/revoke")
        assert response.status_code == 200

        self.invitation.refresh_from_db()
        assert self.invitation.status == "revoked"
        assert self.invitation.responded_at is not None

    def test_non_inviter_cannot_revoke(self):
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.invitee.id)},
            format="json",
        )
        response = self.client.post(f"/api/invitations/{self.invitation.id}/revoke")
        assert response.status_code == 403


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestReInviteAfterDecline(TestCase):
    """API-INVITE.05: Re-inviting after decline creates new pending invitation."""

    def setUp(self):
        self.client = APIClient()
        self.owner = _create_user(USER_1_ID, "owner@test.local", "Owner User")
        self.invitee = _create_user(USER_2_ID, "invitee@test.local", "Invitee User")
        self.project = Project.objects.create(owner_id=self.owner.id, title="Test Project")
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.owner.id)},
            format="json",
        )

    def test_reinvite_after_decline(self):
        # First invitation
        resp1 = self.client.post(
            f"/api/projects/{self.project.id}/collaborators/invite",
            {"invitee_id": str(self.invitee.id)},
            format="json",
        )
        assert resp1.status_code == 201
        inv_id = resp1.json()["invitation_id"]

        # Decline as invitee
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.invitee.id)},
            format="json",
        )
        resp_decline = self.client.post(f"/api/invitations/{inv_id}/decline")
        assert resp_decline.status_code == 200

        # Re-invite as owner
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.owner.id)},
            format="json",
        )
        resp2 = self.client.post(
            f"/api/projects/{self.project.id}/collaborators/invite",
            {"invitee_id": str(self.invitee.id)},
            format="json",
        )
        assert resp2.status_code == 201
        assert resp2.json()["invitation_id"] != inv_id

        assert CollaborationInvitation.objects.filter(
            project_id=self.project.id,
            invitee_id=self.invitee.id,
            status="pending",
        ).count() == 1
