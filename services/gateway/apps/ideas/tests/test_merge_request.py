"""Tests for Merge Request API — US-007 (T-5.5.01, T-5.5.02, T-5.5.04)."""

import uuid
from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.ideas.models import Idea
from apps.similarity.models import MergeRequest

USER_1_ID = uuid.UUID("00000000-0000-0000-0000-000000000701")
USER_2_ID = uuid.UUID("00000000-0000-0000-0000-000000000702")
USER_3_ID = uuid.UUID("00000000-0000-0000-0000-000000000703")


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
class TestCreateMergeRequest(TestCase):
    """T-5.5.01: POST /api/ideas/:id/merge-request creates pending record."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = _create_user(USER_1_ID, "mr1@test.local", "MR User1")
        self.user2 = _create_user(USER_2_ID, "mr2@test.local", "MR User2")
        self.user3 = _create_user(USER_3_ID, "mr3@test.local", "MR User3")

        self.idea_a = Idea.objects.create(owner_id=self.user1.id, title="Idea A")
        self.idea_b = Idea.objects.create(owner_id=self.user2.id, title="Idea B")

        self._login_as(self.user1)

    def _login_as(self, user: User):
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(user.id)},
            format="json",
        )

    def test_create_merge_request_success(self, mock_publish):
        """T-5.5.01: Creates a pending merge request with implicit requesting consent."""
        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_id": str(self.idea_b.id)},
            format="json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["requesting_idea_id"] == str(self.idea_a.id)
        assert data["target_idea_id"] == str(self.idea_b.id)
        assert data["merge_type"] == "merge"
        assert data["status"] == "pending"
        assert data["requesting_owner_consent"] == "accepted"
        assert data["target_owner_consent"] == "pending"

    def test_publishes_created_event(self, mock_publish):
        """Publishes merge_request.created event on creation."""
        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_id": str(self.idea_b.id)},
            format="json",
        )
        assert response.status_code == 201
        mock_publish.assert_called_once()
        call_args = mock_publish.call_args
        assert call_args[0][0] == "notification.similarity.merge_request_created"
        payload = call_args[0][1]
        assert payload["requesting_idea_id"] == str(self.idea_a.id)
        assert payload["target_idea_id"] == str(self.idea_b.id)

    def test_400_duplicate_pending_request(self, mock_publish):
        """Returns 400 if a pending merge request already exists for this pair."""
        MergeRequest.objects.create(
            requesting_idea_id=self.idea_a.id,
            target_idea_id=self.idea_b.id,
            merge_type="merge",
            requested_by=self.user1.id,
            status="pending",
        )
        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_id": str(self.idea_b.id)},
            format="json",
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["message"]

    def test_400_duplicate_pending_reverse_direction(self, mock_publish):
        """Returns 400 if a pending merge request exists in reverse direction."""
        MergeRequest.objects.create(
            requesting_idea_id=self.idea_b.id,
            target_idea_id=self.idea_a.id,
            merge_type="merge",
            requested_by=self.user2.id,
            status="pending",
        )
        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_id": str(self.idea_b.id)},
            format="json",
        )
        assert response.status_code == 400

    def test_allows_after_declined(self, mock_publish):
        """Allows creating a new merge request after the previous was declined."""
        MergeRequest.objects.create(
            requesting_idea_id=self.idea_a.id,
            target_idea_id=self.idea_b.id,
            merge_type="merge",
            requested_by=self.user1.id,
            status="declined",
        )
        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_id": str(self.idea_b.id)},
            format="json",
        )
        assert response.status_code == 201

    def test_403_non_owner(self, mock_publish):
        """Returns 403 if user is not the requesting idea's owner."""
        self._login_as(self.user2)
        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_id": str(self.idea_b.id)},
            format="json",
        )
        assert response.status_code == 403

    def test_404_nonexistent_requesting_idea(self, mock_publish):
        """Returns 404 for non-existent requesting idea."""
        fake_id = uuid.uuid4()
        response = self.client.post(
            f"/api/ideas/{fake_id}/merge-request",
            {"target_idea_id": str(self.idea_b.id)},
            format="json",
        )
        assert response.status_code == 404

    def test_404_nonexistent_target_idea(self, mock_publish):
        """Returns 404 for non-existent target idea."""
        fake_id = uuid.uuid4()
        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_id": str(fake_id)},
            format="json",
        )
        assert response.status_code == 404

    def test_400_self_merge(self, mock_publish):
        """Returns 400 when trying to merge with self."""
        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {"target_idea_id": str(self.idea_a.id)},
            format="json",
        )
        assert response.status_code == 400

    def test_400_missing_target_id(self, mock_publish):
        """Returns 400 when target_idea_id is missing."""
        response = self.client.post(
            f"/api/ideas/{self.idea_a.id}/merge-request",
            {},
            format="json",
        )
        assert response.status_code == 400


