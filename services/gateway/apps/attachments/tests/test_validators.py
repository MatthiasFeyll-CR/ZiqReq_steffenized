import uuid
from io import BytesIO
from unittest.mock import MagicMock, patch

from django.core.cache import cache
from django.test import TestCase, override_settings
from PIL import Image
from rest_framework.test import APIClient

from apps.attachments.validators import (
    FileValidationError,
    sanitize_filename,
    sanitize_image,
    sanitize_pdf,
    validate_magic_bytes,
)
from apps.authentication.models import User
from apps.projects.models import Project

USER_1_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


def _create_user(user_id, email, display_name):
    return User.objects.create(
        id=user_id,
        email=email,
        first_name=display_name.split()[0],
        last_name=display_name.split()[-1],
        display_name=display_name,
        roles=["user"],
    )


def _make_real_png() -> bytes:
    """Create a valid PNG file using Pillow."""
    img = Image.new("RGB", (10, 10), color="red")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def _make_real_jpeg() -> bytes:
    """Create a valid JPEG file using Pillow."""
    img = Image.new("RGB", (10, 10), color="blue")
    buf = BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf.read()



def _make_real_webp() -> bytes:
    """Create a valid WebP file using Pillow."""
    img = Image.new("RGB", (10, 10), color="green")
    buf = BytesIO()
    img.save(buf, format="WEBP")
    buf.seek(0)
    return buf.read()


def _make_minimal_pdf() -> bytes:
    """Create a minimal valid PDF."""
    return (
        b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
        b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n"
        b"0000000058 00000 n \n0000000115 00000 n \n"
        b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF"
    )


class TestValidateMagicBytes(TestCase):
    """Tests for validate_magic_bytes()."""

    def test_valid_png(self):
        data = _make_real_png()
        validate_magic_bytes(data, "image/png")  # Should not raise

    def test_valid_jpeg(self):
        data = _make_real_jpeg()
        validate_magic_bytes(data, "image/jpeg")  # Should not raise

    def test_valid_webp(self):
        data = _make_real_webp()
        validate_magic_bytes(data, "image/webp")  # Should not raise

    def test_valid_pdf(self):
        data = _make_minimal_pdf()
        validate_magic_bytes(data, "application/pdf")  # Should not raise

    def test_spoofed_mime_exe_as_pdf(self):
        """EXE file with PDF content type should be rejected."""
        exe_data = b"MZ\x00\x00" + b"\x00" * 100
        with self.assertRaises(FileValidationError):
            validate_magic_bytes(exe_data, "application/pdf")

    def test_spoofed_mime_png_as_jpeg(self):
        """PNG file declared as JPEG should be rejected."""
        png_data = _make_real_png()
        with self.assertRaises(FileValidationError):
            validate_magic_bytes(png_data, "image/jpeg")

    def test_spoofed_mime_pdf_as_png(self):
        """PDF declared as PNG should be rejected."""
        pdf_data = _make_minimal_pdf()
        with self.assertRaises(FileValidationError):
            validate_magic_bytes(pdf_data, "image/png")

    def test_spoofed_mime_random_as_webp(self):
        """Random bytes declared as WebP should be rejected."""
        random_data = b"\x00\x01\x02\x03" * 10
        with self.assertRaises(FileValidationError):
            validate_magic_bytes(random_data, "image/webp")

    def test_file_too_small(self):
        with self.assertRaises(FileValidationError):
            validate_magic_bytes(b"\x89P", "image/png")

    def test_unsupported_content_type(self):
        with self.assertRaises(FileValidationError):
            validate_magic_bytes(b"\x00" * 20, "application/octet-stream")


class TestSanitizeImage(TestCase):
    """Tests for sanitize_image()."""

    def test_png_sanitized(self):
        data = _make_real_png()
        result = sanitize_image(data)
        # Result should be valid PNG
        img = Image.open(BytesIO(result))
        assert img.format == "PNG"

    def test_jpeg_sanitized(self):
        data = _make_real_jpeg()
        result = sanitize_image(data)
        img = Image.open(BytesIO(result))
        assert img.format == "JPEG"

    def test_webp_sanitized(self):
        data = _make_real_webp()
        result = sanitize_image(data)
        img = Image.open(BytesIO(result))
        assert img.format == "WEBP"

    def test_exif_stripped_from_jpeg(self):
        """JPEG with EXIF data should have metadata stripped."""
        data = _make_real_jpeg()
        result = sanitize_image(data)
        img = Image.open(BytesIO(result))
        # info should be cleared
        assert not img.info.get("exif", b"")

    def test_invalid_image_data(self):
        with self.assertRaises(FileValidationError):
            sanitize_image(b"not an image at all")


