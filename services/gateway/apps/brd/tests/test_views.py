import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.brd.models import BrdDraft
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
class TestBrdDraftAPI(TestCase):
    """Integration tests for BRD Draft GET/PATCH API."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = _create_user(USER_1_ID, "brd1@test.local", "Brd User1")
        self.user2 = _create_user(USER_2_ID, "brd2@test.local", "Brd User2")
        self.user3 = _create_user(USER_3_ID, "brd3@test.local", "Brd User3")
        self.idea = Idea.objects.create(owner_id=self.user1.id)
        self._login_as(self.user1)

    def _login_as(self, user: User):
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(user.id)},
            format="json",
        )

    def _url(self, idea_id=None):
        return f"/api/ideas/{idea_id or self.idea.id}/brd"

    # --- API-4.01: GET returns all BRD fields ---

    def test_get_returns_all_fields(self):
        """API-4.01: GET /api/ideas/:id/brd returns 200 with all fields."""
        response = self.client.get(self._url())
        assert response.status_code == 200
        data = response.json()
        assert data["idea_id"] == str(self.idea.id)
        assert data["section_title"] is None
        assert data["section_short_description"] is None
        assert data["section_current_workflow"] is None
        assert data["section_affected_department"] is None
        assert data["section_core_capabilities"] is None
        assert data["section_success_criteria"] is None
        assert data["section_locks"] == {}
        assert data["allow_information_gaps"] is False
        assert data["readiness_evaluation"] == {}
        assert data["last_evaluated_at"] is None

    def test_get_creates_empty_draft_if_none(self):
        """GET creates empty BRD draft on first access."""
        assert not BrdDraft.objects.filter(idea_id=self.idea.id).exists()
        response = self.client.get(self._url())
        assert response.status_code == 200
        assert BrdDraft.objects.filter(idea_id=self.idea.id).exists()

    def test_get_returns_existing_draft(self):
        """GET returns existing draft data."""
        BrdDraft.objects.create(
            idea_id=self.idea.id,
            section_title="My Title",
            section_locks={"title": True},
            readiness_evaluation={"title": "ready"},
        )
        response = self.client.get(self._url())
        assert response.status_code == 200
        data = response.json()
        assert data["section_title"] == "My Title"
        assert data["section_locks"] == {"title": True}
        assert data["readiness_evaluation"] == {"title": "ready"}

    # --- API-4.02: PATCH updates sections ---

    def test_patch_updates_section(self):
        """API-4.02: PATCH updates section content."""
        response = self.client.patch(
            self._url(),
            {"section_title": "Updated Title"},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["section_title"] == "Updated Title"

    # --- API-4.03: Auto-lock on edit ---

    def test_auto_lock_on_section_edit(self):
        """API-4.03: PATCH section_title auto-locks that section."""
        response = self.client.patch(
            self._url(),
            {"section_title": "New Title"},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["section_locks"]["title"] is True

    def test_auto_lock_on_current_workflow_edit(self):
        """API-4.03: PATCH section_current_workflow auto-locks current_workflow."""
        response = self.client.patch(
            self._url(),
            {"section_current_workflow": "Current workflow text"},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["section_locks"]["current_workflow"] is True

    def test_auto_lock_multiple_sections(self):
        """Editing multiple sections auto-locks all of them."""
        response = self.client.patch(
            self._url(),
            {
                "section_title": "Title",
                "section_core_capabilities": "Capabilities",
            },
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["section_locks"]["title"] is True
        assert data["section_locks"]["core_capabilities"] is True

    # --- T-4.4.02: Lock toggle works ---

    def test_lock_toggle(self):
        """T-4.4.02: PATCH section_locks toggles lock."""
        response = self.client.patch(
            self._url(),
            {"section_locks": {"core_capabilities": True}},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["section_locks"]["core_capabilities"] is True

        # Unlock
        response = self.client.patch(
            self._url(),
            {"section_locks": {"core_capabilities": False}},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["section_locks"]["core_capabilities"] is False

    # --- T-4.9.02: Gaps toggle persists ---

    def test_gaps_toggle(self):
        """T-4.9.02: PATCH allow_information_gaps toggles and persists."""
        response = self.client.patch(
            self._url(),
            {"allow_information_gaps": True},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["allow_information_gaps"] is True

        # Verify persistence
        response = self.client.get(self._url())
        assert response.json()["allow_information_gaps"] is True

    # --- API-4.04: 403 if not collaborator ---

    def test_get_403_if_not_collaborator(self):
        """API-4.04: GET returns 403 if user is not owner/co-owner/collaborator."""
        self._login_as(self.user2)
        response = self.client.get(self._url())
        assert response.status_code == 403

    def test_patch_403_if_not_collaborator(self):
        """PATCH returns 403 if user is not owner/co-owner/collaborator."""
        self._login_as(self.user2)
        response = self.client.patch(
            self._url(),
            {"section_title": "Hacked"},
            format="json",
        )
        assert response.status_code == 403

    # --- 404 if idea not found ---

    def test_get_404_if_idea_not_found(self):
        """GET returns 404 for non-existent idea."""
        fake_id = uuid.uuid4()
        response = self.client.get(self._url(idea_id=fake_id))
        assert response.status_code == 404

    def test_get_404_for_invalid_uuid(self):
        """GET returns 404 for invalid UUID."""
        response = self.client.get("/api/ideas/not-a-uuid/brd")
        assert response.status_code == 404

    # --- Collaborator access ---

    def test_collaborator_can_access(self):
        """Collaborator can GET BRD draft."""
        IdeaCollaborator.objects.create(idea=self.idea, user_id=self.user3.id)
        self._login_as(self.user3)
        response = self.client.get(self._url())
        assert response.status_code == 200

    def test_co_owner_can_access(self):
        """Co-owner can GET BRD draft."""
        self.idea.co_owner_id = self.user2.id
        self.idea.save(update_fields=["co_owner_id"])
        self._login_as(self.user2)
        response = self.client.get(self._url())
        assert response.status_code == 200

    # --- Readiness evaluation is read-only ---

    def test_readiness_evaluation_not_writable(self):
        """readiness_evaluation cannot be set via PATCH (ignored field)."""
        response = self.client.patch(
            self._url(),
            {"allow_information_gaps": True},
            format="json",
        )
        assert response.status_code == 200
        # readiness_evaluation stays empty — only AI can update it
        data = response.json()
        assert data["readiness_evaluation"] == {}

    # --- Empty PATCH body rejected ---

    def test_empty_patch_returns_400(self):
        """PATCH with empty body returns 400."""
        response = self.client.patch(
            self._url(),
            {},
            format="json",
        )
        assert response.status_code == 400