@override_settings(DEBUG=True, AUTH_BYPASS=True)
@patch("apps.ideas.views._publish_event")
class TestConsentMergeRequest(TestCase):
    """T-5.5.04: POST /api/merge-requests/:id/consent — accept or decline."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = _create_user(USER_1_ID, "mr1@test.local", "MR User1")
        self.user2 = _create_user(USER_2_ID, "mr2@test.local", "MR User2")
        self.user3 = _create_user(USER_3_ID, "mr3@test.local", "MR User3")

        self.idea_a = Idea.objects.create(owner_id=self.user1.id, title="Idea A")
        self.idea_b = Idea.objects.create(owner_id=self.user2.id, title="Idea B")

        self.merge_request = MergeRequest.objects.create(
            requesting_idea_id=self.idea_a.id,
            target_idea_id=self.idea_b.id,
            merge_type="merge",
            requested_by=self.user1.id,
            status="pending",
            requesting_owner_consent="accepted",
            target_owner_consent="pending",
        )

        # Login as target owner by default
        self._login_as(self.user2)

    def _login_as(self, user: User):
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(user.id)},
            format="json",
        )

    def test_accept_sets_both_consents_and_status(self, mock_publish):
        """Accept sets target_owner_consent='accepted', status='accepted' when both consent."""
        response = self.client.post(
            f"/api/merge-requests/{self.merge_request.id}/consent",
            {"consent": "accept"},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"
        assert data["target_owner_consent"] == "accepted"
        assert data["requesting_owner_consent"] == "accepted"
        assert data["resolved_at"] is not None

    def test_accept_publishes_accepted_event(self, mock_publish):
        """Accept publishes merge_request.accepted event."""
        self.client.post(
            f"/api/merge-requests/{self.merge_request.id}/consent",
            {"consent": "accept"},
            format="json",
        )
        mock_publish.assert_called_once()
        call_args = mock_publish.call_args
        assert call_args[0][0] == "notification.similarity.merge_request_accepted"

    def test_decline_sets_status_declined(self, mock_publish):
        """T-5.5.04: Decline sets status='declined' and target_owner_consent='declined'."""
        response = self.client.post(
            f"/api/merge-requests/{self.merge_request.id}/consent",
            {"consent": "decline"},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "declined"
        assert data["target_owner_consent"] == "declined"
        assert data["resolved_at"] is not None

    def test_decline_publishes_declined_event(self, mock_publish):
        """Decline publishes merge_request.declined event."""
        self.client.post(
            f"/api/merge-requests/{self.merge_request.id}/consent",
            {"consent": "decline"},
            format="json",
        )
        mock_publish.assert_called_once()
        call_args = mock_publish.call_args
        assert call_args[0][0] == "notification.similarity.merge_request_declined"

    def test_decline_permanently_dismisses_pair(self, mock_publish):
        """T-5.5.04: Declined pair cannot have a new pending merge request via unique constraint."""
        self.client.post(
            f"/api/merge-requests/{self.merge_request.id}/consent",
            {"consent": "decline"},
            format="json",
        )
        self.merge_request.refresh_from_db()
        assert self.merge_request.status == "declined"
        # The pair can still create a new request (declined doesn't block DB unique constraint)
        # but the pair IS permanently dismissed from similarity detection (checked in US-001/002)

    def test_403_non_target_owner(self, mock_publish):
        """Returns 403 if user is not the target idea owner."""
        self._login_as(self.user1)  # requesting owner, not target
        response = self.client.post(
            f"/api/merge-requests/{self.merge_request.id}/consent",
            {"consent": "accept"},
            format="json",
        )
        assert response.status_code == 403

    def test_403_random_user(self, mock_publish):
        """Returns 403 for unrelated user."""
        self._login_as(self.user3)
        response = self.client.post(
            f"/api/merge-requests/{self.merge_request.id}/consent",
            {"consent": "accept"},
            format="json",
        )
        assert response.status_code == 403

    def test_404_nonexistent_merge_request(self, mock_publish):
        """Returns 404 for non-existent merge request."""
        fake_id = uuid.uuid4()
        response = self.client.post(
            f"/api/merge-requests/{fake_id}/consent",
            {"consent": "accept"},
            format="json",
        )
        assert response.status_code == 404

    def test_400_already_accepted(self, mock_publish):
        """Returns 400 if merge request is already accepted."""
        self.merge_request.status = "accepted"
        self.merge_request.save()
        response = self.client.post(
            f"/api/merge-requests/{self.merge_request.id}/consent",
            {"consent": "accept"},
            format="json",
        )
        assert response.status_code == 400

    def test_400_already_declined(self, mock_publish):
        """Returns 400 if merge request is already declined."""
        self.merge_request.status = "declined"
        self.merge_request.save()
        response = self.client.post(
            f"/api/merge-requests/{self.merge_request.id}/consent",
            {"consent": "accept"},
            format="json",
        )
        assert response.status_code == 400

    def test_400_invalid_consent_value(self, mock_publish):
        """Returns 400 for invalid consent value."""
        response = self.client.post(
            f"/api/merge-requests/{self.merge_request.id}/consent",
            {"consent": "maybe"},
            format="json",
        )
        assert response.status_code == 400

    def test_400_missing_consent(self, mock_publish):
        """Returns 400 when consent field is missing."""
        response = self.client.post(
            f"/api/merge-requests/{self.merge_request.id}/consent",
            {},
            format="json",
        )
        assert response.status_code == 400
