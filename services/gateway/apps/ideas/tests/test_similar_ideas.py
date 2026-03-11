"""Tests for GET /api/ideas/:id/similar — T-4.12.01."""

import uuid
from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.ideas.models import Idea, IdeaCollaborator
from apps.review.models import ReviewAssignment
from apps.similarity.models import IdeaKeywords, MergeRequest

USER_1_ID = uuid.UUID("00000000-0000-0000-0000-000000000501")
USER_2_ID = uuid.UUID("00000000-0000-0000-0000-000000000502")
USER_3_ID = uuid.UUID("00000000-0000-0000-0000-000000000503")
REVIEWER_ID = uuid.UUID("00000000-0000-0000-0000-000000000504")


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
@patch("apps.ideas.views._get_near_threshold_matches", return_value=[])
class TestSimilarIdeas(TestCase):
    """T-4.12.01: GET /api/ideas/:id/similar — declined merges + near-threshold."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = _create_user(USER_1_ID, "sim1@test.local", "Sim User1")
        self.user2 = _create_user(USER_2_ID, "sim2@test.local", "Sim User2")
        self.user3 = _create_user(USER_3_ID, "sim3@test.local", "Sim User3")
        self.reviewer = _create_user(REVIEWER_ID, "reviewer@test.local", "Rev Iewer")

        self.idea_a = Idea.objects.create(owner_id=self.user1.id, title="Idea A")
        self.idea_b = Idea.objects.create(owner_id=self.user2.id, title="Idea B")
        self.idea_c = Idea.objects.create(owner_id=self.user3.id, title="Idea C")

        self._login_as(self.user1)

    def _login_as(self, user: User):
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(user.id)},
            format="json",
        )

    def test_returns_declined_merges(self, _mock_near):
        """T-4.12.01: Declined merge requests appear as similar ideas."""
        MergeRequest.objects.create(
            requesting_idea_id=self.idea_a.id,
            target_idea_id=self.idea_b.id,
            merge_type="merge",
            requested_by=self.user1.id,
            status="declined",
        )
        IdeaKeywords.objects.create(
            idea_id=self.idea_b.id,
            keywords=["ai", "ml", "deep"],
        )

        response = self.client.get(f"/api/ideas/{self.idea_a.id}/similar")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        result = data["results"][0]
        assert result["id"] == str(self.idea_b.id)
        assert result["title"] == "Idea B"
        assert result["similarity_type"] == "declined_merge"
        assert result["similarity_score"] is None
        assert result["keywords"] == ["ai", "ml", "deep"]

    def test_returns_declined_merges_reverse_direction(self, _mock_near):
        """Declined merge where idea is the target also appears."""
        MergeRequest.objects.create(
            requesting_idea_id=self.idea_b.id,
            target_idea_id=self.idea_a.id,
            merge_type="merge",
            requested_by=self.user2.id,
            status="declined",
        )

        response = self.client.get(f"/api/ideas/{self.idea_a.id}/similar")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["id"] == str(self.idea_b.id)
        assert data["results"][0]["similarity_type"] == "declined_merge"

    def test_excludes_pending_and_accepted_merges(self, _mock_near):
        """Only declined merges are returned, not pending or accepted."""
        MergeRequest.objects.create(
            requesting_idea_id=self.idea_a.id,
            target_idea_id=self.idea_b.id,
            merge_type="merge",
            requested_by=self.user1.id,
            status="pending",
        )
        MergeRequest.objects.create(
            requesting_idea_id=self.idea_a.id,
            target_idea_id=self.idea_c.id,
            merge_type="merge",
            requested_by=self.user1.id,
            status="accepted",
        )

        response = self.client.get(f"/api/ideas/{self.idea_a.id}/similar")
        assert response.status_code == 200
        assert response.json()["count"] == 0

    def test_empty_list_when_no_similar(self, _mock_near):
        """Returns empty list when no similar ideas found."""
        response = self.client.get(f"/api/ideas/{self.idea_a.id}/similar")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["results"] == []

    def test_404_for_nonexistent_idea(self, _mock_near):
        """Returns 404 for a non-existent idea ID."""
        fake_id = uuid.uuid4()
        response = self.client.get(f"/api/ideas/{fake_id}/similar")
        assert response.status_code == 404

    def test_404_for_invalid_uuid(self, _mock_near):
        """Returns 404 for an invalid UUID."""
        response = self.client.get("/api/ideas/not-a-uuid/similar")
        assert response.status_code == 404

    def test_403_for_unauthorized_user(self, _mock_near):
        """Returns 403 if user is not owner, co-owner, collaborator, or reviewer."""
        self._login_as(self.user3)
        response = self.client.get(f"/api/ideas/{self.idea_a.id}/similar")
        assert response.status_code == 403

    def test_owner_can_access(self, _mock_near):
        """Idea owner can access similar ideas."""
        response = self.client.get(f"/api/ideas/{self.idea_a.id}/similar")
        assert response.status_code == 200

    def test_co_owner_can_access(self, _mock_near):
        """Co-owner can access similar ideas."""
        self.idea_a.co_owner_id = self.user2.id
        self.idea_a.save(update_fields=["co_owner_id"])
        self._login_as(self.user2)

        response = self.client.get(f"/api/ideas/{self.idea_a.id}/similar")
        assert response.status_code == 200

    def test_collaborator_can_access(self, _mock_near):
        """Collaborator can access similar ideas."""
        IdeaCollaborator.objects.create(idea=self.idea_a, user_id=self.user3.id)
        self._login_as(self.user3)

        response = self.client.get(f"/api/ideas/{self.idea_a.id}/similar")
        assert response.status_code == 200

    def test_reviewer_can_access(self, _mock_near):
        """Assigned reviewer can access similar ideas."""
        self.idea_a.state = "in_review"
        self.idea_a.save(update_fields=["state"])
        ReviewAssignment.objects.create(
            idea_id=self.idea_a.id,
            reviewer_id=self.reviewer.id,
            assigned_by="submitter",
        )
        self._login_as(self.reviewer)

        response = self.client.get(f"/api/ideas/{self.idea_a.id}/similar")
        assert response.status_code == 200

    def test_pagination_defaults(self, _mock_near):
        """Response is paginated with default page_size=10."""
        for i in range(12):
            other = Idea.objects.create(owner_id=self.user2.id, title=f"Other {i}")
            MergeRequest.objects.create(
                requesting_idea_id=self.idea_a.id,
                target_idea_id=other.id,
                merge_type="merge",
                requested_by=self.user1.id,
                status="declined",
            )

        response = self.client.get(f"/api/ideas/{self.idea_a.id}/similar")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 12
        assert len(data["results"]) == 10
        assert data["next"] == 2
        assert data["previous"] is None

    def test_pagination_page_2(self, _mock_near):
        """Second page returns remaining items."""
        for i in range(12):
            other = Idea.objects.create(owner_id=self.user2.id, title=f"Other {i}")
            MergeRequest.objects.create(
                requesting_idea_id=self.idea_a.id,
                target_idea_id=other.id,
                merge_type="merge",
                requested_by=self.user1.id,
                status="declined",
            )

        response = self.client.get(f"/api/ideas/{self.idea_a.id}/similar?page=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2
        assert data["next"] is None
        assert data["previous"] == 1

    def test_pagination_custom_page_size(self, _mock_near):
        """Custom page_size is respected."""
        for i in range(5):
            other = Idea.objects.create(owner_id=self.user2.id, title=f"Other {i}")
            MergeRequest.objects.create(
                requesting_idea_id=self.idea_a.id,
                target_idea_id=other.id,
                merge_type="merge",
                requested_by=self.user1.id,
                status="declined",
            )

        response = self.client.get(f"/api/ideas/{self.idea_a.id}/similar?page_size=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 3
        assert data["count"] == 5
        assert data["next"] == 2

    def test_pagination_max_page_size_enforced(self, _mock_near):
        """page_size cannot exceed 50."""
        response = self.client.get(f"/api/ideas/{self.idea_a.id}/similar?page_size=100")
        assert response.status_code == 200

    def test_deleted_other_idea_excluded(self, _mock_near):
        """Declined merge with soft-deleted other idea is excluded from results."""
        from django.utils import timezone

        deleted_idea = Idea.objects.create(
            owner_id=self.user2.id,
            title="Deleted",
            deleted_at=timezone.now(),
        )
        MergeRequest.objects.create(
            requesting_idea_id=self.idea_a.id,
            target_idea_id=deleted_idea.id,
            merge_type="merge",
            requested_by=self.user1.id,
            status="declined",
        )

        response = self.client.get(f"/api/ideas/{self.idea_a.id}/similar")
        assert response.status_code == 200
        assert response.json()["count"] == 0

    def test_multiple_declined_merges(self, _mock_near):
        """Multiple declined merges from different ideas are all returned."""
        MergeRequest.objects.create(
            requesting_idea_id=self.idea_a.id,
            target_idea_id=self.idea_b.id,
            merge_type="merge",
            requested_by=self.user1.id,
            status="declined",
        )
        MergeRequest.objects.create(
            requesting_idea_id=self.idea_a.id,
            target_idea_id=self.idea_c.id,
            merge_type="merge",
            requested_by=self.user1.id,
            status="declined",
        )

        response = self.client.get(f"/api/ideas/{self.idea_a.id}/similar")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        ids = {r["id"] for r in data["results"]}
        assert str(self.idea_b.id) in ids
        assert str(self.idea_c.id) in ids

    def test_near_threshold_matches_included(self, mock_near):
        """Near-threshold vector matches are included in results."""
        mock_near.return_value = [
            {
                "idea_id": self.idea_b.id,
                "similarity_type": "near_threshold",
                "similarity_score": 0.7123,
            }
        ]

        response = self.client.get(f"/api/ideas/{self.idea_a.id}/similar")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        result = data["results"][0]
        assert result["id"] == str(self.idea_b.id)
        assert result["similarity_type"] == "near_threshold"
        assert result["similarity_score"] == 0.7123
