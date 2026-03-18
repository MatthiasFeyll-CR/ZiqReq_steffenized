import uuid
from io import BytesIO
from unittest.mock import MagicMock, patch

from django.core.cache import cache
from django.test import TestCase, override_settings
from PIL import Image
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.projects.models import Attachment, Project, ProjectCollaborator

USER_1_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
USER_2_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
USER_3_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")


def _create_user(user_id: uuid.UUID, email: str, display_name: str) -> "User":
    return User.objects.create(
        id=user_id,
        email=email,
        first_name=display_name.split()[0],
        last_name=display_name.split()[-1],
        display_name=display_name,
        roles=["user"],
    )


def _fake_pdf_bytes() -> bytes:
    return (
        b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
        b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n"
        b"0000000058 00000 n \n0000000115 00000 n \n"
        b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF"
    )


def _fake_png_bytes() -> bytes:
    img = Image.new("RGB", (2, 2), color="red")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def _fake_jpeg_bytes() -> bytes:
    img = Image.new("RGB", (2, 2), color="blue")
    buf = BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf.read()


def _fake_webp_bytes() -> bytes:
    img = Image.new("RGB", (2, 2), color="green")
    buf = BytesIO()
    img.save(buf, format="WEBP")
    buf.seek(0)
    return buf.read()


