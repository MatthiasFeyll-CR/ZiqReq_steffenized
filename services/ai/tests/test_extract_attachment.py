"""Tests for the extract_attachment_content Celery task (US-006).

Covers: successful PDF extraction, page-level vision fallback trigger,
truncation, mock mode, error handling, missing attachment.
"""

from __future__ import annotations

import io
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_attachment_row(
    attachment_id: str = "aaaaaaaa-1111-2222-3333-444444444444",
    project_id: str = "bbbbbbbb-1111-2222-3333-444444444444",
    filename: str = "test.pdf",
    storage_key: str = "attachments/proj/test.pdf",
    content_type: str = "application/pdf",
    size_bytes: int = 12345,
) -> tuple:
    """Return a DB row tuple matching the SELECT in _get_attachment."""
    return (attachment_id, project_id, filename, storage_key, content_type, size_bytes)


def _create_simple_pdf(pages: list[str] | None = None) -> bytes:
    """Create a simple PDF using PyMuPDF with given page texts."""
    import fitz

    doc = fitz.open()
    for text in (pages or ["Hello world. This is a test document with enough text to pass the 50-char threshold for vision fallback."]):
        page = doc.new_page()
        page.insert_text((72, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def _create_sparse_pdf_with_image() -> bytes:
    """Create a PDF with a page that has < 50 chars of text and an image."""
    import fitz
    from PIL import Image

    doc = fitz.open()
    page = doc.new_page()
    # Insert minimal text (< 50 chars)
    page.insert_text((72, 72), "Hi")

    # Insert a small PNG image to trigger the vision fallback
    img = Image.new("RGB", (10, 10), color="red")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    page.insert_image(fitz.Rect(72, 100, 200, 200), stream=img_bytes)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


# ---------------------------------------------------------------------------
# Tests: _get_attachment
# ---------------------------------------------------------------------------


class TestGetAttachment:
    """Test the _get_attachment helper."""

    @patch("django.db.connection")
    def test_returns_attachment_dict(self, mock_conn: MagicMock) -> None:
        from tasks.extract_attachment import _get_attachment

        row = _make_attachment_row()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = row
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        result = _get_attachment("aaaaaaaa-1111-2222-3333-444444444444")

        assert result is not None
        assert result["id"] == "aaaaaaaa-1111-2222-3333-444444444444"
        assert result["filename"] == "test.pdf"
        assert result["content_type"] == "application/pdf"

    @patch("django.db.connection")
    def test_returns_none_when_not_found(self, mock_conn: MagicMock) -> None:
        from tasks.extract_attachment import _get_attachment

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        result = _get_attachment("nonexistent-id")
        assert result is None


# ---------------------------------------------------------------------------
# Tests: _extract_pdf
# ---------------------------------------------------------------------------


class TestExtractPdf:
    """Test the _extract_pdf function."""

    @patch("tasks.extract_attachment._call_vision")
    def test_extracts_text_from_simple_pdf(self, mock_vision: MagicMock) -> None:
        from tasks.extract_attachment import _extract_pdf

        pdf_bytes = _create_simple_pdf(["This is a test page with enough text to exceed the fifty character threshold for vision."])
        result = _extract_pdf(pdf_bytes, 16000)

        assert "[Page 1]" in result
        assert "test page" in result
        mock_vision.assert_not_called()

    @patch("tasks.extract_attachment._call_vision")
    def test_multi_page_pdf(self, mock_vision: MagicMock) -> None:
        from tasks.extract_attachment import _extract_pdf

        pdf_bytes = _create_simple_pdf([
            "Page one content that is long enough to pass the fifty character threshold easily.",
            "Page two content that is also long enough to pass the fifty character threshold easily.",
        ])
        result = _extract_pdf(pdf_bytes, 16000)

        assert "[Page 1]" in result
        assert "[Page 2]" in result
        assert "Page one" in result
        assert "Page two" in result

    @patch("tasks.extract_attachment._call_vision")
    def test_truncation(self, mock_vision: MagicMock) -> None:
        from tasks.extract_attachment import _extract_pdf

        long_text = "A" * 200  # enough to be > 50 chars
        pdf_bytes = _create_simple_pdf([long_text])
        result = _extract_pdf(pdf_bytes, 50)

        assert "[... truncated]" in result

    @patch("tasks.extract_attachment._call_vision", return_value="Vision: chart showing workflow")
    def test_vision_fallback_for_sparse_page_with_images(self, mock_vision: MagicMock) -> None:
        from tasks.extract_attachment import _extract_pdf

        pdf_bytes = _create_sparse_pdf_with_image()
        result = _extract_pdf(pdf_bytes, 16000)

        mock_vision.assert_called_once()
        assert "Vision: chart showing workflow" in result

    @patch("tasks.extract_attachment._call_vision", side_effect=Exception("API error"))
    def test_vision_fallback_failure_uses_available_text(self, mock_vision: MagicMock) -> None:
        from tasks.extract_attachment import _extract_pdf

        pdf_bytes = _create_sparse_pdf_with_image()
        result = _extract_pdf(pdf_bytes, 16000)

        # Should still return without raising
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Tests: extract_attachment_content task
# ---------------------------------------------------------------------------


class TestExtractAttachmentContentTask:
    """Test the main Celery task."""

    @patch("tasks.extract_attachment._update_attachment")
    @patch("tasks.extract_attachment._get_attachment")
    @patch("tasks.extract_attachment._is_mock_mode", return_value=True)
    def test_mock_mode(self, mock_mode: MagicMock, mock_get: MagicMock, mock_update: MagicMock) -> None:
        from tasks.extract_attachment import extract_attachment_content

        mock_get.return_value = {
            "id": "att-1",
            "project_id": "proj-1",
            "filename": "report.pdf",
            "storage_key": "attachments/proj/report.pdf",
            "content_type": "application/pdf",
            "size_bytes": 54321,
        }

        extract_attachment_content("att-1", "proj-1")

        mock_update.assert_called_once()
        args = mock_update.call_args[0]
        assert args[0] == "att-1"
        assert "[Mock extraction]" in args[1]
        assert "report.pdf" in args[1]
        assert "54321" in args[1]
        assert args[2] == "completed"

    @patch("tasks.extract_attachment._update_attachment")
    @patch("tasks.extract_attachment._get_attachment", return_value=None)
    @patch("tasks.extract_attachment._is_mock_mode", return_value=True)
    def test_mock_mode_missing_attachment(self, mock_mode: MagicMock, mock_get: MagicMock, mock_update: MagicMock) -> None:
        from tasks.extract_attachment import extract_attachment_content

        extract_attachment_content("nonexistent", "proj-1")

        mock_update.assert_not_called()

    @patch("tasks.extract_attachment._update_attachment")
    @patch("tasks.extract_attachment._extract_pdf", return_value="Extracted PDF text")
    @patch("tasks.extract_attachment._download_file", return_value=b"fake pdf bytes")
    @patch("tasks.extract_attachment._get_max_chars", return_value=16000)
    @patch("tasks.extract_attachment._set_extraction_processing")
    @patch("tasks.extract_attachment._get_attachment")
    @patch("tasks.extract_attachment._is_mock_mode", return_value=False)
    def test_successful_pdf_extraction(
        self,
        mock_mode: MagicMock,
        mock_get: MagicMock,
        mock_processing: MagicMock,
        mock_max_chars: MagicMock,
        mock_download: MagicMock,
        mock_extract: MagicMock,
        mock_update: MagicMock,
    ) -> None:
        from tasks.extract_attachment import extract_attachment_content

        mock_get.return_value = {
            "id": "att-1",
            "project_id": "proj-1",
            "filename": "report.pdf",
            "storage_key": "attachments/proj/report.pdf",
            "content_type": "application/pdf",
            "size_bytes": 12345,
        }

        extract_attachment_content("att-1", "proj-1")

        mock_processing.assert_called_once_with("att-1")
        mock_download.assert_called_once_with("attachments/proj/report.pdf")
        mock_extract.assert_called_once_with(b"fake pdf bytes", 16000)
        mock_update.assert_called_once_with("att-1", "Extracted PDF text", "completed")

    @patch("tasks.extract_attachment._update_attachment")
    @patch("tasks.extract_attachment._set_extraction_processing")
    @patch("tasks.extract_attachment._get_attachment")
    @patch("tasks.extract_attachment._is_mock_mode", return_value=False)
    def test_skips_non_pdf(
        self,
        mock_mode: MagicMock,
        mock_get: MagicMock,
        mock_processing: MagicMock,
        mock_update: MagicMock,
    ) -> None:
        from tasks.extract_attachment import extract_attachment_content

        mock_get.return_value = {
            "id": "att-1",
            "project_id": "proj-1",
            "filename": "photo.png",
            "storage_key": "attachments/proj/photo.png",
            "content_type": "image/png",
            "size_bytes": 5000,
        }

        extract_attachment_content("att-1", "proj-1")

        # Should not call update since it's not a PDF
        mock_update.assert_not_called()

    @patch("tasks.extract_attachment._update_attachment")
    @patch("tasks.extract_attachment._download_file", side_effect=Exception("Storage error"))
    @patch("tasks.extract_attachment._get_max_chars", return_value=16000)
    @patch("tasks.extract_attachment._set_extraction_processing")
    @patch("tasks.extract_attachment._get_attachment")
    @patch("tasks.extract_attachment._is_mock_mode", return_value=False)
    def test_error_sets_failed_status(
        self,
        mock_mode: MagicMock,
        mock_get: MagicMock,
        mock_processing: MagicMock,
        mock_max_chars: MagicMock,
        mock_download: MagicMock,
        mock_update: MagicMock,
    ) -> None:
        from tasks.extract_attachment import extract_attachment_content

        mock_get.return_value = {
            "id": "att-1",
            "project_id": "proj-1",
            "filename": "report.pdf",
            "storage_key": "attachments/proj/report.pdf",
            "content_type": "application/pdf",
            "size_bytes": 12345,
        }

        extract_attachment_content("att-1", "proj-1")

        mock_update.assert_called_once_with("att-1", "", "failed")

    @patch("tasks.extract_attachment._update_attachment")
    @patch("tasks.extract_attachment._set_extraction_processing")
    @patch("tasks.extract_attachment._get_attachment", return_value=None)
    @patch("tasks.extract_attachment._is_mock_mode", return_value=False)
    def test_missing_attachment_in_real_mode(
        self,
        mock_mode: MagicMock,
        mock_get: MagicMock,
        mock_processing: MagicMock,
        mock_update: MagicMock,
    ) -> None:
        from tasks.extract_attachment import extract_attachment_content

        extract_attachment_content("nonexistent", "proj-1")

        mock_update.assert_not_called()


# ---------------------------------------------------------------------------
# Tests: _get_max_chars
# ---------------------------------------------------------------------------


class TestGetMaxChars:
    """Test the _get_max_chars helper."""

    @patch("grpc_clients.core_client.CoreClient")
    def test_reads_admin_param(self, mock_client_cls: MagicMock) -> None:
        from tasks.extract_attachment import _get_max_chars

        mock_client = MagicMock()
        mock_client.get_admin_parameter.return_value = {"value": "5000"}
        mock_client_cls.return_value = mock_client

        result = _get_max_chars()
        assert result == 20000  # 5000 tokens * 4 chars

    @patch("grpc_clients.core_client.CoreClient", side_effect=Exception("DB error"))
    def test_falls_back_to_default(self, mock_client_cls: MagicMock) -> None:
        from tasks.extract_attachment import DEFAULT_MAX_CHARS, _get_max_chars

        result = _get_max_chars()
        assert result == DEFAULT_MAX_CHARS
