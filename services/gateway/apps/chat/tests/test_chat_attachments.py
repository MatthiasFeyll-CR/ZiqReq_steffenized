import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.projects.models import Attachment, ChatMessage, Project

USER_1_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
USER_2_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")


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
class TestChatAttachmentLinking(TestCase):
    """Integration tests for chat-attachment linking (US-004)."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = _create_user(USER_1_ID, "user1@test.local", "Test User1")
        self.user2 = _create_user(USER_2_ID, "user2@test.local", "Test User2")
        self.project = Project.objects.create(owner_id=self.user1.id, title="Test Project")
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.user1.id)},
            format="json",
        )

    def _chat_url(self, project_id=None):
        return f"/api/projects/{project_id or self.project.id}/chat/"

    def _create_attachment(self, **kwargs):
        defaults = {
            "project": self.project,
            "uploader_id": self.user1.id,
            "filename": "test.pdf",
            "storage_key": f"attachments/{self.project.id}/{uuid.uuid4()}.pdf",
            "content_type": "application/pdf",
            "size_bytes": 1024,
        }
        defaults.update(kwargs)
        return Attachment.objects.create(**defaults)

    # --- POST with attachment_ids ---

    def test_create_message_with_attachments(self):
        """POST with attachment_ids links attachments to message."""
        a1 = self._create_attachment(filename="doc1.pdf")
        a2 = self._create_attachment(filename="doc2.pdf")

        response = self.client.post(
            self._chat_url(),
            {"content": "Check these files", "attachment_ids": [str(a1.id), str(a2.id)]},
            format="json",
        )
        assert response.status_code == 201
        data = response.json()
        assert "attachments" in data
        assert len(data["attachments"]) == 2
        filenames = {a["filename"] for a in data["attachments"]}
        assert filenames == {"doc1.pdf", "doc2.pdf"}

        # Verify DB update
        a1.refresh_from_db()
        a2.refresh_from_db()
        assert a1.message_id == uuid.UUID(data["id"])
        assert a2.message_id == uuid.UUID(data["id"])

    def test_create_message_without_attachments(self):
        """POST without attachment_ids works normally."""
        response = self.client.post(
            self._chat_url(),
            {"content": "No attachments here"},
            format="json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["attachments"] == []

    def test_create_message_max_3_attachments(self):
        """POST with more than 3 attachment_ids is rejected."""
        ids = [str(uuid.uuid4()) for _ in range(4)]
        response = self.client.post(
            self._chat_url(),
            {"content": "Too many", "attachment_ids": ids},
            format="json",
        )
        assert response.status_code == 400

    def test_create_message_skips_invalid_attachment_ids(self):
        """POST with mix of valid and invalid IDs links only valid ones."""
        valid = self._create_attachment(filename="valid.pdf")
        fake_id = str(uuid.uuid4())

        response = self.client.post(
            self._chat_url(),
            {"content": "Partial", "attachment_ids": [str(valid.id), fake_id]},
            format="json",
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data["attachments"]) == 1
        assert data["attachments"][0]["filename"] == "valid.pdf"

    def test_create_message_skips_already_linked_attachment(self):
        """POST skips attachments that already have a message_id."""
        msg = ChatMessage.objects.create(
            project_id=self.project.id,
            sender_type="user",
            sender_id=self.user1.id,
            content="Previous",
        )
        linked = self._create_attachment(filename="linked.pdf", message_id=msg.id)

        response = self.client.post(
            self._chat_url(),
            {"content": "Try to reuse", "attachment_ids": [str(linked.id)]},
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["attachments"] == []

    def test_create_message_skips_deleted_attachment(self):
        """POST skips soft-deleted attachments."""
        from django.utils import timezone
        deleted = self._create_attachment(filename="deleted.pdf", deleted_at=timezone.now())

        response = self.client.post(
            self._chat_url(),
            {"content": "Try deleted", "attachment_ids": [str(deleted.id)]},
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["attachments"] == []

    def test_create_message_skips_other_project_attachment(self):
        """POST skips attachments belonging to a different project."""
        other_project = Project.objects.create(owner_id=self.user1.id, title="Other")
        other_att = self._create_attachment(project=other_project, filename="other.pdf")

        response = self.client.post(
            self._chat_url(),
            {"content": "Wrong project", "attachment_ids": [str(other_att.id)]},
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["attachments"] == []

    # --- GET with attachments ---

    def test_list_messages_includes_attachments(self):
        """GET returns messages with their linked attachments."""
        msg = ChatMessage.objects.create(
            project_id=self.project.id,
            sender_type="user",
            sender_id=self.user1.id,
            content="With file",
        )
        self._create_attachment(filename="listed.pdf", message_id=msg.id)

        response = self.client.get(self._chat_url())
        assert response.status_code == 200
        messages = response.json()["messages"]
        assert len(messages) == 1
        assert len(messages[0]["attachments"]) == 1
        assert messages[0]["attachments"][0]["filename"] == "listed.pdf"

    def test_list_messages_excludes_deleted_attachments(self):
        """GET excludes soft-deleted attachments from message attachment list."""
        from django.utils import timezone
        msg = ChatMessage.objects.create(
            project_id=self.project.id,
            sender_type="user",
            sender_id=self.user1.id,
            content="With deleted file",
        )
        self._create_attachment(
            filename="deleted.pdf", message_id=msg.id, deleted_at=timezone.now()
        )

        response = self.client.get(self._chat_url())
        messages = response.json()["messages"]
        assert messages[0]["attachments"] == []

    def test_list_messages_no_attachments(self):
        """GET returns empty attachments for messages without attachments."""
        ChatMessage.objects.create(
            project_id=self.project.id,
            sender_type="user",
            sender_id=self.user1.id,
            content="Plain message",
        )

        response = self.client.get(self._chat_url())
        messages = response.json()["messages"]
        assert messages[0]["attachments"] == []


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestAttachmentImmutability(TestCase):
    """Tests for the immutability rule: cannot delete attachment linked to a message."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = _create_user(USER_1_ID, "user1@test.local", "Test User1")
        self.project = Project.objects.create(owner_id=self.user1.id, title="Test Project")
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.user1.id)},
            format="json",
        )

    def _delete_url(self, attachment_id, project_id=None):
        pid = project_id or self.project.id
        return f"/api/projects/{pid}/attachments/{attachment_id}/"

    def test_delete_linked_attachment_returns_400(self):
        """DELETE on attachment with message_id set returns 400."""
        msg = ChatMessage.objects.create(
            project_id=self.project.id,
            sender_type="user",
            sender_id=self.user1.id,
            content="Message",
        )
        attachment = Attachment.objects.create(
            project=self.project,
            uploader_id=self.user1.id,
            filename="linked.pdf",
            storage_key=f"attachments/{self.project.id}/{uuid.uuid4()}.pdf",
            content_type="application/pdf",
            size_bytes=1024,
            message_id=msg.id,
        )

        response = self.client.delete(self._delete_url(attachment.id))
        assert response.status_code == 400
        data = response.json()
        assert "Cannot delete attachment already sent with message" in data["message"]

    def test_delete_unlinked_attachment_returns_204(self):
        """DELETE on attachment without message_id returns 204."""
        attachment = Attachment.objects.create(
            project=self.project,
            uploader_id=self.user1.id,
            filename="free.pdf",
            storage_key=f"attachments/{self.project.id}/{uuid.uuid4()}.pdf",
            content_type="application/pdf",
            size_bytes=1024,
        )

        with self.settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}):
            from unittest.mock import MagicMock, patch
            with patch("apps.attachments.views._get_storage_backend", return_value=MagicMock()):
                response = self.client.delete(self._delete_url(attachment.id))

        assert response.status_code == 204
