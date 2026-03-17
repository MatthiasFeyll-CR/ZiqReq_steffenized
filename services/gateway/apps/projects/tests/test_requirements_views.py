import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.projects.models import (
    Project,
    RequirementsDocumentDraft,
)

USER_1_ID = uuid.UUID("00000000-0000-0000-0000-000000000031")
USER_2_ID = uuid.UUID("00000000-0000-0000-0000-000000000032")


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
class TestRequirementsAPI(TestCase):
    """Integration tests for Requirements endpoints (US-002)."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = _create_user(USER_1_ID, "req1@test.local", "Req User1")
        self.user2 = _create_user(USER_2_ID, "req2@test.local", "Req User2")
        self.project = Project.objects.create(
            owner_id=self.user1.id, project_type="software"
        )
        self._login_as(self.user1)

    def _login_as(self, user: User):
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(user.id)},
            format="json",
        )

    def _url(self, suffix="", project_id=None):
        pid = project_id or self.project.id
        return f"/api/projects/{pid}/requirements/{suffix}"

    # --- GET /requirements/ ---

    def test_get_creates_empty_draft(self):
        response = self.client.get(self._url())
        assert response.status_code == 200
        data = response.json()
        assert data["structure"] == []
        assert data["item_locks"] == {}
        assert data["allow_information_gaps"] is False

    def test_get_returns_existing_draft(self):
        RequirementsDocumentDraft.objects.create(
            project=self.project,
            title="My Reqs",
            structure=[{"id": "test", "type": "epic", "title": "E1", "children": []}],
        )
        response = self.client.get(self._url())
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "My Reqs"
        assert len(data["structure"]) == 1

    # --- PATCH /requirements/ ---

    def test_patch_title(self):
        response = self.client.patch(
            self._url(),
            {"title": "Updated Title"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    def test_patch_403_for_non_collaborator(self):
        self._login_as(self.user2)
        response = self.client.patch(
            self._url(),
            {"title": "Hacked"},
            format="json",
        )
        assert response.status_code == 403

    # --- POST /requirements/items ---

    def test_add_epic_to_software_project(self):
        """API-3.01: Add epic to software project returns 201."""
        response = self.client.post(
            self._url("items"),
            {"title": "Auth Epic", "description": "Authentication features", "type": "epic"},
            format="json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "epic"
        assert data["title"] == "Auth Epic"
        assert "id" in data

    def test_add_milestone_to_non_software_project(self):
        self.project.project_type = "non_software"
        self.project.save(update_fields=["project_type"])
        response = self.client.post(
            self._url("items"),
            {"title": "Phase 1", "type": "milestone"},
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["type"] == "milestone"

    def test_add_wrong_type_returns_400(self):
        response = self.client.post(
            self._url("items"),
            {"title": "Wrong", "type": "milestone"},
            format="json",
        )
        assert response.status_code == 400

    def test_add_item_403_for_non_collaborator(self):
        self._login_as(self.user2)
        response = self.client.post(
            self._url("items"),
            {"title": "Nope", "type": "epic"},
            format="json",
        )
        assert response.status_code == 403

    # --- PATCH/DELETE /requirements/items/:item_id ---

    def _add_epic(self):
        response = self.client.post(
            self._url("items"),
            {"title": "Epic", "type": "epic"},
            format="json",
        )
        return response.json()["id"]

    def test_patch_item(self):
        item_id = self._add_epic()
        response = self.client.patch(
            self._url(f"items/{item_id}"),
            {"title": "Updated Epic"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Epic"

    def test_delete_item(self):
        item_id = self._add_epic()
        response = self.client.delete(self._url(f"items/{item_id}"))
        assert response.status_code == 204

        # Verify removed from structure
        response = self.client.get(self._url())
        assert len(response.json()["structure"]) == 0

    def test_delete_nonexistent_item_404(self):
        response = self.client.delete(self._url(f"items/{uuid.uuid4()}"))
        assert response.status_code == 404

    # --- POST /requirements/items/:item_id/children ---

    def test_add_child_to_epic(self):
        item_id = self._add_epic()
        response = self.client.post(
            self._url(f"items/{item_id}/children"),
            {
                "title": "Login Story",
                "description": "As a user...",
                "acceptance_criteria": ["Email validation"],
                "priority": "high",
            },
            format="json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "user_story"
        assert data["priority"] == "high"
        assert data["acceptance_criteria"] == ["Email validation"]

    def test_add_child_to_nonexistent_parent_404(self):
        response = self.client.post(
            self._url(f"items/{uuid.uuid4()}/children"),
            {"title": "Orphan"},
            format="json",
        )
        assert response.status_code == 404

    # --- PATCH/DELETE children ---

    def _add_epic_with_child(self):
        item_id = self._add_epic()
        resp = self.client.post(
            self._url(f"items/{item_id}/children"),
            {"title": "Story", "priority": "low"},
            format="json",
        )
        child_id = resp.json()["id"]
        return item_id, child_id

    def test_patch_child(self):
        item_id, child_id = self._add_epic_with_child()
        response = self.client.patch(
            self._url(f"items/{item_id}/children/{child_id}"),
            {"priority": "high"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["priority"] == "high"

    def test_delete_child(self):
        item_id, child_id = self._add_epic_with_child()
        response = self.client.delete(
            self._url(f"items/{item_id}/children/{child_id}")
        )
        assert response.status_code == 204

    # --- POST /requirements/reorder ---

    def test_reorder_items(self):
        """API-3.02: Reorder items returns 200."""
        id1 = self._add_epic()
        # Add a second epic
        resp2 = self.client.post(
            self._url("items"),
            {"title": "Epic 2", "type": "epic"},
            format="json",
        )
        id2 = resp2.json()["id"]

        response = self.client.post(
            self._url("reorder"),
            {"item_ids": [id2, id1]},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["structure"][0]["id"] == id2
        assert data["structure"][1]["id"] == id1

    def test_reorder_invalid_id_400(self):
        response = self.client.post(
            self._url("reorder"),
            {"item_ids": ["nonexistent"]},
            format="json",
        )
        assert response.status_code == 400

    # --- 404 for non-existent project ---

    def test_404_for_nonexistent_project(self):
        fake_id = uuid.uuid4()
        response = self.client.get(self._url(project_id=fake_id))
        assert response.status_code == 404
