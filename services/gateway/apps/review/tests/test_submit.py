"""Tests for POST /api/ideas/:id/submit — US-001: Submit Idea for Review.

Test IDs: T-1.5.01, T-1.5.05, T-4.7.01, T-4.10.01, T-4.10.02,
          API-SUBMIT.01, API-SUBMIT.02, API-SUBMIT.03, API-SUBMIT.04
"""

import unittest.mock
import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.brd.models import BrdDraft
from apps.ideas.models import Idea
from apps.review.models import BrdVersion, ReviewAssignment, ReviewTimelineEntry

USER_1_ID = uuid.UUID("00000000-0000-0000-0000-000000000101")
USER_2_ID = uuid.UUID("00000000-0000-0000-0000-000000000102")
USER_3_ID = uuid.UUID("00000000-0000-0000-0000-000000000103")
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
class TestSubmitIdea(TestCase):
    """Integration tests for POST /api/ideas/:id/submit."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = _create_user(USER_1_ID, "owner@test.local", "Idea Owner")
        self.user2 = _create_user(USER_2_ID, "other@test.local", "Other User")
        self.reviewer1 = _create_user(REVIEWER_1_ID, "reviewer1@test.local", "Reviewer One", ["user", "reviewer"])
        self.reviewer2 = _create_user(REVIEWER_2_ID, "reviewer2@test.local", "Reviewer Two", ["user", "reviewer"])
        self.idea = Idea.objects.create(owner_id=self.user1.id, state="open", title="Test Idea")
        BrdDraft.objects.create(
            idea_id=self.idea.id,
            section_title="My Title",
            section_short_description="My Description",
            section_current_workflow="Current workflow",
            section_affected_department="IT",
            section_core_capabilities="Capabilities",
            section_success_criteria="Success criteria",
        )
        self._login_as(self.user1)

    def _login_as(self, user: User):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    def _url(self, idea_id=None):
        return f"/api/ideas/{idea_id or self.idea.id}/submit"

    # --- T-1.5.01: Open -> In Review via submit ---

    @unittest.mock.patch("apps.review.views._create_pdf_client")
    def test_submit_open_to_in_review(self, mock_pdf_client_factory):
        """T-1.5.01 | Integration | Open -> In Review via submit.
        Input: POST /api/ideas/:id/submit on open idea.
        Expected: State = in_review, BRD version created, timeline entry.
        """
        mock_client = unittest.mock.MagicMock()
        mock_client.generate_pdf.return_value = {"pdf_data": b"%PDF", "filename": "test.pdf"}
        mock_pdf_client_factory.return_value = mock_client

        response = self.client.post(self._url(), {}, format="json")
        assert response.status_code == 200, response.json()
        data = response.json()
        assert data["state"] == "in_review"
        assert data["version_number"] == 1

        self.idea.refresh_from_db()
        assert self.idea.state == "in_review"

        assert BrdVersion.objects.filter(idea_id=self.idea.id, version_number=1).exists()
        assert ReviewTimelineEntry.objects.filter(
            idea_id=self.idea.id, entry_type="state_change", old_state="open", new_state="in_review"
        ).exists()

    # --- T-1.5.05: Rejected -> In Review via resubmit ---

    @unittest.mock.patch("apps.review.views._create_pdf_client")
    def test_resubmit_rejected_to_in_review(self, mock_pdf_client_factory):
        """T-1.5.05 | Integration | Rejected -> In Review via resubmit.
        Input: POST /api/ideas/:id/submit on rejected idea.
        Expected: State = in_review, new BRD version, resubmission timeline entry.
        """
        mock_client = unittest.mock.MagicMock()
        mock_client.generate_pdf.return_value = {"pdf_data": b"%PDF", "filename": "test.pdf"}
        mock_pdf_client_factory.return_value = mock_client

        # First submit
        self.client.post(self._url(), {}, format="json")
        self.idea.refresh_from_db()
        assert self.idea.state == "in_review"

        # Manually set to rejected (simulating reviewer action)
        self.idea.state = "rejected"
        self.idea.save(update_fields=["state"])

        # Resubmit
        response = self.client.post(self._url(), {"message": "Fixed issues"}, format="json")
        assert response.status_code == 200, response.json()
        data = response.json()
        assert data["state"] == "in_review"
        assert data["version_number"] == 2

        self.idea.refresh_from_db()
        assert self.idea.state == "in_review"

        assert BrdVersion.objects.filter(idea_id=self.idea.id).count() == 2
        assert ReviewTimelineEntry.objects.filter(
            idea_id=self.idea.id, entry_type="resubmission"
        ).exists()

    # --- T-4.7.01: Submit creates immutable BRD version ---

    @unittest.mock.patch("apps.review.views._create_pdf_client")
    def test_submit_creates_brd_version(self, mock_pdf_client_factory):
        """T-4.7.01 | Integration | Submit creates immutable BRD version.
        Input: POST /api/ideas/:id/submit.
        Expected: New brd_versions row with correct section content.
        """
        mock_client = unittest.mock.MagicMock()
        mock_client.generate_pdf.return_value = {"pdf_data": b"%PDF", "filename": "test.pdf"}
        mock_pdf_client_factory.return_value = mock_client

        response = self.client.post(self._url(), {}, format="json")
        assert response.status_code == 200

        version = BrdVersion.objects.get(idea_id=self.idea.id, version_number=1)
        assert version.section_title == "My Title"
        assert version.section_short_description == "My Description"
        assert version.section_current_workflow == "Current workflow"
        assert version.section_affected_department == "IT"
        assert version.section_core_capabilities == "Capabilities"
        assert version.section_success_criteria == "Success criteria"

    # --- T-4.10.01: Submit with reviewer IDs creates assignments ---

    @unittest.mock.patch("apps.review.views._create_pdf_client")
    def test_submit_with_reviewers_creates_assignments(self, mock_pdf_client_factory):
        """T-4.10.01 | Integration | Submit with reviewer IDs creates assignments.
        Input: POST submit with reviewer_ids.
        Expected: review_assignments created.
        """
        mock_client = unittest.mock.MagicMock()
        mock_client.generate_pdf.return_value = {"pdf_data": b"%PDF", "filename": "test.pdf"}
        mock_pdf_client_factory.return_value = mock_client

        response = self.client.post(
            self._url(),
            {"reviewer_ids": [str(self.reviewer1.id), str(self.reviewer2.id)]},
            format="json",
        )
        assert response.status_code == 200

        assignments = ReviewAssignment.objects.filter(idea_id=self.idea.id)
        assert assignments.count() == 2
        assert assignments.filter(reviewer_id=self.reviewer1.id, assigned_by="submitter").exists()
        assert assignments.filter(reviewer_id=self.reviewer2.id, assigned_by="submitter").exists()

    # --- T-4.10.02: Submit without reviewers goes to shared queue ---

    @unittest.mock.patch("apps.review.views._create_pdf_client")
    def test_submit_without_reviewers(self, mock_pdf_client_factory):
        """T-4.10.02 | Integration | Submit without reviewers goes to shared queue.
        Input: POST submit without reviewer_ids.
        Expected: No review_assignments, idea appears in unassigned list.
        """
        mock_client = unittest.mock.MagicMock()
        mock_client.generate_pdf.return_value = {"pdf_data": b"%PDF", "filename": "test.pdf"}
        mock_pdf_client_factory.return_value = mock_client

        response = self.client.post(self._url(), {}, format="json")
        assert response.status_code == 200

        assert ReviewAssignment.objects.filter(idea_id=self.idea.id).count() == 0

    # --- API-SUBMIT.01: Success ---

    @unittest.mock.patch("apps.review.views._create_pdf_client")
    def test_submit_success(self, mock_pdf_client_factory):
        """API-SUBMIT.01 | POST /api/ideas/:id/submit | Success.
        Input: Valid request.
        Expected: 200 with version data.
        """
        mock_client = unittest.mock.MagicMock()
        mock_client.generate_pdf.return_value = {"pdf_data": b"%PDF", "filename": "test.pdf"}
        mock_pdf_client_factory.return_value = mock_client

        response = self.client.post(
            self._url(),
            {"message": "Please review", "reviewer_ids": [str(self.reviewer1.id)]},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["version_number"] == 1
        assert "pdf_url" in data
        assert data["state"] == "in_review"

    # --- API-SUBMIT.02: Invalid state ---

    def test_submit_invalid_state(self):
        """API-SUBMIT.02 | POST /api/ideas/:id/submit | Invalid state.
        Input: Idea state = accepted.
        Expected: 400 INVALID_STATE.
        """
        self.idea.state = "accepted"
        self.idea.save(update_fields=["state"])

        response = self.client.post(self._url(), {}, format="json")
        assert response.status_code == 400
        assert response.json()["error"] == "INVALID_STATE"

    def test_submit_invalid_state_in_review(self):
        """Submit on in_review idea returns 400."""
        self.idea.state = "in_review"
        self.idea.save(update_fields=["state"])

        response = self.client.post(self._url(), {}, format="json")
        assert response.status_code == 400
        assert response.json()["error"] == "INVALID_STATE"

    def test_submit_invalid_state_dropped(self):
        """Submit on dropped idea returns 400."""
        self.idea.state = "dropped"
        self.idea.save(update_fields=["state"])

        response = self.client.post(self._url(), {}, format="json")
        assert response.status_code == 400
        assert response.json()["error"] == "INVALID_STATE"

    # --- API-SUBMIT.03: Access control ---

    def test_submit_non_owner_forbidden(self):
        """API-SUBMIT.03 | POST /api/ideas/:id/submit | Access control.
        Input: Non-owner.
        Expected: 403 ACCESS_DENIED.
        """
        self._login_as(self.user2)
        response = self.client.post(self._url(), {}, format="json")
        assert response.status_code == 403
        assert response.json()["error"] == "ACCESS_DENIED"

    # --- API-SUBMIT.04: PDF failure ---

    @unittest.mock.patch("apps.review.views._create_pdf_client")
    def test_submit_pdf_failure(self, mock_pdf_client_factory):
        """API-SUBMIT.04 | POST /api/ideas/:id/submit | PDF failure.
        Input: PDF service down.
        Expected: 503 PDF_GENERATION_FAILED.
        """
        mock_client = unittest.mock.MagicMock()
        mock_client.generate_pdf.side_effect = Exception("PDF service unavailable")
        mock_pdf_client_factory.return_value = mock_client

        response = self.client.post(self._url(), {}, format="json")
        assert response.status_code == 503
        assert response.json()["error"] == "PDF_GENERATION_FAILED"

        # State should NOT have changed
        self.idea.refresh_from_db()
        assert self.idea.state == "open"

    # --- Submit message creates comment timeline entry ---

    @unittest.mock.patch("apps.review.views._create_pdf_client")
    def test_submit_message_creates_comment(self, mock_pdf_client_factory):
        """Submit with message creates comment entry in timeline."""
        mock_client = unittest.mock.MagicMock()
        mock_client.generate_pdf.return_value = {"pdf_data": b"%PDF", "filename": "test.pdf"}
        mock_pdf_client_factory.return_value = mock_client

        response = self.client.post(
            self._url(), {"message": "Please review this carefully"}, format="json"
        )
        assert response.status_code == 200

        assert ReviewTimelineEntry.objects.filter(
            idea_id=self.idea.id,
            entry_type="comment",
            content="Please review this carefully",
        ).exists()

    # --- Sequential version numbering ---

    @unittest.mock.patch("apps.review.views._create_pdf_client")
    def test_version_numbers_are_sequential(self, mock_pdf_client_factory):
        """Version numbers increment sequentially."""
        mock_client = unittest.mock.MagicMock()
        mock_client.generate_pdf.return_value = {"pdf_data": b"%PDF", "filename": "test.pdf"}
        mock_pdf_client_factory.return_value = mock_client

        # First submit
        response = self.client.post(self._url(), {}, format="json")
        assert response.json()["version_number"] == 1

        # Reject and resubmit
        self.idea.state = "rejected"
        self.idea.save(update_fields=["state"])
        response = self.client.post(self._url(), {}, format="json")
        assert response.json()["version_number"] == 2
