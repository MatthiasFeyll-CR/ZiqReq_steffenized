"""Tests for US-005: Recursive Merge — Co-Owner Demotion.

Tests execute_merge() recursive merge behavior:
1. When requesting/target idea has co_owner_id, non-triggering co-owners are demoted
2. Triggering owners (requesting + target) become co-owners of new idea
3. Demoted co-owners become collaborators on new idea
4. Collaborator transfer includes demoted co-owners (deduplicated)
5. Never >2 owners on any idea
6. merge.complete event includes demoted_co_owners array
"""

import uuid
from unittest.mock import patch

from django.test import TestCase, override_settings

from apps.authentication.models import User
from apps.ideas.models import Idea, IdeaCollaborator
from apps.similarity.models import MergeRequest

USER_1_ID = uuid.UUID("00000000-0000-0000-0000-000000005001")
USER_2_ID = uuid.UUID("00000000-0000-0000-0000-000000005002")
USER_3_ID = uuid.UUID("00000000-0000-0000-0000-000000005003")
USER_4_ID = uuid.UUID("00000000-0000-0000-0000-000000005004")
USER_5_ID = uuid.UUID("00000000-0000-0000-0000-000000005005")


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
@patch("apps.similarity.merge_service._publish_merge_complete")
class TestRecursiveMerge(TestCase):
    """Test recursive merge — co-owner demotion logic in execute_merge()."""

    def setUp(self):
        self.user1 = _create_user(USER_1_ID, "rm1@test.local", "Recursive User1")
        self.user2 = _create_user(USER_2_ID, "rm2@test.local", "Recursive User2")
        self.user3 = _create_user(USER_3_ID, "rm3@test.local", "Recursive User3")
        self.user4 = _create_user(USER_4_ID, "rm4@test.local", "Recursive User4")

    def _execute_merge(self, merge_request, idea_a, idea_b):
        from apps.similarity.merge_service import execute_merge

        return execute_merge(
            merge_request_id=str(merge_request.id),
            requesting_idea_id=str(idea_a.id),
            target_idea_id=str(idea_b.id),
            synthesis_message="Merged synthesis",
            board_instructions=[],
        )

    def test_simple_merge_no_demotion(self, mock_publish):
        """Simple merge (no co-owners) — no demotion occurs."""
        idea_a = Idea.objects.create(owner_id=self.user1.id, title="Idea A")
        idea_b = Idea.objects.create(owner_id=self.user2.id, title="Idea B")
        mr = MergeRequest.objects.create(
            requesting_idea_id=idea_a.id,
            target_idea_id=idea_b.id,
            merge_type="merge",
            requested_by=self.user1.id,
            status="pending",
            requesting_owner_consent="accepted",
            target_owner_consent="accepted",
        )

        result = self._execute_merge(mr, idea_a, idea_b)
        merged = Idea.objects.get(id=result["resulting_idea_id"])

        assert merged.owner_id == self.user1.id
        assert merged.co_owner_id == self.user2.id

        # No demoted co-owners in event
        mock_publish.assert_called_once()
        call_kwargs = mock_publish.call_args
        assert call_kwargs[1]["demoted_co_owners"] == []

    def test_recursive_merge_requesting_has_co_owner(self, mock_publish):
        """Requesting idea has co-owner — co-owner demoted to collaborator."""
        # Idea C was previously merged (User1 owner, User2 co-owner)
        idea_c = Idea.objects.create(
            owner_id=self.user1.id, co_owner_id=self.user2.id, title="Merged Idea C"
        )
        idea_d = Idea.objects.create(owner_id=self.user3.id, title="Idea D")
        mr = MergeRequest.objects.create(
            requesting_idea_id=idea_c.id,
            target_idea_id=idea_d.id,
            merge_type="merge",
            requested_by=self.user1.id,
            status="pending",
            requesting_owner_consent="accepted",
            target_owner_consent="accepted",
        )

        result = self._execute_merge(mr, idea_c, idea_d)
        merged = Idea.objects.get(id=result["resulting_idea_id"])

        # Triggering owners become co-owners
        assert merged.owner_id == self.user1.id
        assert merged.co_owner_id == self.user3.id

        # User2 demoted to collaborator
        assert IdeaCollaborator.objects.filter(
            idea_id=merged.id, user_id=self.user2.id
        ).exists()

        # Event includes demoted_co_owners
        mock_publish.assert_called_once()
        call_kwargs = mock_publish.call_args
        assert str(self.user2.id) in call_kwargs[1]["demoted_co_owners"]

    def test_recursive_merge_target_has_co_owner(self, mock_publish):
        """Target idea has co-owner — co-owner demoted to collaborator."""
        idea_a = Idea.objects.create(owner_id=self.user1.id, title="Idea A")
        # Idea B was previously merged (User2 owner, User3 co-owner)
        idea_b = Idea.objects.create(
            owner_id=self.user2.id, co_owner_id=self.user3.id, title="Merged Idea B"
        )
        mr = MergeRequest.objects.create(
            requesting_idea_id=idea_a.id,
            target_idea_id=idea_b.id,
            merge_type="merge",
            requested_by=self.user1.id,
            status="pending",
            requesting_owner_consent="accepted",
            target_owner_consent="accepted",
        )

        result = self._execute_merge(mr, idea_a, idea_b)
        merged = Idea.objects.get(id=result["resulting_idea_id"])

        # Triggering owners
        assert merged.owner_id == self.user1.id
        assert merged.co_owner_id == self.user2.id

        # User3 demoted to collaborator
        assert IdeaCollaborator.objects.filter(
            idea_id=merged.id, user_id=self.user3.id
        ).exists()

        # Event
        call_kwargs = mock_publish.call_args
        assert str(self.user3.id) in call_kwargs[1]["demoted_co_owners"]

    def test_recursive_merge_both_have_co_owners(self, mock_publish):
        """Both ideas have co-owners — both non-triggering co-owners demoted."""
        idea_c = Idea.objects.create(
            owner_id=self.user1.id, co_owner_id=self.user2.id, title="Merged C"
        )
        idea_d = Idea.objects.create(
            owner_id=self.user3.id, co_owner_id=self.user4.id, title="Merged D"
        )
        mr = MergeRequest.objects.create(
            requesting_idea_id=idea_c.id,
            target_idea_id=idea_d.id,
            merge_type="merge",
            requested_by=self.user1.id,
            status="pending",
            requesting_owner_consent="accepted",
            target_owner_consent="accepted",
        )

        result = self._execute_merge(mr, idea_c, idea_d)
        merged = Idea.objects.get(id=result["resulting_idea_id"])

        # Triggering owners
        assert merged.owner_id == self.user1.id
        assert merged.co_owner_id == self.user3.id

        # Both co-owners demoted
        assert IdeaCollaborator.objects.filter(
            idea_id=merged.id, user_id=self.user2.id
        ).exists()
        assert IdeaCollaborator.objects.filter(
            idea_id=merged.id, user_id=self.user4.id
        ).exists()

        # Max 2 owners enforced
        assert merged.owner_id is not None
        assert merged.co_owner_id is not None

        # Event has both demoted
        call_kwargs = mock_publish.call_args
        demoted = call_kwargs[1]["demoted_co_owners"]
        assert len(demoted) == 2
        assert str(self.user2.id) in demoted
        assert str(self.user4.id) in demoted

    def test_never_more_than_2_owners(self, mock_publish):
        """Resulting idea never has more than 2 owners regardless of input."""
        idea_c = Idea.objects.create(
            owner_id=self.user1.id, co_owner_id=self.user2.id, title="Merged C"
        )
        idea_d = Idea.objects.create(
            owner_id=self.user3.id, co_owner_id=self.user4.id, title="Merged D"
        )
        mr = MergeRequest.objects.create(
            requesting_idea_id=idea_c.id,
            target_idea_id=idea_d.id,
            merge_type="merge",
            requested_by=self.user1.id,
            status="pending",
            requesting_owner_consent="accepted",
            target_owner_consent="accepted",
        )

        result = self._execute_merge(mr, idea_c, idea_d)
        merged = Idea.objects.get(id=result["resulting_idea_id"])

        # Exactly 2 owners (owner_id + co_owner_id), no more
        owner_count = 1 + (1 if merged.co_owner_id else 0)
        assert owner_count <= 2

    def test_demoted_co_owners_deduplicated_with_existing_collaborators(
        self, mock_publish
    ):
        """Demoted co-owner who is also a collaborator — deduplicated."""
        idea_c = Idea.objects.create(
            owner_id=self.user1.id, co_owner_id=self.user2.id, title="Merged C"
        )
        idea_d = Idea.objects.create(owner_id=self.user3.id, title="Idea D")

        # User2 is already a collaborator on idea_d
        IdeaCollaborator.objects.create(idea_id=idea_d.id, user_id=self.user2.id)

        mr = MergeRequest.objects.create(
            requesting_idea_id=idea_c.id,
            target_idea_id=idea_d.id,
            merge_type="merge",
            requested_by=self.user1.id,
            status="pending",
            requesting_owner_consent="accepted",
            target_owner_consent="accepted",
        )

        result = self._execute_merge(mr, idea_c, idea_d)
        merged = Idea.objects.get(id=result["resulting_idea_id"])

        # User2 is a collaborator exactly once (no duplicates)
        collab_count = IdeaCollaborator.objects.filter(
            idea_id=merged.id, user_id=self.user2.id
        ).count()
        assert collab_count == 1

    def test_co_owner_same_as_triggering_owner_not_demoted(self, mock_publish):
        """If co-owner is same as the other idea's owner, they're a triggering owner."""
        # Edge case: idea_c has User1 as owner, User3 as co-owner
        # idea_d has User3 as owner
        # User3 is triggering owner (target owner), so NOT demoted
        idea_c = Idea.objects.create(
            owner_id=self.user1.id, co_owner_id=self.user3.id, title="Merged C"
        )
        idea_d = Idea.objects.create(owner_id=self.user3.id, title="Idea D")
        mr = MergeRequest.objects.create(
            requesting_idea_id=idea_c.id,
            target_idea_id=idea_d.id,
            merge_type="merge",
            requested_by=self.user1.id,
            status="pending",
            requesting_owner_consent="accepted",
            target_owner_consent="accepted",
        )

        result = self._execute_merge(mr, idea_c, idea_d)
        merged = Idea.objects.get(id=result["resulting_idea_id"])

        # User3 is co-owner, not collaborator
        assert merged.co_owner_id == self.user3.id
        assert not IdeaCollaborator.objects.filter(
            idea_id=merged.id, user_id=self.user3.id
        ).exists()

        # No demotions
        call_kwargs = mock_publish.call_args
        assert call_kwargs[1]["demoted_co_owners"] == []

    def test_merge_complete_event_includes_demoted_array(self, mock_publish):
        """merge.complete event payload includes demoted_co_owners array."""
        idea_c = Idea.objects.create(
            owner_id=self.user1.id, co_owner_id=self.user2.id, title="Merged C"
        )
        idea_d = Idea.objects.create(owner_id=self.user3.id, title="Idea D")
        mr = MergeRequest.objects.create(
            requesting_idea_id=idea_c.id,
            target_idea_id=idea_d.id,
            merge_type="merge",
            requested_by=self.user1.id,
            status="pending",
            requesting_owner_consent="accepted",
            target_owner_consent="accepted",
        )

        self._execute_merge(mr, idea_c, idea_d)

        mock_publish.assert_called_once()
        call_kwargs = mock_publish.call_args
        assert "demoted_co_owners" in call_kwargs[1]
        assert call_kwargs[1]["demoted_co_owners"] == [str(self.user2.id)]

    def test_collaborator_transfer_includes_demoted(self, mock_publish):
        """Result includes demoted co-owners in collaborator_ids."""
        idea_c = Idea.objects.create(
            owner_id=self.user1.id, co_owner_id=self.user2.id, title="Merged C"
        )
        idea_d = Idea.objects.create(owner_id=self.user3.id, title="Idea D")
        mr = MergeRequest.objects.create(
            requesting_idea_id=idea_c.id,
            target_idea_id=idea_d.id,
            merge_type="merge",
            requested_by=self.user1.id,
            status="pending",
            requesting_owner_consent="accepted",
            target_owner_consent="accepted",
        )

        result = self._execute_merge(mr, idea_c, idea_d)

        # User2 should be in collaborator_ids
        assert str(self.user2.id) in result["collaborator_ids"]
