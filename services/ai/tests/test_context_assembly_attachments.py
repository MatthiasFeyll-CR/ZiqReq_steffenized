"""Tests for US-008: AI context integration — attachments in context assembly,
prompt sandboxing, and context extension search.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from agents.context_extension.prompt import _format_attachments
from agents.context_extension.prompt import build_system_prompt as build_extension_prompt
from agents.facilitator.agent import _build_prompt_context, _format_messages
from agents.facilitator.prompt import (
    _render_attachment_guidance_block,
    _render_attachments_block,
    build_system_prompt,
)
from processing.context_assembler import ContextAssembler

# ── Fixtures ──


def _make_attachment(
    att_id: str = "att-001",
    filename: str = "requirements.pdf",
    content_type: str = "application/pdf",
    size_bytes: int = 12345,
    extracted_content: str = "This document describes the project requirements.",
    extraction_status: str = "completed",
    message_id: str | None = "msg-001",
) -> dict:
    return {
        "id": att_id,
        "filename": filename,
        "content_type": content_type,
        "size_bytes": size_bytes,
        "extracted_content": extracted_content,
        "extraction_status": extraction_status,
        "message_id": message_id,
    }


def _make_message(
    msg_id: str = "msg-001",
    sender_type: str = "user",
    content: str = "Please check the uploaded PDF.",
    attachments: list | None = None,
) -> dict:
    return {
        "id": msg_id,
        "sender_type": sender_type,
        "sender_name": "User",
        "content": content,
        "created_at": "2026-03-18T10:00:00Z",
        "attachments": attachments or [],
    }


def _make_project_context_response(
    recent_messages: list | None = None,
) -> dict:
    return {
        "project": {
            "id": "proj-001",
            "title": "Test Project",
            "state": "open",
            "project_type": "software",
        },
        "recent_messages": recent_messages or [],
        "chat_summary": None,
        "requirements_state": {},
    }


# ── ContextAssembler tests ──


class TestContextAssemblerAttachments:
    """Test that ContextAssembler.assemble() includes attachments."""

    @patch("processing.context_assembler._load_project_attachments")
    def test_assemble_includes_attachments(self, mock_load):
        """Assembled context should include 'attachments' key with loaded attachments."""
        attachments = [_make_attachment(), _make_attachment(att_id="att-002", filename="diagram.png")]
        mock_load.return_value = attachments

        assembler = ContextAssembler()
        result = assembler.assemble("proj-001", _make_project_context_response())

        assert "attachments" in result
        assert len(result["attachments"]) == 2
        assert result["attachments"][0]["filename"] == "requirements.pdf"
        mock_load.assert_called_once_with("proj-001")

    @patch("processing.context_assembler._load_project_attachments")
    def test_assemble_empty_attachments(self, mock_load):
        """Assembled context should have empty attachments list when none exist."""
        mock_load.return_value = []

        assembler = ContextAssembler()
        result = assembler.assemble("proj-001", _make_project_context_response())

        assert result["attachments"] == []

    @patch("processing.context_assembler._load_project_attachments")
    def test_assemble_attachment_load_failure(self, mock_load):
        """Assembled context should have empty attachments on load failure."""
        mock_load.return_value = []

        assembler = ContextAssembler()
        result = assembler.assemble("proj-001", _make_project_context_response())
        assert result["attachments"] == []


# ── Prompt rendering tests ──


class TestAttachmentsBlock:
    """Test the attachments block rendering with sandboxing tags."""

    def test_render_attachments_block_with_attachments(self):
        attachments = [_make_attachment()]
        result = _render_attachments_block(attachments)

        assert "<attachments_block>" in result
        assert "</attachments_block>" in result
        assert '<user_attachment id="att-001"' in result
        assert 'filename="requirements.pdf"' in result
        assert 'WARNING="Content extracted from user-uploaded file' in result
        assert "<extracted_content>" in result
        assert "This document describes the project requirements." in result

    def test_render_attachments_block_empty(self):
        result = _render_attachments_block([])
        assert result == ""

    @patch("agents.facilitator.prompt._get_max_content_chars", return_value=20)
    def test_render_attachments_block_truncation(self, _mock):
        """Extracted content should be truncated to max chars."""
        att = _make_attachment(extracted_content="A" * 100)
        result = _render_attachments_block([att])

        # Should contain exactly 20 A's, not 100
        assert "A" * 20 in result
        assert "A" * 21 not in result

    def test_render_attachments_block_multiple(self):
        attachments = [
            _make_attachment(att_id="att-001", filename="doc1.pdf"),
            _make_attachment(att_id="att-002", filename="diagram.png"),
        ]
        result = _render_attachments_block(attachments)
        assert 'filename="doc1.pdf"' in result
        assert 'filename="diagram.png"' in result

    def test_render_attachment_guidance_with_attachments(self):
        result = _render_attachment_guidance_block([_make_attachment()])
        assert "<attachment_guidance>" in result
        assert "reference it by filename" in result

    def test_render_attachment_guidance_empty(self):
        result = _render_attachment_guidance_block([])
        assert result == ""


class TestBuildSystemPromptWithAttachments:
    """Test that build_system_prompt integrates attachments."""

    @patch("agents.facilitator.prompt._get_max_content_chars", return_value=16000)
    def test_prompt_includes_attachments_block(self, _mock):
        context = {
            "project_title": "Test",
            "project_state": "open",
            "project_type": "software",
            "title_manually_edited": False,
            "facilitator_bucket_content": "",
            "recent_messages_formatted": "(no messages yet)",
            "chat_summary": None,
            "delegation_results": None,
            "extension_results": None,
            "is_multi_user": False,
            "user_names_list": "",
            "creator_language": "English",
            "no_messages_yet": True,
            "requirements_structure": None,
            "attachments": [_make_attachment()],
        }
        prompt = build_system_prompt(context)
        assert "<attachments_block>" in prompt
        assert "<user_attachment" in prompt
        assert "<attachment_guidance>" in prompt

    @patch("agents.facilitator.prompt._get_max_content_chars", return_value=16000)
    def test_prompt_no_attachments(self, _mock):
        context = {
            "project_title": "Test",
            "project_state": "open",
            "project_type": "software",
            "title_manually_edited": False,
            "facilitator_bucket_content": "",
            "recent_messages_formatted": "(no messages yet)",
            "chat_summary": None,
            "delegation_results": None,
            "extension_results": None,
            "is_multi_user": False,
            "user_names_list": "",
            "creator_language": "English",
            "no_messages_yet": True,
            "requirements_structure": None,
            "attachments": [],
        }
        prompt = build_system_prompt(context)
        assert "<attachments_block>" not in prompt
        assert "<attachment_guidance>" not in prompt


# ── _format_messages tests ──


class TestFormatMessagesWithAttachments:
    """Test that _format_messages appends attachment filenames."""

    def test_message_with_attachments(self):
        msg = _make_message(
            attachments=[
                {"filename": "doc.pdf"},
                {"filename": "diagram.png"},
            ]
        )
        result = _format_messages([msg])
        assert "[Attachments: doc.pdf, diagram.png]" in result

    def test_message_without_attachments(self):
        msg = _make_message(attachments=[])
        result = _format_messages([msg])
        assert "[Attachments:" not in result

    def test_empty_messages(self):
        result = _format_messages([])
        assert result == "(no messages yet)"


# ── _build_prompt_context tests ──


class TestBuildPromptContextAttachments:
    """Test that _build_prompt_context passes attachments through."""

    def test_passes_attachments(self):
        attachments = [_make_attachment()]
        input_data = {
            "project_context": {"title": "T", "state": "open", "project_type": "software"},
            "recent_messages": [],
            "attachments": attachments,
        }
        ctx = _build_prompt_context(input_data)
        assert ctx["attachments"] == attachments

    def test_missing_attachments_defaults_empty(self):
        input_data = {
            "project_context": {"title": "T"},
            "recent_messages": [],
        }
        ctx = _build_prompt_context(input_data)
        assert ctx["attachments"] == []


# ── Context Extension prompt tests ──


class TestContextExtensionWithAttachments:
    """Test that context extension prompt includes attachment content."""

    def test_extension_prompt_includes_attachments(self):
        messages = [_make_message()]
        attachments = [_make_attachment()]
        prompt = build_extension_prompt("search query", messages, attachments)

        assert "<project_attachments>" in prompt
        assert 'filename="requirements.pdf"' in prompt
        assert "This document describes the project requirements." in prompt

    def test_extension_prompt_no_attachments(self):
        messages = [_make_message()]
        prompt = build_extension_prompt("search query", messages, [])
        assert "<project_attachments>" not in prompt

    def test_extension_prompt_default_no_attachments(self):
        """Backward compat: calling without attachments arg works."""
        messages = [_make_message()]
        prompt = build_extension_prompt("search query", messages)
        assert "<project_attachments>" not in prompt

    def test_format_attachments_function(self):
        attachments = [_make_attachment()]
        result = _format_attachments(attachments)
        assert "<project_attachments>" in result
        assert "</project_attachments>" in result
        assert 'filename="requirements.pdf"' in result

    def test_format_attachments_empty(self):
        result = _format_attachments([])
        assert result == ""


# ── CoreClient.get_project_attachments tests ──


class TestCoreClientGetProjectAttachments:
    """Test CoreClient.get_project_attachments()."""

    @patch("grpc_clients.core_client.CoreClient.__init__", return_value=None)
    def test_returns_completed_attachments(self, _init):
        from grpc_clients.core_client import CoreClient

        client = CoreClient.__new__(CoreClient)
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (
                "att-001", "doc.pdf", "application/pdf", 5000,
                "Extracted text", "completed", "msg-001",
            ),
        ]
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        with patch("django.db.connection", mock_conn):
            result = client.get_project_attachments("proj-001")

        assert len(result) == 1
        assert result[0]["id"] == "att-001"
        assert result[0]["filename"] == "doc.pdf"
        assert result[0]["extracted_content"] == "Extracted text"
        assert result[0]["message_id"] == "msg-001"

    @patch("grpc_clients.core_client.CoreClient.__init__", return_value=None)
    def test_returns_empty_when_no_attachments(self, _init):
        from grpc_clients.core_client import CoreClient

        client = CoreClient.__new__(CoreClient)
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        with patch("django.db.connection", mock_conn):
            result = client.get_project_attachments("proj-001")

        assert result == []

    @patch("grpc_clients.core_client.CoreClient.__init__", return_value=None)
    def test_null_message_id_becomes_none(self, _init):
        from grpc_clients.core_client import CoreClient

        client = CoreClient.__new__(CoreClient)
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("att-002", "img.png", "image/png", 3000, "Image desc", "completed", None),
        ]
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        with patch("django.db.connection", mock_conn):
            result = client.get_project_attachments("proj-001")

        assert result[0]["message_id"] is None