class TestSanitizePdf(TestCase):
    """Tests for sanitize_pdf()."""

    def test_clean_pdf_passes(self):
        data = _make_minimal_pdf()
        result = sanitize_pdf(data)
        assert result == data

    def test_pdf_with_javascript_action_rejected(self):
        """PDF containing /JavaScript action should be rejected."""
        # Build a PDF string with /JavaScript embedded in xref objects
        pdf_with_js = (
            b"%PDF-1.4\n"
            b"1 0 obj<</Type/Catalog/Pages 2 0 R/OpenAction 4 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
            b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
            b"4 0 obj<</S/JavaScript/JS(app.alert('XSS'))>>endobj\n"
            b"xref\n0 5\n"
            b"0000000000 65535 f \n"
            b"0000000009 00000 n \n"
            b"0000000068 00000 n \n"
            b"0000000125 00000 n \n"
            b"0000000196 00000 n \n"
            b"trailer<</Size 5/Root 1 0 R>>\n"
            b"startxref\n254\n%%EOF"
        )
        with self.assertRaises(FileValidationError) as ctx:
            sanitize_pdf(pdf_with_js)
        assert "dangerous action" in str(ctx.exception).lower() or "JavaScript" in str(ctx.exception)

    def test_invalid_pdf_rejected(self):
        """Invalid PDF data should raise FileValidationError."""
        with self.assertRaises(FileValidationError):
            sanitize_pdf(b"not a pdf file")

    def test_missing_pymupdf_returns_data(self):
        """If PyMuPDF import fails, sanitize_pdf returns data unchanged."""
        import builtins

        data = _make_minimal_pdf()
        real_import = builtins.__import__

        def fail_fitz(name, *args, **kwargs):
            if name == "fitz":
                raise ImportError("No module named 'fitz'")
            return real_import(name, *args, **kwargs)

        with patch.object(builtins, "__import__", side_effect=fail_fitz):
            result = sanitize_pdf(data)
        assert result == data


class TestSanitizeFilename(TestCase):
    """Tests for sanitize_filename()."""

    def test_normal_filename(self):
        assert sanitize_filename("report.pdf") == "report.pdf"

    def test_path_traversal(self):
        result = sanitize_filename("../../../etc/passwd.pdf")
        assert "/" not in result
        assert ".." not in result

    def test_windows_path(self):
        result = sanitize_filename("C:\\Users\\evil\\file.pdf")
        assert "\\" not in result
        assert result == "file.pdf"

    def test_special_characters(self):
        result = sanitize_filename("my file (1) [final].pdf")
        assert result == "my_file_1_final_.pdf"

    def test_consecutive_underscores(self):
        result = sanitize_filename("a___b.pdf")
        assert result == "a_b.pdf"

    def test_truncate_long_name(self):
        long_name = "a" * 300 + ".pdf"
        result = sanitize_filename(long_name)
        assert len(result) <= 255

    def test_empty_name(self):
        result = sanitize_filename("")
        assert result == ""


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestUploadValidationIntegration(TestCase):
    """Integration tests: upload endpoint with security validation."""

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = _create_user(USER_1_ID, "user1@test.local", "Test User1")
        self.project = Project.objects.create(title="Test Project", owner_id=USER_1_ID)
        self.client.post("/api/auth/dev-login", {"user_id": str(self.user.id)}, format="json")

    def tearDown(self):
        cache.clear()

    def _upload(self, name, content, content_type):
        from django.core.files.uploadedfile import SimpleUploadedFile

        f = SimpleUploadedFile(name, content, content_type=content_type)
        with patch("apps.attachments.views._get_storage_backend") as mock_backend:
            mock_backend.return_value = MagicMock()
            return self.client.post(
                f"/api/projects/{self.project.id}/attachments/",
                {"file": f},
                format="multipart",
            )

    def test_spoofed_mime_rejected(self):
        """File with mismatched magic bytes and MIME type is rejected."""
        exe_data = b"MZ\x00\x00" + b"\x00" * 100
        resp = self._upload("file.pdf", exe_data, "application/pdf")
        assert resp.status_code == 400
        assert "validation failed" in resp.json()["message"].lower()

    def test_valid_png_upload_succeeds(self):
        data = _make_real_png()
        resp = self._upload("test.png", data, "image/png")
        assert resp.status_code == 201

    def test_valid_jpeg_upload_succeeds(self):
        data = _make_real_jpeg()
        resp = self._upload("test.jpg", data, "image/jpeg")
        assert resp.status_code == 201

    def test_valid_webp_upload_succeeds(self):
        data = _make_real_webp()
        resp = self._upload("test.webp", data, "image/webp")
        assert resp.status_code == 201

    def test_valid_pdf_upload_succeeds(self):
        data = _make_minimal_pdf()
        resp = self._upload("test.pdf", data, "application/pdf")
        assert resp.status_code == 201

    def test_image_exif_stripped_on_upload(self):
        """Uploaded images should have EXIF stripped (sanitized bytes stored)."""
        data = _make_real_png()
        with patch("apps.attachments.views._get_storage_backend") as mock_backend:
            mock_storage = MagicMock()
            mock_backend.return_value = mock_storage
            f = BytesIO(data)
            f.name = "test.png"
            resp = self.client.post(
                f"/api/projects/{self.project.id}/attachments/",
                {"file": f},
                format="multipart",
            )
        assert resp.status_code == 201
        # Storage was called with sanitized data
        mock_storage.upload_file.assert_called_once()
        stored_data = mock_storage.upload_file.call_args[0][1]
        # Verify it's still valid PNG
        img = Image.open(BytesIO(stored_data))
        assert img.format == "PNG"

    def test_rate_limit_exceeded(self):
        cache.set(f"upload_rate:{self.user.id}", 10, timeout=60)
        data = _make_real_png()
        resp = self._upload("test.png", data, "image/png")
        assert resp.status_code == 429
