"""Tests for Review Timeline API — GET Entries & POST Comments — US-004.

Test IDs: API-TIMELINE.01, API-TIMELINE.02, API-TIMELINE.03, API-TIMELINE.04, API-TIMELINE.05
"""

import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.projects.models import Project
from apps.review.models import ReviewTimelineEntry

OWNER_ID = uuid.UUID("00000000-0000-0000-0000-000000000401")
REVIEWER_ID = uuid.UUID("00000000-0000-0000-0000-000000000411")
OTHER_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000402")


def _create_user(user_id: uuid.UUID, email: str, display_name: str, roles: list[str] | None = None) -> User:
    return User.objects.create(
        id=user_id,
        email=email,
        first_name=display_name.split()[0],
        last_name=display_name.split()[-1],
        display_name=display_name,
        roles=roles or ["user"],
    )


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestReviewTimeline(TestCase):
    """Integration tests for GET/POST review timeline endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.owner = _create_user(OWNER_ID, "owner@test.local", "Project Owner")
        self.reviewer = _create_user(REVIEWER_ID, "reviewer@test.local", "Reviewer One", ["user", "reviewer"])
        self.other_user = _create_user(OTHER_USER_ID, "other@test.local", "Other User")
        self.project = Project.objects.create(owner_id=self.owner.id, state="in_review", title="Test Project")
        self._login_as(self.owner)

    def _login_as(self, user: User):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    def _url(self, project_id=None):
        return f"/api/projects/{project_id or self.project.id}/review/timeline"

    # --- API-TIMELINE.01: GET timeline success ---

    def test_get_timeline_success(self):
        """API-TIMELINE.01 | GET /api/projects/:id/review/timeline | Success.
        Input: Valid project with timeline entries.
        Expected: 200 with timeline array ordered by created_at ASC.
        """
        # Create entries of different types
        ReviewTimelineEntry.objects.create(
            project_id=self.project.id,
            entry_type="state_change",
            author_id=self.owner.id,
            content="Submitted for review",
            old_state="open",
            new_state="in_review",
        )
        ReviewTimelineEntry.objects.create(
            project_id=self.project.id,
            entry_type="comment",
            author_id=self.reviewer.id,
            content="Looks good so far",
        )
        ReviewTimelineEntry.objects.create(
            project_id=self.project.id,
            entry_type="resubmission",
            author_id=self.owner.id,
            old_version_id=uuid.uuid4(),
            new_version_id=uuid.uuid4(),
        )

        response = self.client.get(self._url())
        assert response.status_code == 200, response.json()
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

        # Check entry types
        assert data[0]["entry_type"] == "state_change"
        assert data[0]["old_state"] == "open"
        assert data[0]["new_state"] == "in_review"
        assert data[0]["content"] == "Submitted for review"

        assert data[1]["entry_type"] == "comment"
        assert data[1]["content"] == "Looks good so far"
        assert data[1]["author"]["display_name"] == "Reviewer One"

        assert data[2]["entry_type"] == "resubmission"
        assert data[2]["old_version_id"] is not None
        assert data[2]["new_version_id"] is not None

    def test_get_timeline_empty(self):
        """GET timeline returns empty array for project with no entries."""
        response = self.client.get(self._url())
        assert response.status_code == 200
        assert response.json() == []

    def test_get_timeline_ordered_asc(self):
        """Entries ordered by created_at ASC."""
        e1 = ReviewTimelineEntry.objects.create(
            project_id=self.project.id,
            entry_type="comment",
            author_id=self.owner.id,
            content="First",
        )
        e2 = ReviewTimelineEntry.objects.create(
            project_id=self.project.id,
            entry_type="comment",
            author_id=self.owner.id,
            content="Second",
        )
        response = self.client.get(self._url())
        data = response.json()
        assert data[0]["id"] == str(e1.id)
        assert data[1]["id"] == str(e2.id)

    def test_get_timeline_project_not_found(self):
        """GET timeline returns 404 for non-existent project."""
        fake_id = uuid.uuid4()
        response = self.client.get(self._url(fake_id))
        assert response.status_code == 404

    # --- API-TIMELINE.02: GET timeline access control ---

    def test_get_timeline_unauthenticated(self):
        """API-TIMELINE.02 | GET /api/projects/:id/review/timeline | Access control.
        Unauthenticated user gets 401.
        """
        self.client.logout()
        # Clear session
        self.client = APIClient()
        response = self.client.get(self._url())
        assert response.status_code == 401

    # --- API-TIMELINE.03: POST comment success ---

    def test_post_comment_success(self):
        """API-TIMELINE.03 | POST /api/projects/:id/review/timeline | Create comment.
        Input: {content: "Great project"}.
        Expected: 201 with new entry.
        """
        response = self.client.post(
            self._url(),
            {"content": "Great project"},
            format="json",
        )
        assert response.status_code == 201, response.json()
        data = response.json()
        assert data["entry_type"] == "comment"
        assert data["content"] == "Great project"
        assert data["author"]["id"] == str(self.owner.id)
        assert data["parent_entry_id"] is None

        # Verify in DB
        entry = ReviewTimelineEntry.objects.get(id=data["id"])
        assert entry.content == "Great project"
        assert entry.author_id == self.owner.id

    # --- API-TIMELINE.04: POST nested reply ---

    def test_post_nested_reply(self):
        """API-TIMELINE.04 | POST /api/projects/:id/review/timeline | Nested reply.
        Input: {content: "Reply", parent_entry_id: uuid}.
        Expected: 201 with parent link.
        """
        parent = ReviewTimelineEntry.objects.create(
            project_id=self.project.id,
            entry_type="comment",
            author_id=self.reviewer.id,
            content="Parent comment",
        )
        response = self.client.post(
            self._url(),
            {"content": "Reply to comment", "parent_entry_id": str(parent.id)},
            format="json",
        )
        assert response.status_code == 201, response.json()
        data = response.json()
        assert data["parent_entry_id"] == str(parent.id)
        assert data["content"] == "Reply to comment"

    def test_post_reply_parent_not_found(self):
        """POST with non-existent parent_entry_id returns 404."""
        fake_parent = uuid.uuid4()
        response = self.client.post(
            self._url(),
            {"content": "Reply", "parent_entry_id": str(fake_parent)},
            format="json",
        )
        assert response.status_code == 404

    def test_post_reply_parent_wrong_project(self):
        """POST with parent_entry_id from different project returns 404."""
        other_project = Project.objects.create(owner_id=self.owner.id, state="in_review", title="Other Project")
        parent = ReviewTimelineEntry.objects.create(
            project_id=other_project.id,
            entry_type="comment",
            author_id=self.owner.id,
            content="Other project comment",
        )
        response = self.client.post(
            self._url(),
            {"content": "Reply", "parent_entry_id": str(parent.id)},
            format="json",
        )
        assert response.status_code == 404

    # --- API-TIMELINE.05: POST validation ---

    def test_post_comment_empty_content(self):
        """API-TIMELINE.05 | POST /api/projects/:id/review/timeline | Validation.
        Input: Empty content.
        Expected: 400.
        """
        response = self.client.post(self._url(), {"content": ""}, format="json")
        assert response.status_code == 400

    def test_post_comment_missing_content(self):
        """POST without content field returns 400."""
        response = self.client.post(self._url(), {}, format="json")
        assert response.status_code == 400

    def test_post_comment_project_not_found(self):
        """POST comment on non-existent project returns 404."""
        fake_id = uuid.uuid4()
        response = self.client.post(
            self._url(fake_id),
            {"content": "Comment"},
            format="json",
        )
        assert response.status_code == 404

    def test_post_comment_unauthenticated(self):
        """POST comment without auth returns 401."""
        self.client = APIClient()
        response = self.client.post(
            self._url(),
            {"content": "Comment"},
            format="json",
        )
        assert response.status_code == 401

    # --- Author info in response ---

    def test_author_info_included(self):
        """Author object includes id and display_name."""
        ReviewTimelineEntry.objects.create(
            project_id=self.project.id,
            entry_type="comment",
            author_id=self.owner.id,
            content="Test",
        )
        response = self.client.get(self._url())
        data = response.json()
        assert data[0]["author"]["id"] == str(self.owner.id)
        assert data[0]["author"]["display_name"] == "Project Owner"

    def test_system_entry_null_author(self):
        """System entries (null author_id) return null author."""
        ReviewTimelineEntry.objects.create(
            project_id=self.project.id,
            entry_type="state_change",
            author_id=None,
            content="System action",
            old_state="open",
            new_state="in_review",
        )
        response = self.client.get(self._url())
        data = response.json()
        assert data[0]["author"] is None
