"""Tests for review actions API — Accept, Reject, Drop, Undo — US-003.

Test IDs: T-1.5.02, T-1.5.03, T-1.5.04, T-1.5.06, T-1.5.07, T-1.5.08, T-1.5.09,
          API-REVIEW.06, API-REVIEW.07, API-REVIEW.08, API-REVIEW.09
"""

import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.ideas.models import Idea
from apps.review.models import ReviewTimelineEntry

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
class TestReviewActions(TestCase):
    """Integration tests for review action endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.owner = _create_user(USER_1_ID, "owner@test.local", "Idea Owner")
        self.reviewer1 = _create_user(REVIEWER_1_ID, "reviewer1@test.local", "Reviewer One", ["user", "reviewer"])
        self.reviewer2 = _create_user(REVIEWER_2_ID, "reviewer2@test.local", "Reviewer Two", ["user", "reviewer"])
        self.regular_user = _create_user(REGULAR_USER_ID, "regular@test.local", "Regular User")
        self.idea = Idea.objects.create(owner_id=self.owner.id, state="in_review", title="Test Idea")
        self._login_as(self.reviewer1)

    def _login_as(self, user: User):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    def _url(self, action: str, idea_id=None):
        return f"/api/ideas/{idea_id or self.idea.id}/review/{action}"

    # --- T-1.5.02: In Review → Accepted via reviewer accept ---

    def test_accept_success(self):
        """T-1.5.02 | Integration | In Review → Accepted via reviewer accept.
        Input: POST /api/ideas/:id/review/accept.
        Expected: State = accepted, timeline entry created.
        """
        response = self.client.post(self._url("accept"), {}, format="json")
        assert response.status_code == 200, response.json()
        assert response.json()["state"] == "accepted"

        self.idea.refresh_from_db()
        assert self.idea.state == "accepted"

        entry = ReviewTimelineEntry.objects.get(idea_id=self.idea.id, entry_type="state_change", new_state="accepted")
        assert entry.old_state == "in_review"
        assert entry.author_id == self.reviewer1.id

    # --- T-1.5.03: In Review → Dropped via reviewer drop ---

    def test_drop_success(self):
        """T-1.5.03 | Integration | In Review → Dropped via reviewer drop.
        Input: POST /api/ideas/:id/review/drop with comment.
        Expected: State = dropped, timeline entry with comment.
        """
        response = self.client.post(self._url("drop"), {"comment": "Not viable"}, format="json")
        assert response.status_code == 200, response.json()
        assert response.json()["state"] == "dropped"

        self.idea.refresh_from_db()
        assert self.idea.state == "dropped"

        entry = ReviewTimelineEntry.objects.get(idea_id=self.idea.id, entry_type="state_change", new_state="dropped")
        assert entry.content == "Not viable"

    # --- T-1.5.04: In Review → Rejected via reviewer reject ---

    def test_reject_success(self):
        """T-1.5.04 | Integration | In Review → Rejected via reviewer reject.
        Input: POST /api/ideas/:id/review/reject with comment.
        Expected: State = rejected, timeline entry with comment.
        """
        response = self.client.post(self._url("reject"), {"comment": "Needs rework"}, format="json")
        assert response.status_code == 200, response.json()
        assert response.json()["state"] == "rejected"

        self.idea.refresh_from_db()
        assert self.idea.state == "rejected"

        entry = ReviewTimelineEntry.objects.get(idea_id=self.idea.id, entry_type="state_change", new_state="rejected")
        assert entry.content == "Needs rework"

    # --- T-1.5.06: Accepted → In Review via undo ---

    def test_undo_accepted(self):
        """T-1.5.06 | Integration | Accepted → In Review via undo.
        Input: POST /api/ideas/:id/review/undo with comment.
        Expected: State = in_review.
        """
        self.idea.state = "accepted"
        self.idea.save(update_fields=["state"])

        response = self.client.post(self._url("undo"), {"comment": "Reconsidering"}, format="json")
        assert response.status_code == 200, response.json()
        assert response.json()["state"] == "in_review"

        self.idea.refresh_from_db()
        assert self.idea.state == "in_review"

        entry = ReviewTimelineEntry.objects.filter(
            idea_id=self.idea.id, entry_type="state_change", new_state="in_review"
        ).last()
        assert entry is not None
        assert entry.old_state == "accepted"
        assert entry.content == "Reconsidering"

    # --- T-1.5.07: Dropped → In Review via undo ---

    def test_undo_dropped(self):
        """T-1.5.07 | Integration | Dropped → In Review via undo.
        Input: POST /api/ideas/:id/review/undo with comment.
        Expected: State = in_review.
        """
        self.idea.state = "dropped"
        self.idea.save(update_fields=["state"])

        response = self.client.post(self._url("undo"), {"comment": "Reopening"}, format="json")
        assert response.status_code == 200, response.json()
        assert response.json()["state"] == "in_review"

        self.idea.refresh_from_db()
        assert self.idea.state == "in_review"

    # --- Undo rejected (not in original test IDs but AC says it works) ---

    def test_undo_rejected(self):
        """Undo works for rejected state too."""
        self.idea.state = "rejected"
        self.idea.save(update_fields=["state"])

        response = self.client.post(self._url("undo"), {"comment": "Give another chance"}, format="json")
        assert response.status_code == 200, response.json()
        assert response.json()["state"] == "in_review"

        self.idea.refresh_from_db()
        assert self.idea.state == "in_review"

    # --- T-1.5.08: Invalid transition ---

    def test_accept_invalid_state_open(self):
        """T-1.5.08 | Integration | Invalid transition.
        Input: POST /api/ideas/:id/review/accept on open idea.
        Expected: 400 INVALID_STATE.
        """
        open_idea = Idea.objects.create(owner_id=self.owner.id, state="open", title="Open Idea")
        response = self.client.post(self._url("accept", open_idea.id), {}, format="json")
        assert response.status_code == 400
        assert response.json()["error"] == "INVALID_STATE"

    def test_undo_invalid_state_in_review(self):
        """Undo on in_review idea is invalid."""
        response = self.client.post(self._url("undo"), {"comment": "Nope"}, format="json")
        assert response.status_code == 400
        assert response.json()["error"] == "INVALID_STATE"

    def test_undo_invalid_state_open(self):
        """Undo on open idea is invalid."""
        open_idea = Idea.objects.create(owner_id=self.owner.id, state="open", title="Open Idea 2")
        response = self.client.post(self._url("undo", open_idea.id), {"comment": "Nope"}, format="json")
        assert response.status_code == 400
        assert response.json()["error"] == "INVALID_STATE"

    # --- T-1.5.09: Multiple reviewers, latest action wins ---

    def test_multiple_reviewers_latest_wins(self):
        """T-1.5.09 | Integration | Multiple reviewers: latest action wins.
        Two reviewers act in sequence, last action determines state.
        """
        # Reviewer 1 accepts
        response = self.client.post(self._url("accept"), {}, format="json")
        assert response.status_code == 200
        self.idea.refresh_from_db()
        assert self.idea.state == "accepted"

        # Reviewer 2 undoes
        self._login_as(self.reviewer2)
        response = self.client.post(self._url("undo"), {"comment": "Not yet"}, format="json")
        assert response.status_code == 200
        self.idea.refresh_from_db()
        assert self.idea.state == "in_review"

        # Reviewer 2 rejects
        response = self.client.post(self._url("reject"), {"comment": "Needs work"}, format="json")
        assert response.status_code == 200
        self.idea.refresh_from_db()
        assert self.idea.state == "rejected"

    # --- API-REVIEW.06: Accept success ---

    def test_api_review_06_accept_success(self):
        """API-REVIEW.06 | POST /api/ideas/:id/review/accept | Success.
        Input: Valid in_review idea.
        Expected: 200 with state=accepted.
        """
        response = self.client.post(self._url("accept"), {}, format="json")
        assert response.status_code == 200
        assert response.json()["state"] == "accepted"

    # --- API-REVIEW.07: Reject missing comment ---

    def test_api_review_07_reject_missing_comment(self):
        """API-REVIEW.07 | POST /api/ideas/:id/review/reject | Missing comment.
        Input: No comment field.
        Expected: 400 COMMENT_REQUIRED.
        """
        response = self.client.post(self._url("reject"), {}, format="json")
        assert response.status_code == 400
        assert response.json()["error"] == "COMMENT_REQUIRED"

    def test_reject_blank_comment(self):
        """Reject with blank comment returns 400 COMMENT_REQUIRED."""
        response = self.client.post(self._url("reject"), {"comment": ""}, format="json")
        assert response.status_code == 400
        assert response.json()["error"] == "COMMENT_REQUIRED"

    def test_drop_missing_comment(self):
        """Drop without comment returns 400 COMMENT_REQUIRED."""
        response = self.client.post(self._url("drop"), {}, format="json")
        assert response.status_code == 400
        assert response.json()["error"] == "COMMENT_REQUIRED"

    def test_undo_missing_comment(self):
        """Undo without comment returns 400 COMMENT_REQUIRED."""
        self.idea.state = "accepted"
        self.idea.save(update_fields=["state"])

        response = self.client.post(self._url("undo"), {}, format="json")
        assert response.status_code == 400
        assert response.json()["error"] == "COMMENT_REQUIRED"

    # --- API-REVIEW.08: Drop invalid state ---

    def test_api_review_08_drop_invalid_state(self):
        """API-REVIEW.08 | POST /api/ideas/:id/review/drop | Invalid state.
        Input: Idea state = open.
        Expected: 400 INVALID_STATE.
        """
        open_idea = Idea.objects.create(owner_id=self.owner.id, state="open", title="Open Idea 3")
        response = self.client.post(self._url("drop", open_idea.id), {"comment": "Drop it"}, format="json")
        assert response.status_code == 400
        assert response.json()["error"] == "INVALID_STATE"

    # --- API-REVIEW.09: Undo access control ---

    def test_api_review_09_undo_access_control(self):
        """API-REVIEW.09 | POST /api/ideas/:id/review/undo | Access control.
        Input: User role (not Reviewer).
        Expected: 403.
        """
        self.idea.state = "accepted"
        self.idea.save(update_fields=["state"])

        self._login_as(self.regular_user)
        response = self.client.post(self._url("undo"), {"comment": "Undo it"}, format="json")
        assert response.status_code == 403

    def test_accept_non_reviewer_forbidden(self):
        """Non-reviewer cannot accept."""
        self._login_as(self.regular_user)
        response = self.client.post(self._url("accept"), {}, format="json")
        assert response.status_code == 403

    # --- Timeline entry records old_state and new_state ---

    def test_timeline_records_states(self):
        """Timeline entries record old_state and new_state for state_change type."""
        self.client.post(self._url("accept"), {}, format="json")

        entry = ReviewTimelineEntry.objects.get(idea_id=self.idea.id, entry_type="state_change")
        assert entry.old_state == "in_review"
        assert entry.new_state == "accepted"
