"""Tests for Manual Merge — US-003: UUID/URL Entry."""

import uuid
from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.ideas.models import Idea
from apps.review.models import ReviewAssignment
from apps.similarity.models import MergeRequest

USER_1_ID = uuid.UUID("00000000-0000-0000-0000-000000003001")
USER_2_ID = uuid.UUID("00000000-0000-0000-0000-000000003002")
USER_3_ID = uuid.UUID("00000000-0000-0000-0000-000000003003")
REVIEWER_ID = uuid.UUID("00000000-0000-0000-0000-000000003004")


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
@patch("apps.ideas.views._publish_event")
class TestManualMergeViaUUID(TestCase):
    """T-5.8.01: Manual merge request with valid target UUID."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = _create_user(USER_1_ID, "mm1@test.local", "Manual User1")
        self.user2 = _create_user(USER_2_ID, "mm2@test.local", "Manual User2")
        self.idea_a = Idea.objects.create(owner_id=self.user1.id, title="My Idea A")
        self.idea_b = Idea.objects.create(owner_id=self.user2.id, title="Target Idea B")
        self._login_as(self.user1)

    def _login_as(self, user: User):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    def test_manual_merge_via_uuid(self, mock_publish):
        """T-5.8.01: POST with target_idea_id returns 201 and creates merge request."""
        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_id": str(self.idea_b.id)},
            format="json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["merge_type"] == "merge"
        assert data["status"] == "pending"
        assert data["requesting_owner_consent"] == "accepted"
        assert data["target_owner_consent"] == "pending"

    def test_manual_merge_via_url(self, mock_publish):
        """Manual merge request with target_idea_url extracts UUID and creates request."""
        url = f"https://app.ziqreq.com/idea/{self.idea_b.id}"
        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_url": url},
            format="json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["target_idea_id"] == str(self.idea_b.id)
        assert data["manual_request"] is True

    def test_manual_merge_via_url_sets_manual_flag(self, mock_publish):
        """Manual merge via URL sets manual_request=True on the MergeRequest."""
        url = f"https://app.ziqreq.com/idea/{self.idea_b.id}"
        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_url": url},
            format="json",
        )
        assert response.status_code == 201
        mr = MergeRequest.objects.get(id=response.json()["id"])
        assert mr.manual_request is True

    def test_uuid_direct_not_manual(self, mock_publish):
        """Regular UUID-based request has manual_request=False."""
        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_id": str(self.idea_b.id)},
            format="json",
        )
        assert response.status_code == 201
        mr = MergeRequest.objects.get(id=response.json()["id"])
        assert mr.manual_request is False

    def test_publishes_merge_request_created_event(self, mock_publish):
        """Publishes merge_request.created event for merge type."""
        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_id": str(self.idea_b.id)},
            format="json",
        )
        assert response.status_code == 201
        mock_publish.assert_called_once()
        assert mock_publish.call_args[0][0] == "notification.similarity.merge_request_created"

    def test_auto_detect_append_for_in_review_target(self, mock_publish):
        """Auto-detects merge_type='append' for in_review target via URL."""
        reviewer = _create_user(REVIEWER_ID, "rev@test.local", "Reviewer One")
        in_review_idea = Idea.objects.create(
            owner_id=self.user2.id, title="In Review Idea", state="in_review"
        )
        ReviewAssignment.objects.create(
            idea_id=in_review_idea.id, reviewer_id=reviewer.id, assigned_by="submitter"
        )
        url = f"https://app.ziqreq.com/idea/{in_review_idea.id}"
        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_url": url},
            format="json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["merge_type"] == "append"
        assert data["reviewer_consent"] == "pending"
        assert data["manual_request"] is True

    def test_bypasses_declined_pairs(self, mock_publish):
        """Manual merge request bypasses permanent dismissal (declined pairs OK)."""
        # Create a declined merge request for this pair
        MergeRequest.objects.create(
            requesting_idea_id=self.idea_a.id,
            target_idea_id=self.idea_b.id,
            merge_type="merge",
            requested_by=self.user1.id,
            status="declined",
            requesting_owner_consent="accepted",
            target_owner_consent="declined",
        )
        # Now submit a manual merge request for same pair — should succeed
        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_id": str(self.idea_b.id)},
            format="json",
        )
        assert response.status_code == 201


@override_settings(DEBUG=True, AUTH_BYPASS=True)
@patch("apps.ideas.views._publish_event")
class TestManualMergeInvalidUUID(TestCase):
    """T-5.8.02: Manual merge with invalid/non-existent UUID."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = _create_user(USER_1_ID, "mm1@test.local", "Manual User1")
        self.idea_a = Idea.objects.create(owner_id=self.user1.id, title="My Idea A")
        self._login_as(self.user1)

    def _login_as(self, user: User):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    def test_404_target_not_found(self, mock_publish):
        """T-5.8.02: Non-existent UUID returns 404 TARGET_NOT_FOUND."""
        non_existent = str(uuid.uuid4())
        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_id": non_existent},
            format="json",
        )
        assert response.status_code == 404
        assert response.json()["error"] == "TARGET_NOT_FOUND"

    def test_400_invalid_url(self, mock_publish):
        """Invalid URL returns 400 INVALID_UUID."""
        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_url": "https://app.ziqreq.com/idea/not-a-uuid"},
            format="json",
        )
        assert response.status_code == 400
        assert response.json()["error"] == "INVALID_UUID"

    def test_400_invalid_state_deleted_target(self, mock_publish):
        """Soft-deleted target returns 404 TARGET_NOT_FOUND."""
        user2 = _create_user(USER_2_ID, "mm2@test.local", "Manual User2")
        from django.utils import timezone

        deleted_idea = Idea.objects.create(
            owner_id=user2.id, title="Deleted Idea", deleted_at=timezone.now()
        )
        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_id": str(deleted_idea.id)},
            format="json",
        )
        assert response.status_code == 404
        assert response.json()["error"] == "TARGET_NOT_FOUND"

    def test_400_invalid_state_accepted_target(self, mock_publish):
        """Target with state='accepted' returns 400 INVALID_STATE."""
        user2 = _create_user(USER_2_ID, "mm2@test.local", "Manual User2")
        accepted_idea = Idea.objects.create(
            owner_id=user2.id, title="Accepted Idea", state="accepted"
        )
        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_id": str(accepted_idea.id)},
            format="json",
        )
        assert response.status_code == 400
        assert response.json()["error"] == "INVALID_STATE"


@override_settings(DEBUG=True, AUTH_BYPASS=True)
@patch("apps.ideas.views._publish_event")
class TestManualMergeSelf(TestCase):
    """T-5.8.03: Manual merge targeting same idea."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = _create_user(USER_1_ID, "mm1@test.local", "Manual User1")
        self.idea_a = Idea.objects.create(owner_id=self.user1.id, title="My Idea A")
        self._login_as(self.user1)

    def _login_as(self, user: User):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    def test_400_cannot_merge_self(self, mock_publish):
        """T-5.8.03: Targeting same idea returns 400 CANNOT_MERGE_SELF."""
        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_id": str(self.idea_a.id)},
            format="json",
        )
        assert response.status_code == 400
        assert response.json()["error"] == "CANNOT_MERGE_SELF"

    def test_400_cannot_merge_self_via_url(self, mock_publish):
        """Targeting same idea via URL returns 400 CANNOT_MERGE_SELF."""
        url = f"https://app.ziqreq.com/idea/{self.idea_a.id}"
        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_url": url},
            format="json",
        )
        assert response.status_code == 400
        assert response.json()["error"] == "CANNOT_MERGE_SELF"
