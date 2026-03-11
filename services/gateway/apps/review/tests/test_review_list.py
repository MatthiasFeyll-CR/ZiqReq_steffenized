"""Tests for GET /api/reviews — US-005: Review Page List API.

Test IDs: T-10.1.01, T-10.2.01, API-REVIEW.01, API-REVIEW.02
"""

import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.ideas.models import Idea
from apps.review.models import ReviewAssignment

USER_1_ID = uuid.UUID("00000000-0000-0000-0000-000000000301")
REVIEWER_1_ID = uuid.UUID("00000000-0000-0000-0000-000000000311")
REVIEWER_2_ID = uuid.UUID("00000000-0000-0000-0000-000000000312")
REGULAR_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000302")


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
class TestReviewList(TestCase):
    """Integration tests for GET /api/reviews."""

    def setUp(self):
        self.client = APIClient()
        self.owner = _create_user(USER_1_ID, "owner@test.local", "Idea Owner")
        self.reviewer1 = _create_user(REVIEWER_1_ID, "reviewer1@test.local", "Reviewer One", ["user", "reviewer"])
        self.reviewer2 = _create_user(REVIEWER_2_ID, "reviewer2@test.local", "Reviewer Two", ["user", "reviewer"])
        self.regular_user = _create_user(REGULAR_USER_ID, "regular@test.local", "Regular User")
        self._login_as(self.reviewer1)

    def _login_as(self, user: User):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    def _url(self):
        return "/api/reviews/"

    # --- T-10.1.01: Review page requires reviewer role ---

    def test_regular_user_forbidden(self):
        """T-10.1.01 | Integration | Review page requires reviewer role.
        Input: GET /api/reviews as regular user.
        Expected: 403.
        """
        self._login_as(self.regular_user)
        resp = self.client.get(self._url())
        self.assertEqual(resp.status_code, 403)

    # --- API-REVIEW.02: Role check ---

    def test_role_check_non_reviewer(self):
        """API-REVIEW.02 | GET /api/reviews | Role check | User role (not Reviewer) | 403."""
        self._login_as(self.regular_user)
        resp = self.client.get(self._url())
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.json()["error"], "FORBIDDEN")

    # --- API-REVIEW.01: Success with categorized lists ---

    def test_success_returns_five_categories(self):
        """API-REVIEW.01 | GET /api/reviews | Success | Reviewer role | 200 with categorized lists."""
        resp = self.client.get(self._url())
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("assigned_to_me", data)
        self.assertIn("unassigned", data)
        self.assertIn("accepted", data)
        self.assertIn("rejected", data)
        self.assertIn("dropped", data)

    # --- T-10.2.01: Ideas grouped correctly ---

    def test_ideas_grouped_correctly(self):
        """T-10.2.01 | Integration | Ideas grouped correctly.
        Input: GET /api/reviews with various idea states.
        Expected: 5 groups: assigned, unassigned, accepted, rejected, dropped.
        """
        # Create ideas in different states
        idea_assigned = Idea.objects.create(owner_id=self.owner.id, state="in_review", title="Assigned Idea")
        idea_unassigned = Idea.objects.create(owner_id=self.owner.id, state="in_review", title="Unassigned Idea")
        idea_accepted = Idea.objects.create(owner_id=self.owner.id, state="accepted", title="Accepted Idea")
        idea_rejected = Idea.objects.create(owner_id=self.owner.id, state="rejected", title="Rejected Idea")
        idea_dropped = Idea.objects.create(owner_id=self.owner.id, state="dropped", title="Dropped Idea")

        # Assign reviewer1 to one idea
        ReviewAssignment.objects.create(
            idea_id=idea_assigned.id,
            reviewer_id=self.reviewer1.id,
            assigned_by="self",
        )

        resp = self.client.get(self._url())
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        # Assigned to me should contain the assigned idea
        assigned_ids = [i["id"] for i in data["assigned_to_me"]]
        self.assertIn(str(idea_assigned.id), assigned_ids)

        # Unassigned should contain the unassigned in_review idea
        unassigned_ids = [i["id"] for i in data["unassigned"]]
        self.assertIn(str(idea_unassigned.id), unassigned_ids)

        # Final states
        accepted_ids = [i["id"] for i in data["accepted"]]
        self.assertIn(str(idea_accepted.id), accepted_ids)

        rejected_ids = [i["id"] for i in data["rejected"]]
        self.assertIn(str(idea_rejected.id), rejected_ids)

        dropped_ids = [i["id"] for i in data["dropped"]]
        self.assertIn(str(idea_dropped.id), dropped_ids)

    def test_assigned_to_other_reviewer_not_in_assigned_to_me(self):
        """An idea assigned to reviewer2 should NOT appear in reviewer1's assigned_to_me."""
        idea = Idea.objects.create(owner_id=self.owner.id, state="in_review", title="Other Assigned")
        ReviewAssignment.objects.create(
            idea_id=idea.id,
            reviewer_id=self.reviewer2.id,
            assigned_by="self",
        )

        resp = self.client.get(self._url())
        data = resp.json()

        assigned_ids = [i["id"] for i in data["assigned_to_me"]]
        self.assertNotIn(str(idea.id), assigned_ids)

        # It should still appear in unassigned (no active assignment for current reviewer,
        # but actually it has an assignment — it just doesn't have one for current user).
        # Per spec: unassigned means no active assignments at all.
        # Since reviewer2 is assigned, it should NOT appear in unassigned either.
        unassigned_ids = [i["id"] for i in data["unassigned"]]
        self.assertNotIn(str(idea.id), unassigned_ids)

    def test_unassigned_at_not_null_treated_as_unassigned(self):
        """An idea where all assignments have unassigned_at set should appear as unassigned."""
        idea = Idea.objects.create(owner_id=self.owner.id, state="in_review", title="Was Assigned")
        from django.utils import timezone

        ReviewAssignment.objects.create(
            idea_id=idea.id,
            reviewer_id=self.reviewer1.id,
            assigned_by="self",
            unassigned_at=timezone.now(),
        )

        resp = self.client.get(self._url())
        data = resp.json()

        unassigned_ids = [i["id"] for i in data["unassigned"]]
        self.assertIn(str(idea.id), unassigned_ids)

    def test_response_includes_idea_metadata(self):
        """Response includes idea title, state, owner_name, submitted_at, reviewers."""
        idea = Idea.objects.create(owner_id=self.owner.id, state="in_review", title="Metadata Test")
        ReviewAssignment.objects.create(
            idea_id=idea.id,
            reviewer_id=self.reviewer1.id,
            assigned_by="self",
        )

        resp = self.client.get(self._url())
        data = resp.json()

        assigned = data["assigned_to_me"]
        self.assertTrue(len(assigned) >= 1)
        item = next(i for i in assigned if i["id"] == str(idea.id))
        self.assertEqual(item["title"], "Metadata Test")
        self.assertEqual(item["state"], "in_review")
        self.assertEqual(item["owner_name"], "Idea Owner")
        self.assertIn("submitted_at", item)
        self.assertIn("reviewers", item)
        self.assertIsInstance(item["reviewers"], list)

    def test_open_ideas_excluded(self):
        """Open ideas should not appear in any category."""
        Idea.objects.create(owner_id=self.owner.id, state="open", title="Open Idea")

        resp = self.client.get(self._url())
        data = resp.json()

        all_ids = []
        for category in ["assigned_to_me", "unassigned", "accepted", "rejected", "dropped"]:
            all_ids.extend(i["id"] for i in data[category])

        # Open idea should not appear
        open_ideas = Idea.objects.filter(state="open")
        for idea in open_ideas:
            self.assertNotIn(str(idea.id), all_ids)

    def test_unauthenticated_returns_401(self):
        """Unauthenticated request returns 401."""
        client = APIClient()
        resp = client.get(self._url())
        self.assertEqual(resp.status_code, 401)

    def test_reviewers_list_in_response(self):
        """Reviewers list includes active reviewer names."""
        idea = Idea.objects.create(owner_id=self.owner.id, state="in_review", title="With Reviewers")
        ReviewAssignment.objects.create(
            idea_id=idea.id,
            reviewer_id=self.reviewer1.id,
            assigned_by="self",
        )
        ReviewAssignment.objects.create(
            idea_id=idea.id,
            reviewer_id=self.reviewer2.id,
            assigned_by="submitter",
        )

        resp = self.client.get(self._url())
        data = resp.json()

        item = next(i for i in data["assigned_to_me"] if i["id"] == str(idea.id))
        reviewer_names = [r["display_name"] for r in item["reviewers"]]
        self.assertIn("Reviewer One", reviewer_names)
        self.assertIn("Reviewer Two", reviewer_names)

    def test_empty_review_list(self):
        """No ideas returns empty lists for all categories."""
        resp = self.client.get(self._url())
        data = resp.json()
        for category in ["assigned_to_me", "unassigned", "accepted", "rejected", "dropped"]:
            self.assertEqual(data[category], [])
