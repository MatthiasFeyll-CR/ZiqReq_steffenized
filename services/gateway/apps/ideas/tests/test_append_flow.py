"""Tests for Append Flow — US-001: 3-Way Consent (requesting owner + target owner + reviewer)."""

import uuid
from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.ideas.models import Idea
from apps.review.models import ReviewAssignment
from apps.similarity.models import MergeRequest

USER_1_ID = uuid.UUID("00000000-0000-0000-0000-000000001401")
USER_2_ID = uuid.UUID("00000000-0000-0000-0000-000000001402")
USER_3_ID = uuid.UUID("00000000-0000-0000-0000-000000001403")
REVIEWER_ID = uuid.UUID("00000000-0000-0000-0000-000000001404")


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
class TestCreateAppendRequest(TestCase):
    """POST /api/ideas/:id/merge-request — append type for in_review targets."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = _create_user(USER_1_ID, "a1@test.local", "Append User1")
        self.user2 = _create_user(USER_2_ID, "a2@test.local", "Append User2")
        self.reviewer = _create_user(REVIEWER_ID, "rev@test.local", "Reviewer One")

        self.idea_a = Idea.objects.create(owner_id=self.user1.id, title="Open Idea A")
        self.idea_b = Idea.objects.create(
            owner_id=self.user2.id, title="In Review Idea B", state="in_review"
        )

        # Assign a reviewer to idea_b
        ReviewAssignment.objects.create(
            idea_id=self.idea_b.id,
            reviewer_id=self.reviewer.id,
            assigned_by="submitter",
        )

        self._login_as(self.user1)

    def _login_as(self, user: User):
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(user.id)},
            format="json",
        )

    def test_append_request_for_in_review_target(self, mock_publish):
        """Creates merge request with merge_type='append' and reviewer_consent='pending'."""
        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_id": str(self.idea_b.id)},
            format="json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["merge_type"] == "append"
        assert data["status"] == "pending"
        assert data["requesting_owner_consent"] == "accepted"
        assert data["target_owner_consent"] == "pending"
        assert data["reviewer_consent"] == "pending"

    def test_append_publishes_append_request_created(self, mock_publish):
        """Publishes append_request.created event with reviewer_ids."""
        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_id": str(self.idea_b.id)},
            format="json",
        )
        assert response.status_code == 201
        mock_publish.assert_called_once()
        call_args = mock_publish.call_args
        assert call_args[0][0] == "notification.similarity.append_request_created"
        payload = call_args[0][1]
        assert payload["requesting_idea_id"] == str(self.idea_a.id)
        assert payload["target_idea_id"] == str(self.idea_b.id)
        assert str(self.reviewer.id) in payload["reviewer_ids"]

    def test_400_reviewer_required_no_assigned_reviewers(self, mock_publish):
        """Returns 400 REVIEWER_REQUIRED if target has no assigned reviewers."""
        # Remove all reviewer assignments
        ReviewAssignment.objects.filter(idea_id=self.idea_b.id).delete()

        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_id": str(self.idea_b.id)},
            format="json",
        )
        assert response.status_code == 400
        assert response.json()["error"] == "REVIEWER_REQUIRED"

    def test_400_reviewer_required_only_unassigned_reviewers(self, mock_publish):
        """Returns 400 if all reviewers are unassigned (unassigned_at is set)."""
        from django.utils import timezone

        ReviewAssignment.objects.filter(idea_id=self.idea_b.id).update(
            unassigned_at=timezone.now()
        )

        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_id": str(self.idea_b.id)},
            format="json",
        )
        assert response.status_code == 400
        assert response.json()["error"] == "REVIEWER_REQUIRED"

    def test_merge_type_for_open_target(self, mock_publish):
        """Creates merge_type='merge' for open state target (not append)."""
        open_idea = Idea.objects.create(owner_id=self.user2.id, title="Open Idea C")
        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_id": str(open_idea.id)},
            format="json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["merge_type"] == "merge"
        assert data["reviewer_consent"] == "not_required"


@override_settings(DEBUG=True, AUTH_BYPASS=True)
@patch("apps.ideas.views._publish_event")
class TestAppendConsentFlow(TestCase):
    """POST /api/merge-requests/:id/consent — 3-way consent for append type."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = _create_user(USER_1_ID, "a1@test.local", "Append User1")
        self.user2 = _create_user(USER_2_ID, "a2@test.local", "Append User2")
        self.user3 = _create_user(USER_3_ID, "a3@test.local", "Append User3")
        self.reviewer = _create_user(REVIEWER_ID, "rev@test.local", "Reviewer One")

        self.idea_a = Idea.objects.create(owner_id=self.user1.id, title="Open Idea A")
        self.idea_b = Idea.objects.create(
            owner_id=self.user2.id, title="In Review Idea B", state="in_review"
        )

        # Assign reviewer
        ReviewAssignment.objects.create(
            idea_id=self.idea_b.id,
            reviewer_id=self.reviewer.id,
            assigned_by="submitter",
        )

        self.merge_request = MergeRequest.objects.create(
            requesting_idea_id=self.idea_a.id,
            target_idea_id=self.idea_b.id,
            merge_type="append",
            requested_by=self.user1.id,
            status="pending",
            requesting_owner_consent="accepted",
            target_owner_consent="pending",
            reviewer_consent="pending",
        )

    def _login_as(self, user: User):
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(user.id)},
            format="json",
        )

    def test_target_owner_accept_stays_pending(self, mock_publish):
        """Target owner accept alone doesn't resolve — still needs reviewer consent."""
        self._login_as(self.user2)
        response = self.client.post(
            f"/api/merge-requests/{self.merge_request.id}/consent",
            {"consent": "accept"},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert data["target_owner_consent"] == "accepted"
        assert data["reviewer_consent"] == "pending"

    def test_reviewer_accept_stays_pending(self, mock_publish):
        """Reviewer accept alone doesn't resolve — still needs target owner consent."""
        self._login_as(self.reviewer)
        response = self.client.post(
            f"/api/merge-requests/{self.merge_request.id}/consent",
            {"consent": "accept"},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert data["target_owner_consent"] == "pending"
        assert data["reviewer_consent"] == "accepted"

    def test_all_three_accept_resolves_accepted(self, mock_publish):
        """All three consents accepted → status='accepted', publishes append.accepted."""
        # Target owner accepts first
        self._login_as(self.user2)
        self.client.post(
            f"/api/merge-requests/{self.merge_request.id}/consent",
            {"consent": "accept"},
            format="json",
        )

        # Reviewer accepts second
        self._login_as(self.reviewer)
        response = self.client.post(
            f"/api/merge-requests/{self.merge_request.id}/consent",
            {"consent": "accept"},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"
        assert data["target_owner_consent"] == "accepted"
        assert data["reviewer_consent"] == "accepted"
        assert data["requesting_owner_consent"] == "accepted"
        assert data["resolved_at"] is not None

        # Verify append.accepted event published
        last_call = mock_publish.call_args
        assert last_call[0][0] == "notification.similarity.append_accepted"

    def test_all_three_accept_reverse_order(self, mock_publish):
        """Reviewer accepts first, then target owner → still resolves accepted."""
        self._login_as(self.reviewer)
        self.client.post(
            f"/api/merge-requests/{self.merge_request.id}/consent",
            {"consent": "accept"},
            format="json",
        )

        self._login_as(self.user2)
        response = self.client.post(
            f"/api/merge-requests/{self.merge_request.id}/consent",
            {"consent": "accept"},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"

    def test_target_owner_decline_resolves_declined(self, mock_publish):
        """Target owner decline → status='declined', publishes append.declined."""
        self._login_as(self.user2)
        response = self.client.post(
            f"/api/merge-requests/{self.merge_request.id}/consent",
            {"consent": "decline"},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "declined"
        assert data["target_owner_consent"] == "declined"

        last_call = mock_publish.call_args
        assert last_call[0][0] == "notification.similarity.append_declined"

    def test_reviewer_decline_resolves_declined(self, mock_publish):
        """Reviewer decline → status='declined', publishes append.declined."""
        self._login_as(self.reviewer)
        response = self.client.post(
            f"/api/merge-requests/{self.merge_request.id}/consent",
            {"consent": "decline"},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "declined"
        assert data["reviewer_consent"] == "declined"

        last_call = mock_publish.call_args
        assert last_call[0][0] == "notification.similarity.append_declined"

    def test_403_random_user_cannot_consent_append(self, mock_publish):
        """Unrelated user cannot consent to an append request."""
        self._login_as(self.user3)
        response = self.client.post(
            f"/api/merge-requests/{self.merge_request.id}/consent",
            {"consent": "accept"},
            format="json",
        )
        assert response.status_code == 403

    def test_403_requesting_owner_cannot_consent(self, mock_publish):
        """Requesting owner cannot consent (they already implicitly consented)."""
        self._login_as(self.user1)
        response = self.client.post(
            f"/api/merge-requests/{self.merge_request.id}/consent",
            {"consent": "accept"},
            format="json",
        )
        assert response.status_code == 403

    def test_reviewer_cannot_consent_merge_type(self, mock_publish):
        """Reviewer cannot consent on merge type (only on append type)."""
        # Use a different idea pair to avoid unique constraint
        idea_c = Idea.objects.create(owner_id=self.user1.id, title="Idea C")
        idea_d = Idea.objects.create(owner_id=self.user2.id, title="Idea D")
        merge_mr = MergeRequest.objects.create(
            requesting_idea_id=idea_c.id,
            target_idea_id=idea_d.id,
            merge_type="merge",
            requested_by=self.user1.id,
            status="pending",
            requesting_owner_consent="accepted",
            target_owner_consent="pending",
            reviewer_consent="not_required",
        )
        # Assign reviewer to idea_d too
        ReviewAssignment.objects.create(
            idea_id=idea_d.id,
            reviewer_id=self.reviewer.id,
            assigned_by="submitter",
        )
        self._login_as(self.reviewer)
        response = self.client.post(
            f"/api/merge-requests/{merge_mr.id}/consent",
            {"consent": "accept"},
            format="json",
        )
        assert response.status_code == 403
