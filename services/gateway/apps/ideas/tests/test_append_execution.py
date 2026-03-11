"""Tests for US-002: Append Execution — Close & Collaborator Add.

Tests execute_append() which:
1. Sets requesting idea closed_by_append_id = target_idea_id (state stays 'open')
2. Adds requesting owner as collaborator on target idea
3. Updates merge_request status='accepted', resolved_at=now()
4. Publishes append.complete event
5. No new idea created
6. Atomic transaction
"""

import uuid
from unittest.mock import patch

from django.test import TestCase, override_settings

from apps.authentication.models import User
from apps.ideas.models import Idea, IdeaCollaborator
from apps.similarity.models import MergeRequest

USER_1_ID = uuid.UUID("00000000-0000-0000-0000-000000002001")
USER_2_ID = uuid.UUID("00000000-0000-0000-0000-000000002002")
USER_3_ID = uuid.UUID("00000000-0000-0000-0000-000000002003")


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
@patch("apps.similarity.append_service._publish_append_complete")
class TestExecuteAppend(TestCase):
    """Test execute_append() service function."""

    def setUp(self):
        self.user1 = _create_user(USER_1_ID, "ae1@test.local", "Append Exec1")
        self.user2 = _create_user(USER_2_ID, "ae2@test.local", "Append Exec2")

        self.idea_a = Idea.objects.create(
            owner_id=self.user1.id, title="Requesting Idea A"
        )
        self.idea_b = Idea.objects.create(
            owner_id=self.user2.id, title="Target Idea B", state="in_review"
        )

        self.merge_request = MergeRequest.objects.create(
            requesting_idea_id=self.idea_a.id,
            target_idea_id=self.idea_b.id,
            merge_type="append",
            requested_by=self.user1.id,
            status="pending",
            requesting_owner_consent="accepted",
            target_owner_consent="accepted",
            reviewer_consent="accepted",
        )

    def _execute(self):
        from apps.similarity.append_service import execute_append

        return execute_append(
            merge_request_id=str(self.merge_request.id),
            requesting_idea_id=str(self.idea_a.id),
            target_idea_id=str(self.idea_b.id),
        )

    def test_requesting_idea_flagged_with_closed_by_append_id(self, mock_publish):
        """Requesting idea gets closed_by_append_id = target idea id."""
        self._execute()
        self.idea_a.refresh_from_db()
        assert self.idea_a.closed_by_append_id == self.idea_b.id

    def test_requesting_idea_state_stays_open(self, mock_publish):
        """Requesting idea state stays 'open' (not changed)."""
        self._execute()
        self.idea_a.refresh_from_db()
        assert self.idea_a.state == "open"

    def test_requesting_owner_added_as_collaborator(self, mock_publish):
        """Requesting owner is added as collaborator on target idea."""
        self._execute()
        assert IdeaCollaborator.objects.filter(
            idea=self.idea_b, user_id=self.user1.id
        ).exists()

    def test_target_state_stays_in_review(self, mock_publish):
        """Target idea state stays 'in_review'."""
        self._execute()
        self.idea_b.refresh_from_db()
        assert self.idea_b.state == "in_review"

    def test_merge_request_status_accepted(self, mock_publish):
        """Merge request status updated to 'accepted'."""
        self._execute()
        self.merge_request.refresh_from_db()
        assert self.merge_request.status == "accepted"

    def test_merge_request_resolved_at_set(self, mock_publish):
        """Merge request resolved_at is set."""
        self._execute()
        self.merge_request.refresh_from_db()
        assert self.merge_request.resolved_at is not None

    def test_no_new_idea_created(self, mock_publish):
        """No new idea is created by append execution."""
        idea_count_before = Idea.objects.count()
        self._execute()
        idea_count_after = Idea.objects.count()
        assert idea_count_after == idea_count_before

    def test_publishes_append_complete_event(self, mock_publish):
        """Publishes append.complete event with correct payload."""
        self._execute()
        mock_publish.assert_called_once()
        call_kwargs = mock_publish.call_args[1]
        assert call_kwargs["merge_request_id"] == str(self.merge_request.id)
        assert call_kwargs["requesting_idea_id"] == str(self.idea_a.id)
        assert call_kwargs["target_idea_id"] == str(self.idea_b.id)
        assert call_kwargs["requesting_owner_id"] == str(self.user1.id)
        assert call_kwargs["target_owner_id"] == str(self.user2.id)
        assert str(self.user1.id) in call_kwargs["target_collaborator_ids"]

    def test_idempotent_collaborator_add(self, mock_publish):
        """Adding collaborator is idempotent (no duplicate if already exists)."""
        IdeaCollaborator.objects.create(idea=self.idea_b, user_id=self.user1.id)
        self._execute()
        count = IdeaCollaborator.objects.filter(
            idea=self.idea_b, user_id=self.user1.id
        ).count()
        assert count == 1

    def test_existing_collaborators_preserved(self, mock_publish):
        """Existing collaborators on target are preserved."""
        user3 = _create_user(USER_3_ID, "ae3@test.local", "Append Exec3")
        IdeaCollaborator.objects.create(idea=self.idea_b, user_id=user3.id)
        self._execute()
        assert IdeaCollaborator.objects.filter(
            idea=self.idea_b, user_id=user3.id
        ).exists()
        assert IdeaCollaborator.objects.filter(
            idea=self.idea_b, user_id=self.user1.id
        ).exists()

    def test_result_contains_expected_keys(self, mock_publish):
        """Return value contains target_idea_id and requesting_owner_id."""
        result = self._execute()
        assert result["target_idea_id"] == str(self.idea_b.id)
        assert result["requesting_owner_id"] == str(self.user1.id)
        assert isinstance(result["target_collaborator_ids"], list)


@override_settings(DEBUG=True, AUTH_BYPASS=True)
@patch("apps.similarity.append_service._publish_append_complete")
class TestHandleAppendAcceptedConsumer(TestCase):
    """Test handle_append_accepted event consumer."""

    def setUp(self):
        self.user1 = _create_user(USER_1_ID, "ae1@test.local", "Append Exec1")
        self.user2 = _create_user(USER_2_ID, "ae2@test.local", "Append Exec2")

        self.idea_a = Idea.objects.create(
            owner_id=self.user1.id, title="Consumer Idea A"
        )
        self.idea_b = Idea.objects.create(
            owner_id=self.user2.id, title="Consumer Idea B", state="in_review"
        )

        self.merge_request = MergeRequest.objects.create(
            requesting_idea_id=self.idea_a.id,
            target_idea_id=self.idea_b.id,
            merge_type="append",
            requested_by=self.user1.id,
            status="pending",
            requesting_owner_consent="accepted",
            target_owner_consent="accepted",
            reviewer_consent="accepted",
        )

    def test_consumer_calls_execute_append(self, mock_publish):
        """handle_append_accepted consumer triggers execute_append correctly."""
        from events.append_consumer import handle_append_accepted

        payload = {
            "merge_request_id": str(self.merge_request.id),
            "requesting_idea_id": str(self.idea_a.id),
            "target_idea_id": str(self.idea_b.id),
        }
        result = handle_append_accepted(payload)

        # Verify the append was executed
        self.idea_a.refresh_from_db()
        assert self.idea_a.closed_by_append_id == self.idea_b.id
        assert IdeaCollaborator.objects.filter(
            idea=self.idea_b, user_id=self.user1.id
        ).exists()
        assert result["target_idea_id"] == str(self.idea_b.id)
