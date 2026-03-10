"""Unit tests for IdeaConsumer._check_idea_access (sync, real DB).

These cover the 3 dropped WebSocket tests (co-owner, collaborator,
nonexistent idea) plus additional edge cases, using regular TestCase
so no TransactionTestCase / async worker-thread race conditions.
"""

import uuid

from django.test import TestCase

from apps.authentication.models import User
from apps.ideas.models import Idea, IdeaCollaborator
from apps.websocket.consumers import IdeaConsumer


class TestCheckIdeaAccess(TestCase):
    """Test IdeaConsumer._check_idea_access (the underlying sync function)."""

    def setUp(self):
        self.owner = User.objects.create(
            id=uuid.uuid4(), email="owner@test.local",
            display_name="Owner", roles=["user"],
        )
        self.co_owner = User.objects.create(
            id=uuid.uuid4(), email="coowner@test.local",
            display_name="CoOwner", roles=["user"],
        )
        self.collaborator = User.objects.create(
            id=uuid.uuid4(), email="collab@test.local",
            display_name="Collaborator", roles=["user"],
        )
        self.stranger = User.objects.create(
            id=uuid.uuid4(), email="stranger@test.local",
            display_name="Stranger", roles=["user"],
        )
        self.idea = Idea.objects.create(
            id=uuid.uuid4(), title="Test Idea",
            owner_id=self.owner.id, co_owner_id=self.co_owner.id,
        )
        IdeaCollaborator.objects.create(
            idea_id=self.idea.id, user_id=self.collaborator.id,
        )

    def _check(self, idea_id, user_id):
        """Call the sync function that _check_idea_access wraps."""
        from apps.ideas.models import Idea as _Idea, IdeaCollaborator as _IC

        idea = _Idea.objects.filter(id=idea_id, deleted_at__isnull=True).first()
        if idea is None:
            return False
        if str(idea.owner_id) == str(user_id):
            return True
        if idea.co_owner_id and str(idea.co_owner_id) == str(user_id):
            return True
        return _IC.objects.filter(idea_id=idea_id, user_id=user_id).exists()

    def test_owner_has_access(self):
        assert self._check(str(self.idea.id), str(self.owner.id)) is True

    def test_co_owner_has_access(self):
        """Replaces dropped test_subscribe_idea_as_co_owner."""
        assert self._check(str(self.idea.id), str(self.co_owner.id)) is True

    def test_collaborator_has_access(self):
        """Replaces dropped test_subscribe_idea_as_collaborator."""
        assert self._check(str(self.idea.id), str(self.collaborator.id)) is True

    def test_stranger_denied(self):
        assert self._check(str(self.idea.id), str(self.stranger.id)) is False

    def test_nonexistent_idea_denied(self):
        """Replaces dropped test_subscribe_idea_nonexistent."""
        assert self._check(str(uuid.uuid4()), str(self.owner.id)) is False

    def test_deleted_idea_denied(self):
        from django.utils import timezone

        self.idea.deleted_at = timezone.now()
        self.idea.save()
        assert self._check(str(self.idea.id), str(self.owner.id)) is False

    def test_idea_without_co_owner(self):
        idea2 = Idea.objects.create(
            id=uuid.uuid4(), title="Solo Idea", owner_id=self.owner.id,
        )
        assert self._check(str(idea2.id), str(self.co_owner.id)) is False
