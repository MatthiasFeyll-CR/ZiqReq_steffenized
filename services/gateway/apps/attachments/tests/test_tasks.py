"""Tests for attachment Celery tasks: orphan_cleanup, storage_cleanup, bulk_delete_storage."""

import uuid
from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.utils import timezone

from apps.projects.models import Attachment, Project


def _make_project(**overrides):
    defaults = {"title": "Test Project", "owner_id": uuid.uuid4()}
    defaults.update(overrides)
    return Project.objects.create(**defaults)


def _make_attachment(project, **overrides):
    defaults = {
        "project": project,
        "uploader_id": uuid.uuid4(),
        "filename": "test.pdf",
        "storage_key": f"attachments/{project.id}/{uuid.uuid4()}.pdf",
        "content_type": "application/pdf",
        "size_bytes": 1024,
    }
    defaults.update(overrides)
    return Attachment.objects.create(**defaults)


class TestOrphanCleanup(TestCase):
    """Tests for attachments.orphan_cleanup task."""

    def setUp(self):
        self.project = _make_project()

    @patch("apps.admin_config.services.get_parameter", return_value=96)
    def test_soft_deletes_orphaned_attachments_past_ttl(self, _mock_param):
        from apps.attachments.tasks import orphan_cleanup

        # Orphan past TTL: no message, created 5 days ago
        orphan = _make_attachment(self.project, message_id=None)
        Attachment.objects.filter(id=orphan.id).update(
            created_at=timezone.now() - timedelta(hours=100)
        )

        result = orphan_cleanup()

        orphan.refresh_from_db()
        assert orphan.deleted_at is not None
        assert result["soft_deleted_count"] == 1

    @patch("apps.admin_config.services.get_parameter", return_value=96)
    def test_skips_orphans_within_ttl(self, _mock_param):
        from apps.attachments.tasks import orphan_cleanup

        # Orphan within TTL: created 1 hour ago
        recent_orphan = _make_attachment(self.project, message_id=None)
        Attachment.objects.filter(id=recent_orphan.id).update(
            created_at=timezone.now() - timedelta(hours=1)
        )

        result = orphan_cleanup()

        recent_orphan.refresh_from_db()
        assert recent_orphan.deleted_at is None
        assert result["soft_deleted_count"] == 0

    @patch("apps.admin_config.services.get_parameter", return_value=96)
    def test_skips_message_linked_attachments(self, _mock_param):
        from apps.attachments.tasks import orphan_cleanup

        # Linked to a message — not an orphan
        linked = _make_attachment(self.project, message_id=uuid.uuid4())
        Attachment.objects.filter(id=linked.id).update(
            created_at=timezone.now() - timedelta(hours=200)
        )

        result = orphan_cleanup()

        linked.refresh_from_db()
        assert linked.deleted_at is None
        assert result["soft_deleted_count"] == 0

    @patch("apps.admin_config.services.get_parameter", return_value=96)
    def test_skips_already_soft_deleted(self, _mock_param):
        from apps.attachments.tasks import orphan_cleanup

        already_deleted = _make_attachment(self.project, message_id=None)
        Attachment.objects.filter(id=already_deleted.id).update(
            created_at=timezone.now() - timedelta(hours=200),
            deleted_at=timezone.now() - timedelta(hours=50),
        )

        result = orphan_cleanup()
        assert result["soft_deleted_count"] == 0

    @patch("apps.admin_config.services.get_parameter", return_value=24)
    def test_uses_configurable_ttl(self, _mock_param):
        from apps.attachments.tasks import orphan_cleanup

        # Created 30 hours ago, TTL is 24h — should be cleaned
        orphan = _make_attachment(self.project, message_id=None)
        Attachment.objects.filter(id=orphan.id).update(
            created_at=timezone.now() - timedelta(hours=30)
        )

        result = orphan_cleanup()
        assert result["soft_deleted_count"] == 1
        assert result["ttl_hours"] == 24


