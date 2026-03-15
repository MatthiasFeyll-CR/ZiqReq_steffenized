import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.collaboration.models import CollaborationInvitation
from apps.ideas.models import Idea, IdeaCollaborator

USER_1_ID = uuid.UUID("00000000-0000-0000-0000-000000000011")
USER_2_ID = uuid.UUID("00000000-0000-0000-0000-000000000012")
USER_3_ID = uuid.UUID("00000000-0000-0000-0000-000000000013")


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
class TestVisibilityDefaults(TestCase):
    """T-8.1.01: New ideas default to 'private', first accept transitions to 'collaborating'."""

    def setUp(self):
        self.client = APIClient()
        self.owner = _create_user(USER_1_ID, "vis-owner@test.local", "Vis Owner")
        self.invitee = _create_user(USER_2_ID, "vis-invitee@test.local", "Vis Invitee")
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.owner.id)},
            format="json",
        )

    def test_new_idea_defaults_to_private(self):
        response = self.client.post(
            "/api/ideas/",
            {"first_message": "Hello world"},
            format="json",
        )
        assert response.status_code == 201
        idea_id = response.json()["id"]
        idea = Idea.objects.get(id=idea_id)
        assert idea.visibility == "private"

    def test_first_accept_transitions_to_collaborating(self):
        idea = Idea.objects.create(owner_id=self.owner.id, title="Test", visibility="private")
        invitation = CollaborationInvitation.objects.create(
            idea_id=idea.id,
            inviter_id=self.owner.id,
            invitee_id=self.invitee.id,
            status="pending",
        )

        # Accept as invitee
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.invitee.id)},
            format="json",
        )
        response = self.client.post(f"/api/invitations/{invitation.id}/accept")
        assert response.status_code == 200

        idea.refresh_from_db()
        assert idea.visibility == "collaborating"

    def test_second_accept_does_not_change_visibility(self):
        idea = Idea.objects.create(owner_id=self.owner.id, title="Test", visibility="private")

        # First invitation + accept
        inv1 = CollaborationInvitation.objects.create(
            idea_id=idea.id,
            inviter_id=self.owner.id,
            invitee_id=self.invitee.id,
            status="pending",
        )
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.invitee.id)},
            format="json",
        )
        self.client.post(f"/api/invitations/{inv1.id}/accept")
        idea.refresh_from_db()
        assert idea.visibility == "collaborating"

        # Second invitation + accept (different user)
        user3 = _create_user(USER_3_ID, "vis-third@test.local", "Vis Third")
        inv2 = CollaborationInvitation.objects.create(
            idea_id=idea.id,
            inviter_id=self.owner.id,
            invitee_id=user3.id,
            status="pending",
        )
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(user3.id)},
            format="json",
        )
        self.client.post(f"/api/invitations/{inv2.id}/accept")
        idea.refresh_from_db()
        assert idea.visibility == "collaborating"


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestVisibilityNoRevert(TestCase):
    """T-8.1.02: Removing all collaborators does NOT revert to 'private'. Visibility is read-only."""

    def setUp(self):
        self.client = APIClient()
        self.owner = _create_user(USER_1_ID, "vis-owner@test.local", "Vis Owner")
        self.invitee = _create_user(USER_2_ID, "vis-invitee@test.local", "Vis Invitee")
        self.idea = Idea.objects.create(
            owner_id=self.owner.id, title="Collab Idea", visibility="collaborating"
        )
        IdeaCollaborator.objects.create(idea=self.idea, user_id=self.invitee.id)
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.owner.id)},
            format="json",
        )

    def test_removing_all_collaborators_keeps_collaborating(self):
        response = self.client.delete(
            f"/api/ideas/{self.idea.id}/collaborators/{self.invitee.id}"
        )
        assert response.status_code == 204

        # Verify no collaborators remain
        assert IdeaCollaborator.objects.filter(idea_id=self.idea.id).count() == 0

        # Visibility must still be 'collaborating'
        self.idea.refresh_from_db()
        assert self.idea.visibility == "collaborating"

    def test_collaborator_leaving_keeps_collaborating(self):
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.invitee.id)},
            format="json",
        )
        response = self.client.post(f"/api/ideas/{self.idea.id}/leave")
        assert response.status_code == 200

        assert IdeaCollaborator.objects.filter(idea_id=self.idea.id).count() == 0

        self.idea.refresh_from_db()
        assert self.idea.visibility == "collaborating"

    def test_visibility_cannot_be_set_via_patch(self):
        response = self.client.patch(
            f"/api/ideas/{self.idea.id}/",
            {"visibility": "private"},
            format="json",
        )
        assert response.status_code == 400
        assert "Visibility cannot be manually set" in response.json()["message"]

        self.idea.refresh_from_db()
        assert self.idea.visibility == "collaborating"
