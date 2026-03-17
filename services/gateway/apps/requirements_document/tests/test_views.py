import unittest.mock
import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.projects.models import Project, ProjectCollaborator
from apps.requirements_document.models import RequirementsDocumentDraft

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
class TestRequirementsDocumentDraftAPI(TestCase):
    """Integration tests for Requirements Document Draft GET/PATCH API."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = _create_user(USER_1_ID, "req1@test.local", "Req User1")
        self.user2 = _create_user(USER_2_ID, "req2@test.local", "Req User2")
        self.user3 = _create_user(USER_3_ID, "req3@test.local", "Req User3")
        self.project = Project.objects.create(owner_id=self.user1.id)
        self._login_as(self.user1)

    def _login_as(self, user: User):
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(user.id)},
            format="json",
        )

    def _url(self, project_id=None):
        return f"/api/projects/{project_id or self.project.id}/brd/"

    def test_get_returns_all_fields(self):
        """GET /api/projects/:id/brd returns 200 with all fields."""
        response = self.client.get(self._url())
        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == str(self.project.id)
        assert data["title"] is None
        assert data["short_description"] is None
        assert data["structure"] == []
        assert data["item_locks"] == {}
        assert data["allow_information_gaps"] is False
        assert data["readiness_evaluation"] == {}
        assert data["last_evaluated_at"] is None

    def test_get_creates_empty_draft_if_none(self):
        """GET creates empty draft on first access."""
        assert not RequirementsDocumentDraft.objects.filter(project_id=self.project.id).exists()
        response = self.client.get(self._url())
        assert response.status_code == 200
        assert RequirementsDocumentDraft.objects.filter(project_id=self.project.id).exists()

    def test_get_returns_existing_draft(self):
        """GET returns existing draft data."""
        RequirementsDocumentDraft.objects.create(
            project_id=self.project.id,
            title="My Title",
            item_locks={"epic-1": True},
            readiness_evaluation={"ready": True},
        )
        response = self.client.get(self._url())
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "My Title"
        assert data["item_locks"] == {"epic-1": True}
        assert data["readiness_evaluation"] == {"ready": True}

    def test_patch_updates_title(self):
        """PATCH updates title."""
        response = self.client.patch(
            self._url(),
            {"title": "Updated Title"},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"

    def test_lock_toggle(self):
        """PATCH item_locks toggles lock."""
        response = self.client.patch(
            self._url(),
            {"item_locks": {"epic-1": True}},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["item_locks"]["epic-1"] is True

        response = self.client.patch(
            self._url(),
            {"item_locks": {"epic-1": False}},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["item_locks"]["epic-1"] is False

    def test_gaps_toggle(self):
        """PATCH allow_information_gaps toggles and persists."""
        response = self.client.patch(
            self._url(),
            {"allow_information_gaps": True},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["allow_information_gaps"] is True

        response = self.client.get(self._url())
        assert response.json()["allow_information_gaps"] is True

    def test_get_200_for_non_collaborator_read_only(self):
        """GET returns 200 for any authenticated user (read-only access)."""
        self._login_as(self.user2)
        response = self.client.get(self._url())
        assert response.status_code == 200

    def test_patch_403_if_not_collaborator(self):
        """PATCH returns 403 if user is not owner/co-owner/collaborator."""
        self._login_as(self.user2)
        response = self.client.patch(
            self._url(),
            {"title": "Hacked"},
            format="json",
        )
        assert response.status_code == 403

    def test_get_404_if_project_not_found(self):
        """GET returns 404 for non-existent project."""
        fake_id = uuid.uuid4()
        response = self.client.get(self._url(project_id=fake_id))
        assert response.status_code == 404

    def test_get_404_for_invalid_uuid(self):
        """GET returns 404 for invalid UUID."""
        response = self.client.get("/api/projects/not-a-uuid/brd/")
        assert response.status_code == 404

    def test_collaborator_can_access(self):
        """Collaborator can GET draft."""
        ProjectCollaborator.objects.create(project=self.project, user_id=self.user3.id)
        self._login_as(self.user3)
        response = self.client.get(self._url())
        assert response.status_code == 200

    def test_readiness_evaluation_not_writable(self):
        """readiness_evaluation cannot be set via PATCH (ignored field)."""
        response = self.client.patch(
            self._url(),
            {"allow_information_gaps": True},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["readiness_evaluation"] == {}

    def test_empty_patch_returns_400(self):
        """PATCH with empty body returns 400."""
        response = self.client.patch(
            self._url(),
            {},
            format="json",
        )
        assert response.status_code == 400


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestRequirementsGenerateAPI(TestCase):
    """Integration tests for POST /api/projects/:id/brd/generate."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = _create_user(
            uuid.UUID("00000000-0000-0000-0000-000000000021"),
            "gen1@test.local",
            "Gen User1",
        )
        self.user2 = _create_user(
            uuid.UUID("00000000-0000-0000-0000-000000000022"),
            "gen2@test.local",
            "Gen User2",
        )
        self.project = Project.objects.create(owner_id=self.user1.id, state="open")
        self._login_as(self.user1)

        self._ai_patcher = unittest.mock.patch("apps.requirements_document.views._create_ai_client")
        self.mock_create_ai_client = self._ai_patcher.start()
        self.mock_ai_client = self.mock_create_ai_client.return_value
        self.mock_ai_client.trigger_brd_generation.return_value = {
            "status": "accepted",
            "generation_id": "mock-gen-id",
        }

    def tearDown(self):
        self._ai_patcher.stop()

    def _login_as(self, user):
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(user.id)},
            format="json",
        )

    def _url(self, project_id=None):
        return f"/api/projects/{project_id or self.project.id}/brd/generate"

    def test_post_generate_returns_202(self):
        """POST /generate with mode='full_generation' returns 202 Accepted."""
        response = self.client.post(
            self._url(),
            {"mode": "full_generation"},
            format="json",
        )
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "accepted"

    def test_post_generate_triggers_ai(self):
        """POST /generate triggers AI service invocation."""
        response = self.client.post(
            self._url(),
            {"mode": "full_generation"},
            format="json",
        )
        assert response.status_code == 202
        self.mock_ai_client.trigger_brd_generation.assert_called_once_with(
            project_id=str(self.project.id),
            mode="full_generation",
            section_name="",
        )

    def test_post_generate_selective_regeneration(self):
        """POST /generate with selective_regeneration mode."""
        response = self.client.post(
            self._url(),
            {"mode": "selective_regeneration"},
            format="json",
        )
        assert response.status_code == 202

    def test_invalid_mode_returns_400(self):
        """Invalid mode returns 400."""
        response = self.client.post(
            self._url(),
            {"mode": "invalid_mode"},
            format="json",
        )
        assert response.status_code == 400

    def test_missing_mode_returns_400(self):
        """Missing mode field returns 400."""
        response = self.client.post(
            self._url(),
            {},
            format="json",
        )
        assert response.status_code == 400

    def test_403_if_not_collaborator(self):
        """POST returns 403 if user is not owner/co-owner/collaborator."""
        self._login_as(self.user2)
        response = self.client.post(
            self._url(),
            {"mode": "full_generation"},
            format="json",
        )
        assert response.status_code == 403

    def test_404_if_project_not_found(self):
        """POST returns 404 for non-existent project."""
        fake_id = uuid.uuid4()
        response = self.client.post(
            self._url(project_id=fake_id),
            {"mode": "full_generation"},
            format="json",
        )
        assert response.status_code == 404

    def test_non_open_project_returns_400(self):
        """POST returns 400 if project state is not 'open'."""
        self.project.state = "in_review"
        self.project.save(update_fields=["state"])
        response = self.client.post(
            self._url(),
            {"mode": "full_generation"},
            format="json",
        )
        assert response.status_code == 400
        assert response.json()["error"] == "INVALID_STATE"

    def test_grpc_failure_returns_503(self):
        """POST returns 503 if AI gRPC call fails."""
        self.mock_create_ai_client.side_effect = Exception("gRPC connection refused")
        response = self.client.post(
            self._url(),
            {"mode": "full_generation"},
            format="json",
        )
        assert response.status_code == 503
        assert response.json()["error"] == "SERVICE_UNAVAILABLE"
