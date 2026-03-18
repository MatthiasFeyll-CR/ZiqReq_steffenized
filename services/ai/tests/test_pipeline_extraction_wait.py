"""Tests for ChatProcessingPipeline extraction wait logic (US-007).

Covers: wait for pending attachments, timeout behavior, no-op when no attachments,
immediate proceed when all completed.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


def _make_project_context(
    messages: list[dict] | None = None,
) -> dict:
    """Create a minimal project context dict."""
    return {
        "project": {"id": "proj-1", "title": "Test", "state": "open", "owner_id": "user-1"},
        "recent_messages": messages or [],
        "chat_summary": None,
    }


def _make_message(
    sender_type: str = "user",
    attachments: list[dict] | None = None,
) -> dict:
    return {
        "id": "msg-1",
        "sender_type": sender_type,
        "sender_id": "user-1",
        "ai_agent": None,
        "content": "test message",
        "message_type": "regular",
        "created_at": "2026-01-01T00:00:00",
        "sender_name": "User",
        "attachments": attachments or [],
    }


class TestWaitForExtraction:
    """Test _wait_for_extraction in ChatProcessingPipeline."""

    @pytest.mark.asyncio
    async def test_no_messages_returns_immediately(self) -> None:
        from processing.pipeline import ChatProcessingPipeline

        core_client = MagicMock()
        pipeline = ChatProcessingPipeline(core_client=core_client)

        context = _make_project_context(messages=[])
        result = await pipeline._wait_for_extraction("proj-1", context)

        assert result is context  # unchanged

    @pytest.mark.asyncio
    async def test_no_attachments_returns_immediately(self) -> None:
        from processing.pipeline import ChatProcessingPipeline

        core_client = MagicMock()
        pipeline = ChatProcessingPipeline(core_client=core_client)

        msg = _make_message(sender_type="user", attachments=[])
        context = _make_project_context(messages=[msg])
        result = await pipeline._wait_for_extraction("proj-1", context)

        assert result is context

    @pytest.mark.asyncio
    async def test_all_completed_returns_immediately(self) -> None:
        from processing.pipeline import ChatProcessingPipeline

        core_client = MagicMock()
        pipeline = ChatProcessingPipeline(core_client=core_client)

        att = {"id": "att-1", "extraction_status": "completed"}
        msg = _make_message(attachments=[att])
        context = _make_project_context(messages=[msg])
        result = await pipeline._wait_for_extraction("proj-1", context)

        assert result is context
        core_client.get_project_context.assert_not_called()

    @pytest.mark.asyncio
    async def test_waits_for_pending_then_proceeds(self) -> None:
        from processing.pipeline import ChatProcessingPipeline

        core_client = MagicMock()
        pipeline = ChatProcessingPipeline(core_client=core_client)
        # Override poll interval for faster test
        pipeline.EXTRACTION_POLL_INTERVAL = 0.05

        att_pending = {"id": "att-1", "extraction_status": "pending"}
        msg_pending = _make_message(attachments=[att_pending])
        context_pending = _make_project_context(messages=[msg_pending])

        # After poll: return completed
        att_completed = {"id": "att-1", "extraction_status": "completed"}
        msg_completed = _make_message(attachments=[att_completed])
        context_completed = _make_project_context(messages=[msg_completed])

        core_client.get_project_context.return_value = context_completed

        result = await pipeline._wait_for_extraction("proj-1", context_pending)

        assert result is context_completed
        core_client.get_project_context.assert_called_once_with("proj-1")

    @pytest.mark.asyncio
    async def test_timeout_proceeds_with_partial_context(self) -> None:
        from processing.pipeline import ChatProcessingPipeline

        core_client = MagicMock()
        pipeline = ChatProcessingPipeline(core_client=core_client)
        # Very short timeout for test
        pipeline.EXTRACTION_POLL_INTERVAL = 0.02
        pipeline.EXTRACTION_POLL_TIMEOUT = 0.05

        att_processing = {"id": "att-1", "extraction_status": "processing"}
        msg_processing = _make_message(attachments=[att_processing])
        context_processing = _make_project_context(messages=[msg_processing])

        # Always return processing
        core_client.get_project_context.return_value = context_processing

        result = await pipeline._wait_for_extraction("proj-1", context_processing)

        # Should return the last-fetched context (still processing — timed out)
        assert result is not None
        # get_project_context was called at least once during polling
        assert core_client.get_project_context.call_count >= 1

    @pytest.mark.asyncio
    async def test_only_checks_triggering_user_message(self) -> None:
        from processing.pipeline import ChatProcessingPipeline

        core_client = MagicMock()
        pipeline = ChatProcessingPipeline(core_client=core_client)

        # AI message at the end (not a user message)
        ai_msg = _make_message(sender_type="ai", attachments=[
            {"id": "att-1", "extraction_status": "pending"},
        ])
        user_msg = _make_message(sender_type="user", attachments=[
            {"id": "att-2", "extraction_status": "completed"},
        ])
        context = _make_project_context(messages=[user_msg, ai_msg])

        result = await pipeline._wait_for_extraction("proj-1", context)

        # Should not poll — the triggering user message has completed attachments
        assert result is context
        core_client.get_project_context.assert_not_called()
