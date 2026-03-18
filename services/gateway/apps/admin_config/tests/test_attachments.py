"""Tests for admin attachment endpoints: list, delete, restore."""

import uuid
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.projects.models import Attachment, Project

ADMIN_ID = uuid.UUID("00000000-0000-0000-0000-000000000010")
USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000011")


def _create_user(user_id, email, display_name, roles=None):
    return User.objects.create(
        id=user_id,
        email=email,
        first_name=display_name.split()[0],
        last_name=display_name.split()[-1],
        display_name=display_name,
        roles=roles or ["user"],
    )


def _make_attachment(project, **overrides):
    defaults = {
        "project": project,
        "uploader_id": ADMIN_ID,
        "filename": "test.pdf",
        "storage_key": f"attachments/{project.id}/{uuid.uuid4()}.pdf",
        "content_type": "application/pdf",
        "size_bytes": 1024,
    }
    defaults.update(overrides)
    return Attachment.objects.create(**defaults)


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestAdminAttachmentsList(TestCase):
    """Tests for GET /api/admin/attachments."""

    def setUp(self):
        self.client = APIClient()
        self.admin = _create_user(ADMIN_ID, "admin@test.local", "Admin User", ["admin"])
        self.user = _create_user(USER_ID, "user@test.local", "Normal User", ["user"])
        self.project = Project.objects.create(title="Test Project", owner_id=ADMIN_ID)
        self._login_as(self.admin)

    def _login_as(self, user):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    def test_list_returns_all_attachments(self):
        _make_attachment(self.project, filename="file1.pdf")
        _make_attachment(self.project, filename="file2.pdf")
        resp = self.client.get("/api/admin/attachments")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 2
        assert len(data["results"]) == 2

    def test_list_includes_stats(self):
        _make_attachment(self.project, size_bytes=1000)
        _make_attachment(self.project, size_bytes=2000)
        resp = self.client.get("/api/admin/attachments")
        data = resp.json()
        assert data["stats"]["total_count"] == 2
        assert data["stats"]["total_size_bytes"] == 3000

    def test_filter_active(self):
        _make_attachment(self.project, filename="active.pdf")
        deleted = _make_attachment(self.project, filename="deleted.pdf")
        Attachment.objects.filter(id=deleted.id).update(deleted_at=timezone.now())

        resp = self.client.get("/api/admin/attachments?filter=active")
        data = resp.json()
        assert data["count"] == 1
        assert data["results"][0]["filename"] == "active.pdf"

    def test_filter_deleted(self):
        _make_attachment(self.project, filename="active.pdf")
        deleted = _make_attachment(self.project, filename="deleted.pdf")
        Attachment.objects.filter(id=deleted.id).update(deleted_at=timezone.now())

        resp = self.client.get("/api/admin/attachments?filter=deleted")
        data = resp.json()
        assert data["count"] == 1
        assert data["results"][0]["filename"] == "deleted.pdf"

    def test_search_by_filename(self):
        _make_attachment(self.project, filename="report.pdf")
        _make_attachment(self.project, filename="screenshot.png", content_type="image/png")

        resp = self.client.get("/api/admin/attachments?search=report")
        data = resp.json()
        assert data["count"] == 1
        assert data["results"][0]["filename"] == "report.pdf"

    def test_pagination(self):
        for i in range(40):
            _make_attachment(self.project, filename=f"file{i:03d}.pdf")

        resp = self.client.get("/api/admin/attachments?page=1&page_size=35")
        data = resp.json()
        assert data["count"] == 40
        assert len(data["results"]) == 35
        assert data["next"] == 2
        assert data["previous"] is None

        resp2 = self.client.get("/api/admin/attachments?page=2&page_size=35")
        data2 = resp2.json()
        assert len(data2["results"]) == 5
        assert data2["next"] is None
        assert data2["previous"] == 1

    def test_results_include_project_info(self):
        _make_attachment(self.project, filename="test.pdf")
        resp = self.client.get("/api/admin/attachments")
        result = resp.json()["results"][0]
        assert "project" in result
        assert result["project"]["id"] == str(self.project.id)
        assert result["project"]["title"] == "Test Project"

    def test_non_admin_forbidden(self):
        self._login_as(self.user)
        resp = self.client.get("/api/admin/attachments")
        assert resp.status_code == 403

    def test_unauthenticated(self):
        self.client.logout()
        resp = self.client.get("/api/admin/attachments")
        assert resp.status_code == 401


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestAdminAttachmentDelete(TestCase):
    """Tests for DELETE /api/admin/attachments/:id."""

    def setUp(self):
        self.client = APIClient()
        self.admin = _create_user(ADMIN_ID, "admin@test.local", "Admin User", ["admin"])
        self.user = _create_user(USER_ID, "user@test.local", "Normal User", ["user"])
        self.project = Project.objects.create(title="Test Project", owner_id=ADMIN_ID)
        self._login_as(self.admin)

    def _login_as(self, user):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    @patch("apps.admin_config.views.get_storage_backend")
    def test_hard_delete_success(self, mock_backend_factory):
        mock_backend = MagicMock()
        mock_backend_factory.return_value = mock_backend
        att = _make_attachment(self.project)

        resp = self.client.delete(f"/api/admin/attachments/{att.id}")
        assert resp.status_code == 204
        assert not Attachment.objects.filter(id=att.id).exists()
        mock_backend.delete_file.assert_called_once_with(att.storage_key)

    @patch("apps.admin_config.views.get_storage_backend")
    def test_hard_delete_storage_failure_still_deletes_record(self, mock_backend_factory):
        mock_backend = MagicMock()
        mock_backend.delete_file.side_effect = Exception("storage error")
        mock_backend_factory.return_value = mock_backend
        att = _make_attachment(self.project)

        resp = self.client.delete(f"/api/admin/attachments/{att.id}")
        assert resp.status_code == 204
        assert not Attachment.objects.filter(id=att.id).exists()

    def test_delete_not_found(self):
        resp = self.client.delete(f"/api/admin/attachments/{uuid.uuid4()}")
        assert resp.status_code == 404

    def test_delete_invalid_uuid(self):
        resp = self.client.delete("/api/admin/attachments/not-a-uuid")
        assert resp.status_code == 404

    def test_non_admin_forbidden(self):
        self._login_as(self.user)
        att = _make_attachment(self.project)
        resp = self.client.delete(f"/api/admin/attachments/{att.id}")
        assert resp.status_code == 403


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestAdminAttachmentRestore(TestCase):
    """Tests for POST /api/admin/attachments/:id/restore/."""

    def setUp(self):
        self.client = APIClient()
        self.admin = _create_user(ADMIN_ID, "admin@test.local", "Admin User", ["admin"])
        self.user = _create_user(USER_ID, "user@test.local", "Normal User", ["user"])
        self.project = Project.objects.create(title="Test Project", owner_id=ADMIN_ID)
        self._login_as(self.admin)

    def _login_as(self, user):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    @patch("apps.admin_config.views.get_storage_backend")
    def test_restore_success(self, mock_backend_factory):
        mock_backend = MagicMock()
        mock_backend.file_exists.return_value = True
        mock_backend_factory.return_value = mock_backend

        att = _make_attachment(self.project)
        Attachment.objects.filter(id=att.id).update(deleted_at=timezone.now())

        resp = self.client.post(f"/api/admin/attachments/{att.id}/restore/")
        assert resp.status_code == 200
        att.refresh_from_db()
        assert att.deleted_at is None

    def test_restore_not_found_active_attachment(self):
        att = _make_attachment(self.project)
        resp = self.client.post(f"/api/admin/attachments/{att.id}/restore/")
        assert resp.status_code == 404

    @patch("apps.admin_config.views.get_storage_backend")
    def test_restore_fails_when_project_deleted(self, mock_backend_factory):
        mock_backend = MagicMock()
        mock_backend.file_exists.return_value = True
        mock_backend_factory.return_value = mock_backend

        att = _make_attachment(self.project)
        Attachment.objects.filter(id=att.id).update(deleted_at=timezone.now())
        Project.objects.filter(id=self.project.id).update(deleted_at=timezone.now())

        resp = self.client.post(f"/api/admin/attachments/{att.id}/restore/")
        assert resp.status_code == 400
        assert resp.json()["error"] == "PROJECT_DELETED"

    @patch("apps.admin_config.views.get_storage_backend")
    def test_restore_fails_when_file_gone(self, mock_backend_factory):
        mock_backend = MagicMock()
        mock_backend.file_exists.return_value = False
        mock_backend_factory.return_value = mock_backend

        att = _make_attachment(self.project)
        Attachment.objects.filter(id=att.id).update(deleted_at=timezone.now())

        resp = self.client.post(f"/api/admin/attachments/{att.id}/restore/")
        assert resp.status_code == 410
        assert resp.json()["error"] == "FILE_GONE"

    def test_non_admin_forbidden(self):
        self._login_as(self.user)
        att = _make_attachment(self.project)
        Attachment.objects.filter(id=att.id).update(deleted_at=timezone.now())
        resp = self.client.post(f"/api/admin/attachments/{att.id}/restore/")
        assert resp.status_code == 403