def _make_upload_file(name="test.pdf", content=None, content_type="application/pdf"):
    if content is None:
        content = _fake_pdf_bytes()
    f = BytesIO(content)
    f.name = name
    f.content_type = content_type
    return f


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestAttachmentUpload(TestCase):
    """Tests for POST /api/projects/:id/attachments/"""

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user1 = _create_user(USER_1_ID, "user1@test.local", "Test User1")
        self.user2 = _create_user(USER_2_ID, "user2@test.local", "Test User2")
        self.project = Project.objects.create(title="Test Project", owner_id=USER_1_ID)
        ProjectCollaborator.objects.create(project=self.project, user_id=USER_2_ID)
        self._login_as(self.user1)

    def tearDown(self):
        cache.clear()

    def _login_as(self, user):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    def _upload(self, project_id=None, name="test.pdf", content=None, content_type="application/pdf"):
        if project_id is None:
            project_id = self.project.id
        f = _make_upload_file(name=name, content=content, content_type=content_type)
        with patch("apps.attachments.views._get_storage_backend") as mock_backend:
            mock_backend.return_value = MagicMock()
            response = self.client.post(
                f"/api/projects/{project_id}/attachments/",
                {"file": f},
                format="multipart",
            )
        return response

    # --- Happy path ---

    def test_upload_pdf_success(self):
        resp = self._upload()
        assert resp.status_code == 201
        data = resp.json()
        assert data["filename"] == "test.pdf"
        assert data["content_type"] == "application/pdf"
        assert data["extraction_status"] == "pending"
        assert "id" in data
        assert "created_at" in data

    def test_upload_png_success(self):
        resp = self._upload(name="image.png", content=_fake_png_bytes(), content_type="image/png")
        assert resp.status_code == 201
        assert resp.json()["content_type"] == "image/png"

    def test_upload_jpeg_success(self):
        resp = self._upload(name="photo.jpg", content=_fake_jpeg_bytes(), content_type="image/jpeg")
        assert resp.status_code == 201

    def test_upload_webp_success(self):
        resp = self._upload(name="img.webp", content=_fake_webp_bytes(), content_type="image/webp")
        assert resp.status_code == 201

    def test_upload_creates_attachment_record(self):
        self._upload()
        assert Attachment.objects.filter(project=self.project).count() == 1
        att = Attachment.objects.get(project=self.project)
        assert att.uploader_id == self.user1.id
        assert att.filename == "test.pdf"
        assert att.extraction_status == "pending"
        assert att.deleted_at is None
        assert att.message_id is None

    def test_upload_storage_key_format(self):
        self._upload()
        att = Attachment.objects.get(project=self.project)
        assert att.storage_key.startswith(f"attachments/{self.project.id}/")
        assert att.storage_key.endswith(".pdf")

    def test_collaborator_can_upload(self):
        self._login_as(self.user2)
        resp = self._upload()
        assert resp.status_code == 201

    # --- Auth ---

    def test_upload_unauthenticated(self):
        self.client.logout()
        f = _make_upload_file()
        resp = self.client.post(
            f"/api/projects/{self.project.id}/attachments/",
            {"file": f},
            format="multipart",
        )
        assert resp.status_code == 401

    def test_upload_non_collaborator(self):
        user3 = _create_user(USER_3_ID, "user3@test.local", "Test User3")
        self._login_as(user3)
        resp = self._upload()
        assert resp.status_code == 403

    # --- Validation ---

    def test_upload_invalid_content_type(self):
        resp = self._upload(name="file.exe", content=b"MZ" + b"\x00" * 100, content_type="application/octet-stream")
        assert resp.status_code == 400
        assert "not allowed" in resp.json()["message"]

    def test_upload_no_file(self):
        with patch("apps.attachments.views._get_storage_backend") as mock_backend:
            mock_backend.return_value = MagicMock()
            resp = self.client.post(
                f"/api/projects/{self.project.id}/attachments/",
                {},
                format="multipart",
            )
        assert resp.status_code == 400
        assert "No file" in resp.json()["message"]

    def test_upload_file_too_large(self):
        # Create a file object that reports a large size
        f = _make_upload_file()
        with patch("apps.attachments.views._get_storage_backend") as mock_backend:
            mock_backend.return_value = MagicMock()
            # Monkey-patch file size
            with patch("apps.attachments.views.MAX_FILE_SIZE", 10):
                resp = self.client.post(
                    f"/api/projects/{self.project.id}/attachments/",
                    {"file": f},
                    format="multipart",
                )
        assert resp.status_code == 400
        assert "100MB" in resp.json()["message"]

    def test_upload_exceeds_project_limit(self):
        # Create 10 existing attachments
        for i in range(10):
            Attachment.objects.create(
                project=self.project,
                uploader_id=self.user1.id,
                filename=f"file{i}.pdf",
                storage_key=f"attachments/{self.project.id}/{uuid.uuid4()}.pdf",
                content_type="application/pdf",
                size_bytes=1024,
            )
        resp = self._upload()
        assert resp.status_code == 400
        assert "maximum" in resp.json()["message"]

    def test_upload_project_not_found(self):
        resp = self._upload(project_id=uuid.uuid4())
        assert resp.status_code == 404

    # --- Rate limiting ---

    def test_upload_rate_limit(self):
        # Set cache to max
        cache.set(f"upload_rate:{self.user1.id}", 10, timeout=60)
        resp = self._upload()
        assert resp.status_code == 429

    # --- Filename sanitization ---

    def test_filename_sanitized(self):
        resp = self._upload(name="../../../etc/passwd.pdf")
        assert resp.status_code == 201
        att = Attachment.objects.get(project=self.project)
        assert "/" not in att.filename
        assert "\\" not in att.filename
        assert ".." not in att.filename


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestAttachmentList(TestCase):
    """Tests for GET /api/projects/:id/attachments/"""

    def setUp(self):
        self.client = APIClient()
        self.user1 = _create_user(USER_1_ID, "user1@test.local", "Test User1")
        self.project = Project.objects.create(title="Test Project", owner_id=USER_1_ID)
        self._login_as(self.user1)

    def _login_as(self, user):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    def _make_attachment(self, **overrides):
        defaults = {
            "project": self.project,
            "uploader_id": self.user1.id,
            "filename": "test.pdf",
            "storage_key": f"attachments/{self.project.id}/{uuid.uuid4()}.pdf",
            "content_type": "application/pdf",
            "size_bytes": 1024,
        }
        defaults.update(overrides)
        return Attachment.objects.create(**defaults)

    def test_list_empty(self):
        resp = self.client.get(f"/api/projects/{self.project.id}/attachments/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_returns_active_attachments(self):
        self._make_attachment(filename="file1.pdf")
        self._make_attachment(filename="file2.pdf")
        resp = self.client.get(f"/api/projects/{self.project.id}/attachments/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2

    def test_list_excludes_soft_deleted(self):
        self._make_attachment(filename="active.pdf")
        from django.utils import timezone
        deleted = self._make_attachment(filename="deleted.pdf")
        deleted.deleted_at = timezone.now()
        deleted.save()
        resp = self.client.get(f"/api/projects/{self.project.id}/attachments/")
        assert len(resp.json()) == 1
        assert resp.json()[0]["filename"] == "active.pdf"

    def test_list_ordered_by_created_at_desc(self):
        self._make_attachment(filename="first.pdf")
        self._make_attachment(filename="second.pdf")
        resp = self.client.get(f"/api/projects/{self.project.id}/attachments/")
        data = resp.json()
        assert data[0]["filename"] == "second.pdf"
        assert data[1]["filename"] == "first.pdf"

    def test_list_unauthenticated(self):
        self.client.logout()
        resp = self.client.get(f"/api/projects/{self.project.id}/attachments/")
        assert resp.status_code == 401

    def test_list_non_collaborator(self):
        user3 = _create_user(USER_3_ID, "user3@test.local", "Test User3")
        self._login_as(user3)
        resp = self.client.get(f"/api/projects/{self.project.id}/attachments/")
        assert resp.status_code == 403

    def test_list_response_fields(self):
        self._make_attachment()
        resp = self.client.get(f"/api/projects/{self.project.id}/attachments/")
        data = resp.json()[0]
        assert "id" in data
        assert "filename" in data
        assert "content_type" in data
        assert "size_bytes" in data
        assert "extraction_status" in data
        assert "created_at" in data
        assert "message_id" in data


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestAttachmentDelete(TestCase):
    """Tests for DELETE /api/projects/:id/attachments/:aid/"""

    def setUp(self):
        self.client = APIClient()
        self.user1 = _create_user(USER_1_ID, "user1@test.local", "Test User1")
        self.user2 = _create_user(USER_2_ID, "user2@test.local", "Test User2")
        self.project = Project.objects.create(title="Test Project", owner_id=USER_1_ID)
        ProjectCollaborator.objects.create(project=self.project, user_id=USER_2_ID)
        self._login_as(self.user1)

    def _login_as(self, user):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    def _make_attachment(self, uploader_id=None, **overrides):
        defaults = {
            "project": self.project,
            "uploader_id": uploader_id or self.user1.id,
            "filename": "test.pdf",
            "storage_key": f"attachments/{self.project.id}/{uuid.uuid4()}.pdf",
            "content_type": "application/pdf",
            "size_bytes": 1024,
        }
        defaults.update(overrides)
        return Attachment.objects.create(**defaults)

    @patch("apps.attachments.views._get_storage_backend")
    def test_delete_by_uploader(self, mock_backend):
        mock_backend.return_value = MagicMock()
        att = self._make_attachment()
        resp = self.client.delete(f"/api/projects/{self.project.id}/attachments/{att.id}/")
        assert resp.status_code == 204
        att.refresh_from_db()
        assert att.deleted_at is not None

    @patch("apps.attachments.views._get_storage_backend")
    def test_delete_by_project_owner(self, mock_backend):
        mock_backend.return_value = MagicMock()
        att = self._make_attachment(uploader_id=USER_2_ID)
        resp = self.client.delete(f"/api/projects/{self.project.id}/attachments/{att.id}/")
        assert resp.status_code == 204

    @patch("apps.attachments.views._get_storage_backend")
    def test_delete_by_non_owner_non_uploader(self, mock_backend):
        mock_backend.return_value = MagicMock()
        att = self._make_attachment(uploader_id=USER_1_ID)
        self._login_as(self.user2)
        resp = self.client.delete(f"/api/projects/{self.project.id}/attachments/{att.id}/")
        assert resp.status_code == 403

    def test_delete_not_found(self):
        resp = self.client.delete(f"/api/projects/{self.project.id}/attachments/{uuid.uuid4()}/")
        assert resp.status_code == 404

    def test_delete_already_deleted(self):
        from django.utils import timezone
        att = self._make_attachment()
        att.deleted_at = timezone.now()
        att.save()
        resp = self.client.delete(f"/api/projects/{self.project.id}/attachments/{att.id}/")
        assert resp.status_code == 404

    def test_delete_unauthenticated(self):
        att = self._make_attachment()
        self.client.logout()
        resp = self.client.delete(f"/api/projects/{self.project.id}/attachments/{att.id}/")
        assert resp.status_code == 401

    @patch("apps.attachments.views._get_storage_backend")
    def test_delete_calls_storage_delete(self, mock_backend):
        mock_storage = MagicMock()
        mock_backend.return_value = mock_storage
        att = self._make_attachment()
        self.client.delete(f"/api/projects/{self.project.id}/attachments/{att.id}/")
        mock_storage.delete_file.assert_called_once_with(att.storage_key)

    @patch("apps.attachments.views._get_storage_backend")
    def test_delete_storage_failure_still_soft_deletes(self, mock_backend):
        mock_storage = MagicMock()
        mock_storage.delete_file.side_effect = Exception("storage error")
        mock_backend.return_value = mock_storage
        att = self._make_attachment()
        resp = self.client.delete(f"/api/projects/{self.project.id}/attachments/{att.id}/")
        assert resp.status_code == 204
        att.refresh_from_db()
        assert att.deleted_at is not None


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestAttachmentPresignedUrl(TestCase):
    """Tests for GET /api/projects/:id/attachments/:aid/url/"""

    def setUp(self):
        self.client = APIClient()
        self.user1 = _create_user(USER_1_ID, "user1@test.local", "Test User1")
        self.project = Project.objects.create(title="Test Project", owner_id=USER_1_ID)
        self._login_as(self.user1)

    def _login_as(self, user):
        self.client.post("/api/auth/dev-login", {"user_id": str(user.id)}, format="json")

    def _make_attachment(self, **overrides):
        defaults = {
            "project": self.project,
            "uploader_id": self.user1.id,
            "filename": "test.pdf",
            "storage_key": f"attachments/{self.project.id}/{uuid.uuid4()}.pdf",
            "content_type": "application/pdf",
            "size_bytes": 1024,
        }
        defaults.update(overrides)
        return Attachment.objects.create(**defaults)

    @patch("apps.attachments.views._get_storage_backend")
    def test_get_presigned_url_success(self, mock_backend):
        mock_storage = MagicMock()
        mock_storage.get_presigned_url.return_value = "https://minio.local/presigned-url"
        mock_backend.return_value = mock_storage
        att = self._make_attachment()
        resp = self.client.get(f"/api/projects/{self.project.id}/attachments/{att.id}/url/")
        assert resp.status_code == 200
        assert resp.json()["url"] == "https://minio.local/presigned-url"

    @patch("apps.attachments.views._get_storage_backend")
    def test_presigned_url_passes_filename(self, mock_backend):
        mock_storage = MagicMock()
        mock_storage.get_presigned_url.return_value = "https://minio.local/url"
        mock_backend.return_value = mock_storage
        att = self._make_attachment(filename="report.pdf")
        self.client.get(f"/api/projects/{self.project.id}/attachments/{att.id}/url/")
        mock_storage.get_presigned_url.assert_called_once_with(
            att.storage_key, expires_seconds=900, filename="report.pdf"
        )

    def test_presigned_url_unauthenticated(self):
        att = self._make_attachment()
        self.client.logout()
        resp = self.client.get(f"/api/projects/{self.project.id}/attachments/{att.id}/url/")
        assert resp.status_code == 401

    def test_presigned_url_non_collaborator(self):
        user3 = _create_user(USER_3_ID, "user3@test.local", "Test User3")
        self._login_as(user3)
        att = self._make_attachment()
        resp = self.client.get(f"/api/projects/{self.project.id}/attachments/{att.id}/url/")
        assert resp.status_code == 403

    def test_presigned_url_not_found(self):
        resp = self.client.get(f"/api/projects/{self.project.id}/attachments/{uuid.uuid4()}/url/")
        assert resp.status_code == 404

    def test_presigned_url_deleted_attachment(self):
        from django.utils import timezone
        att = self._make_attachment()
        att.deleted_at = timezone.now()
        att.save()
        resp = self.client.get(f"/api/projects/{self.project.id}/attachments/{att.id}/url/")
        assert resp.status_code == 404

    @patch("apps.attachments.views._get_storage_backend")
    def test_presigned_url_storage_error(self, mock_backend):
        mock_storage = MagicMock()
        mock_storage.get_presigned_url.side_effect = Exception("storage error")
        mock_backend.return_value = mock_storage
        att = self._make_attachment()
        resp = self.client.get(f"/api/projects/{self.project.id}/attachments/{att.id}/url/")
        assert resp.status_code == 500
