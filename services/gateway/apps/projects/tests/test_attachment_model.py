import uuid

from django.test import TestCase
from django.utils import timezone

from apps.projects.models import Attachment, Project

USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


class TestAttachmentModel(TestCase):
    """Tests for the Attachment model — CRUD, helper methods, constraints."""

    def setUp(self):
        self.project = Project.objects.create(
            title="Test Project",
            owner_id=USER_ID,
        )

    def _make_attachment(self, **overrides):
        defaults = {
            "project": self.project,
            "uploader_id": USER_ID,
            "filename": "test.pdf",
            "storage_key": f"attachments/{self.project.id}/{uuid.uuid4()}.pdf",
            "content_type": "application/pdf",
            "size_bytes": 1024,
        }
        defaults.update(overrides)
        return Attachment.objects.create(**defaults)

    # --- CRUD ---

    def test_create_attachment(self):
        att = self._make_attachment()
        self.assertIsNotNone(att.id)
        self.assertEqual(att.project_id, self.project.id)
        self.assertEqual(att.filename, "test.pdf")
        self.assertEqual(att.extraction_status, "pending")
        self.assertIsNone(att.message_id)
        self.assertIsNone(att.deleted_at)
        self.assertIsNotNone(att.created_at)

    def test_read_attachment(self):
        att = self._make_attachment()
        fetched = Attachment.objects.get(id=att.id)
        self.assertEqual(fetched.filename, "test.pdf")
        self.assertEqual(fetched.size_bytes, 1024)

    def test_update_attachment(self):
        att = self._make_attachment()
        msg_id = uuid.uuid4()
        att.message_id = msg_id
        att.extraction_status = "completed"
        att.extracted_content = "Some extracted text"
        att.save()
        att.refresh_from_db()
        self.assertEqual(att.message_id, msg_id)
        self.assertEqual(att.extraction_status, "completed")
        self.assertEqual(att.extracted_content, "Some extracted text")

    def test_delete_attachment(self):
        att = self._make_attachment()
        att_id = att.id
        att.delete()
        self.assertFalse(Attachment.objects.filter(id=att_id).exists())

    def test_soft_delete(self):
        att = self._make_attachment()
        att.deleted_at = timezone.now()
        att.save()
        att.refresh_from_db()
        self.assertIsNotNone(att.deleted_at)
        # Still exists in DB
        self.assertTrue(Attachment.objects.filter(id=att.id).exists())

    # --- Extraction status choices ---

    def test_extraction_status_choices(self):
        for status in ("pending", "processing", "completed", "failed"):
            att = self._make_attachment(extraction_status=status)
            att.refresh_from_db()
            self.assertEqual(att.extraction_status, status)

    # --- Foreign key ---

    def test_cascade_delete_with_project(self):
        att = self._make_attachment()
        att_id = att.id
        self.project.delete()
        self.assertFalse(Attachment.objects.filter(id=att_id).exists())

    # --- Helper methods ---

    def test_active_count_for_project_empty(self):
        count = Attachment.active_count_for_project(self.project.id)
        self.assertEqual(count, 0)

    def test_active_count_for_project_with_active(self):
        self._make_attachment()
        self._make_attachment(filename="file2.png")
        count = Attachment.active_count_for_project(self.project.id)
        self.assertEqual(count, 2)

    def test_active_count_excludes_soft_deleted(self):
        self._make_attachment()
        deleted = self._make_attachment(filename="deleted.pdf")
        deleted.deleted_at = timezone.now()
        deleted.save()
        count = Attachment.active_count_for_project(self.project.id)
        self.assertEqual(count, 1)

    def test_active_count_for_different_project(self):
        self._make_attachment()
        other_project = Project.objects.create(title="Other", owner_id=USER_ID)
        count = Attachment.active_count_for_project(other_project.id)
        self.assertEqual(count, 0)

    # --- Fields ---

    def test_message_id_nullable(self):
        att = self._make_attachment(message_id=None)
        self.assertIsNone(att.message_id)

    def test_message_id_set(self):
        msg_id = uuid.uuid4()
        att = self._make_attachment(message_id=msg_id)
        att.refresh_from_db()
        self.assertEqual(att.message_id, msg_id)

    def test_thumbnail_storage_key_nullable(self):
        att = self._make_attachment(thumbnail_storage_key=None)
        self.assertIsNone(att.thumbnail_storage_key)

    def test_extracted_content_nullable(self):
        att = self._make_attachment(extracted_content=None)
        self.assertIsNone(att.extracted_content)

    def test_str_representation(self):
        att = self._make_attachment(filename="report.pdf")
        self.assertIn("report.pdf", str(att))
        self.assertIn(str(att.id), str(att))
