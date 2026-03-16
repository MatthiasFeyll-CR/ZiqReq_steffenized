"""Tests for POST /api/reviews/:id/assign and /api/reviews/:id/unassign — US-002.

Test IDs: T-10.3.01, T-10.3.02, T-10.4.01, API-REVIEW.03, API-REVIEW.04, API-REVIEW.05
"""

import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.projects.models import Project
from apps.review.models import ReviewAssignment

USER_1_ID = uuid.UUID("00000000-0000-0000-0000-000000000101")
USER_2_ID = uuid.UUID("00000000-0000-0000-0000-000000000102")
REVIEWER_1_ID = uuid.UUID("00000000-0000-0000-0000-000000000201")
REVIEWER_2_ID = uuid.UUID("00000000-0000-0000-0000-000000000202")


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
class TestReviewAssignment(TestCase):
    """Integration tests for POST /api/reviews/:id/assign and /unassign."""

    def setUp(self):
        self.client = APIClient()
        self.owner = _create_user(USER_1_ID, "owner@test.local", "Project Owner")
        self.regular_user = _create_user(USER_2_ID, "regular@test.local", "Regular User")
        self.reviewer1 = _create_user(REVIEWER_1_ID, "reviewer1@test.local", "Reviewer One", ["user", "reviewer"])
        self.reviewer2 = _create_user(REVIEWER_2_ID, "reviewer2@test.local", "Reviewer Two", ["user", "reviewer"])
        self.project = Project.objects.create(owner_id=self.owner.id, state="in_review", title="Test Project")
        self._login_as(self.reviewer1)

    def _login_as(self, user: User):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    def _assign_url(self, project_id=None):
        return f"/api/reviews/{project_id or self.project.id}/assign"

    def _unassign_url(self, project_id=None):
        return f"/api/reviews/{project_id or self.project.id}/unassign"

    # --- T-10.3.01: Self-assignment works ---

    def test_self_assign_success(self):
        """T-10.3.01 | Integration | Self-assignment works.
        Input: POST /api/reviews/:ideaId/assign.
        Expected: 200, assignment created with assigned_by='self'.
        """
        response = self.client.post(self._assign_url(), {}, format="json")
        assert response.status_code == 200, response.json()

        assignment = ReviewAssignment.objects.get(project_id=self.project.id, reviewer_id=self.reviewer1.id)
        assert assignment.assigned_by == "self"
        assert assignment.unassigned_at is None

    # --- T-10.3.02: Unassign works ---

    def test_unassign_success(self):
        """T-10.3.02 | Integration | Unassign works.
        Input: POST /api/reviews/:ideaId/unassign.
        Expected: 200, unassigned_at set.
        """
        # First assign
        ReviewAssignment.objects.create(
            project_id=self.project.id,
            reviewer_id=self.reviewer1.id,
            assigned_by="self",
        )

        response = self.client.post(self._unassign_url(), {}, format="json")
        assert response.status_code == 200, response.json()

        assignment = ReviewAssignment.objects.get(project_id=self.project.id, reviewer_id=self.reviewer1.id)
        assert assignment.unassigned_at is not None

    # --- T-10.4.01: Conflict of interest blocked ---

    def test_conflict_of_interest_owner(self):
        """T-10.4.01 | Integration | Conflict of interest blocked.
        Input: POST /api/reviews/:ideaId/assign on own project.
        Expected: 400 CONFLICT_OF_INTEREST.
        """
        # Create project owned by reviewer1
        own_idea = Project.objects.create(owner_id=self.reviewer1.id, state="in_review", title="Own Project")

        response = self.client.post(self._assign_url(own_idea.id), {}, format="json")
        assert response.status_code == 400
        assert response.json()["error"] == "CONFLICT_OF_INTEREST"


    # --- API-REVIEW.03: Conflict of interest (same as T-10.4.01) ---

    def test_api_review_03_conflict_of_interest(self):
        """API-REVIEW.03 | POST /api/reviews/:id/assign | Conflict of interest.
        Input: Reviewer = owner.
        Expected: 400 CONFLICT_OF_INTEREST.
        """
        own_idea = Project.objects.create(owner_id=self.reviewer1.id, state="in_review", title="My Project")
        response = self.client.post(self._assign_url(own_idea.id), {}, format="json")
        assert response.status_code == 400
        assert response.json()["error"] == "CONFLICT_OF_INTEREST"

    # --- API-REVIEW.04: Duplicate assignment blocked ---

    def test_duplicate_assignment_blocked(self):
        """API-REVIEW.04 | POST /api/reviews/:id/assign | Duplicate.
        Input: Already assigned.
        Expected: 400 ALREADY_ASSIGNED.
        """
        # First assignment
        self.client.post(self._assign_url(), {}, format="json")

        # Try again
        response = self.client.post(self._assign_url(), {}, format="json")
        assert response.status_code == 400
        assert response.json()["error"] == "ALREADY_ASSIGNED"

    # --- API-REVIEW.05: Role check ---

    def test_user_role_cannot_assign(self):
        """API-REVIEW.05 | POST /api/reviews/:id/assign | Role check.
        Input: User role (not Reviewer).
        Expected: 403.
        """
        self._login_as(self.regular_user)
        response = self.client.post(self._assign_url(), {}, format="json")
        assert response.status_code == 403

    def test_user_role_cannot_unassign(self):
        """Non-reviewer cannot unassign."""
        self._login_as(self.regular_user)
        response = self.client.post(self._unassign_url(), {}, format="json")
        assert response.status_code == 403

    # --- Invalid state ---

    def test_assign_invalid_state_open(self):
        """Only in_review projects can be assigned — 400 INVALID_STATE for open."""
        open_idea = Project.objects.create(owner_id=self.owner.id, state="open", title="Open Project")
        response = self.client.post(self._assign_url(open_idea.id), {}, format="json")
        assert response.status_code == 400
        assert response.json()["error"] == "INVALID_STATE"

    def test_assign_invalid_state_accepted(self):
        """Only in_review projects can be assigned — 400 INVALID_STATE for accepted."""
        accepted_idea = Project.objects.create(owner_id=self.owner.id, state="accepted", title="Accepted Project")
        response = self.client.post(self._assign_url(accepted_idea.id), {}, format="json")
        assert response.status_code == 400
        assert response.json()["error"] == "INVALID_STATE"

    # --- Unassign not found ---

    def test_unassign_not_found(self):
        """Unassign when not assigned returns 404."""
        response = self.client.post(self._unassign_url(), {}, format="json")
        assert response.status_code == 404

    # --- Re-assign after unassign ---

    def test_reassign_after_unassign(self):
        """Can re-assign after unassigning (old assignment has unassigned_at set)."""
        # Assign
        self.client.post(self._assign_url(), {}, format="json")
        # Unassign
        self.client.post(self._unassign_url(), {}, format="json")
        # Re-assign
        response = self.client.post(self._assign_url(), {}, format="json")
        assert response.status_code == 200

        # Should have 2 assignment records: 1 unassigned, 1 active
        assignments = ReviewAssignment.objects.filter(project_id=self.project.id, reviewer_id=self.reviewer1.id)
        assert assignments.count() == 2
        assert assignments.filter(unassigned_at__isnull=True).count() == 1
        assert assignments.filter(unassigned_at__isnull=False).count() == 1

    # --- Project not found ---

    def test_assign_idea_not_found(self):
        """Assign on non-existent project returns 404."""
        fake_id = uuid.uuid4()
        response = self.client.post(self._assign_url(fake_id), {}, format="json")
        assert response.status_code == 404