class TestStorageCleanup(TestCase):
    """Tests for attachments.storage_cleanup task."""

    def setUp(self):
        self.project = _make_project()

    @patch("apps.attachments.tasks._delete_storage_files", return_value=1)
    @patch("apps.admin_config.services.get_parameter", return_value=720)
    def test_hard_deletes_expired_soft_deleted(self, _mock_param, mock_delete_files):
        from apps.attachments.tasks import storage_cleanup

        att = _make_attachment(self.project)
        Attachment.objects.filter(id=att.id).update(
            deleted_at=timezone.now() - timedelta(hours=800)
        )

        result = storage_cleanup()

        assert result["hard_deleted_count"] == 1
        assert not Attachment.objects.filter(id=att.id).exists()
        mock_delete_files.assert_called_once()
        assert att.storage_key in mock_delete_files.call_args[0][0]

    @patch("apps.attachments.tasks._delete_storage_files")
    @patch("apps.admin_config.services.get_parameter", return_value=720)
    def test_skips_recently_soft_deleted(self, _mock_param, mock_delete_files):
        from apps.attachments.tasks import storage_cleanup

        att = _make_attachment(self.project)
        Attachment.objects.filter(id=att.id).update(
            deleted_at=timezone.now() - timedelta(hours=10)
        )

        result = storage_cleanup()

        assert result["hard_deleted_count"] == 0
        assert Attachment.objects.filter(id=att.id).exists()
        mock_delete_files.assert_not_called()

    @patch("apps.attachments.tasks._delete_storage_files")
    @patch("apps.admin_config.services.get_parameter", return_value=720)
    def test_skips_active_attachments(self, _mock_param, mock_delete_files):
        from apps.attachments.tasks import storage_cleanup

        _make_attachment(self.project)  # active, no deleted_at

        result = storage_cleanup()
        assert result["hard_deleted_count"] == 0


class TestBulkDeleteStorage(TestCase):
    """Tests for attachments.bulk_delete_storage task."""

    def setUp(self):
        self.project = _make_project()

    @patch("apps.attachments.tasks._delete_storage_files", return_value=2)
    def test_deletes_valid_storage_keys(self, mock_delete_files):
        from apps.attachments.tasks import bulk_delete_storage

        att1 = _make_attachment(self.project, filename="f1.pdf")
        att2 = _make_attachment(self.project, filename="f2.pdf")
        keys = [att1.storage_key, att2.storage_key]

        result = bulk_delete_storage(keys)

        assert result["requested"] == 2
        assert result["valid"] == 2
        assert result["deleted"] == 2

    @patch("apps.attachments.tasks._delete_storage_files", return_value=1)
    def test_skips_unknown_keys(self, mock_delete_files):
        from apps.attachments.tasks import bulk_delete_storage

        att = _make_attachment(self.project)
        keys = [att.storage_key, "fake/nonexistent/key.pdf"]

        result = bulk_delete_storage(keys)

        assert result["requested"] == 2
        assert result["valid"] == 1

    @patch("apps.attachments.tasks._delete_storage_files")
    def test_empty_keys_list(self, mock_delete_files):
        from apps.attachments.tasks import bulk_delete_storage

        result = bulk_delete_storage([])
        assert result["requested"] == 0
        assert result["valid"] == 0
        assert result["deleted"] == 0
        mock_delete_files.assert_not_called()


class TestDeleteStorageFiles(TestCase):
    """Tests for _delete_storage_files helper."""

    @patch("storage.factory.get_storage_backend")
    def test_deletes_all_keys(self, mock_backend_factory):
        from apps.attachments.tasks import _delete_storage_files

        mock_backend = MagicMock()
        mock_backend_factory.return_value = mock_backend

        count = _delete_storage_files(["key1", "key2", "key3"])

        assert count == 3
        assert mock_backend.delete_file.call_count == 3

    @patch("storage.factory.get_storage_backend")
    def test_continues_on_individual_failure(self, mock_backend_factory):
        from apps.attachments.tasks import _delete_storage_files

        mock_backend = MagicMock()
        mock_backend.delete_file.side_effect = [None, Exception("fail"), None]
        mock_backend_factory.return_value = mock_backend

        count = _delete_storage_files(["key1", "key2", "key3"])

        assert count == 2  # 2 succeeded, 1 failed
        assert mock_backend.delete_file.call_count == 3
