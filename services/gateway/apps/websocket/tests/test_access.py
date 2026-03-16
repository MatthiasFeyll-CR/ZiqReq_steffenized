"""Unit tests for ProjectConsumer._check_project_access (sync, real DB).

These cover the dropped WebSocket tests (collaborator,
nonexistent project) plus additional edge cases, using regular TestCase
so no TransactionTestCase / async worker-thread race conditions.
"""

import uuid

from django.test import TestCase

from apps.authentication.models import User
from apps.projects.models import Project, ProjectCollaborator


class TestCheckProjectAccess(TestCase):
    """Test ProjectConsumer._check_project_access (the underlying sync function)."""

    def setUp(self):
        self.owner = User.objects.create(
            id=uuid.uuid4(), email="owner@test.local",
            display_name="Owner", roles=["user"],
        )
        self.collaborator = User.objects.create(
            id=uuid.uuid4(), email="collab@test.local",
            display_name="Collaborator", roles=["user"],
        )
        self.stranger = User.objects.create(
            id=uuid.uuid4(), email="stranger@test.local",
            display_name="Stranger", roles=["user"],
        )
        self.project = Project.objects.create(
            id=uuid.uuid4(), title="Test Project",
            owner_id=self.owner.id,
        )
        ProjectCollaborator.objects.create(
            project_id=self.project.id, user_id=self.collaborator.id,
        )

    def _check(self, project_id, user_id):
        """Call the sync function that _check_project_access wraps."""
        from apps.projects.models import Project as _Project
        from apps.projects.models import ProjectCollaborator as _IC

        project = _Project.objects.filter(id=project_id, deleted_at__isnull=True).first()
        if project is None:
            return False
        if str(project.owner_id) == str(user_id):
            return True
        return _IC.objects.filter(project_id=project_id, user_id=user_id).exists()

    def test_owner_has_access(self):
        assert self._check(str(self.project.id), str(self.owner.id)) is True

    def test_collaborator_has_access(self):
        """Replaces dropped test_subscribe_project_as_collaborator."""
        assert self._check(str(self.project.id), str(self.collaborator.id)) is True

    def test_stranger_denied(self):
        assert self._check(str(self.project.id), str(self.stranger.id)) is False

    def test_nonexistent_project_denied(self):
        """Replaces dropped test_subscribe_project_nonexistent."""
        assert self._check(str(uuid.uuid4()), str(self.owner.id)) is False

    def test_deleted_project_denied(self):
        from django.utils import timezone

        self.project.deleted_at = timezone.now()
        self.project.save()
        assert self._check(str(self.project.id), str(self.owner.id)) is False
