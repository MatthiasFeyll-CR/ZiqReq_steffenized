"""Unit tests for broadcast helpers in board/chat views.

Replaces dropped test_chat_message_broadcast_via_view_helper and
test_board_update_broadcast_via_view_helper. Uses mocked channel layer
so no async_to_sync race conditions.
"""

import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings


class TestBroadcastChatMessage(TestCase):
    """Test apps.chat.views._broadcast_chat_message."""

    @override_settings(CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}})
    @patch("apps.chat.views.async_to_sync")
    def test_broadcast_sends_correct_payload(self, mock_a2s):
        from apps.chat.views import _broadcast_chat_message

        mock_group_send = MagicMock()
        mock_a2s.return_value = mock_group_send

        idea_id = uuid.uuid4()
        user_id = uuid.uuid4()
        message = SimpleNamespace(
            id=uuid.uuid4(),
            idea_id=idea_id,
            sender_type="user",
            ai_agent=None,
            content="Hello world",
            message_type="regular",
            created_at=SimpleNamespace(isoformat=lambda: "2026-03-10T12:00:00+00:00"),
        )
        sender = SimpleNamespace(id=user_id, display_name="Alice")

        _broadcast_chat_message(message, sender)

        mock_group_send.assert_called_once()
        args = mock_group_send.call_args[0]
        assert args[0] == f"idea_{idea_id}"
        event = args[1]
        assert event["type"] == "chat_message"
        assert event["idea_id"] == str(idea_id)
        assert event["payload"]["id"] == str(message.id)
        assert event["payload"]["content"] == "Hello world"
        assert event["payload"]["sender_type"] == "user"
        assert event["payload"]["sender"]["id"] == str(user_id)
        assert event["payload"]["sender"]["display_name"] == "Alice"
        assert event["payload"]["ai_agent"] is None
        assert event["payload"]["message_type"] == "regular"

    @patch("apps.chat.views.get_channel_layer", return_value=None)
    def test_broadcast_noop_when_no_channel_layer(self, mock_gcl):
        from apps.chat.views import _broadcast_chat_message

        message = SimpleNamespace(
            id=uuid.uuid4(), idea_id=uuid.uuid4(), sender_type="user",
            ai_agent=None, content="x", message_type="regular",
            created_at=SimpleNamespace(isoformat=lambda: ""),
        )
        # Should not raise
        _broadcast_chat_message(message, SimpleNamespace(id=uuid.uuid4(), display_name="X"))


class TestBroadcastBoardUpdate(TestCase):
    """Test apps.board.views._broadcast_board_update."""

    @override_settings(CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}})
    @patch("apps.board.views.async_to_sync")
    def test_broadcast_sends_correct_payload(self, mock_a2s):
        from apps.board.views import _broadcast_board_update

        mock_group_send = MagicMock()
        mock_a2s.return_value = mock_group_send

        idea_id = uuid.uuid4()
        mutation = {"action": "create_node", "node_id": str(uuid.uuid4()), "title": "New Node"}

        _broadcast_board_update(
            str(idea_id),
            mutations=[mutation],
            source="user",
        )

        mock_group_send.assert_called_once()
        args = mock_group_send.call_args[0]
        assert args[0] == f"idea_{idea_id}"
        event = args[1]
        assert event["type"] == "board_update"
        assert event["idea_id"] == str(idea_id)
        assert event["payload"]["mutations"] == [mutation]
        assert event["payload"]["source"] == "user"

    @override_settings(CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}})
    @patch("apps.board.views.async_to_sync")
    def test_broadcast_node_delete(self, mock_a2s):
        from apps.board.views import _broadcast_board_update

        mock_group_send = MagicMock()
        mock_a2s.return_value = mock_group_send

        idea_id = uuid.uuid4()
        node_id = str(uuid.uuid4())
        mutation = {"action": "delete_node", "node_id": node_id}

        _broadcast_board_update(str(idea_id), mutations=[mutation], source="user")

        event = mock_group_send.call_args[0][1]
        assert event["payload"]["mutations"] == [mutation]

    @override_settings(CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}})
    @patch("apps.board.views.async_to_sync")
    def test_broadcast_noop_when_no_mutations(self, mock_a2s):
        from apps.board.views import _broadcast_board_update

        mock_group_send = MagicMock()
        mock_a2s.return_value = mock_group_send

        _broadcast_board_update(str(uuid.uuid4()), source="ai")

        mock_group_send.assert_not_called()

    @override_settings(CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}})
    @patch("apps.board.views.async_to_sync")
    def test_broadcast_ai_source(self, mock_a2s):
        from apps.board.views import _broadcast_board_update

        mock_group_send = MagicMock()
        mock_a2s.return_value = mock_group_send

        mutation = {"action": "create_node", "node_id": "test"}
        _broadcast_board_update(str(uuid.uuid4()), mutations=[mutation], source="ai")

        event = mock_group_send.call_args[0][1]
        assert event["payload"]["source"] == "ai"


class TestBroadcastBoardLockChange(TestCase):
    """Test apps.board.views._broadcast_board_lock_change."""

    @override_settings(CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}})
    @patch("apps.board.views.async_to_sync")
    def test_broadcast_lock_sends_correct_payload(self, mock_a2s):
        from apps.board.views import _broadcast_board_lock_change

        mock_group_send = MagicMock()
        mock_a2s.return_value = mock_group_send

        idea_id = uuid.uuid4()
        node_id = uuid.uuid4()
        user_id = uuid.uuid4()
        changed_by = {"id": str(user_id), "display_name": "Alice"}

        _broadcast_board_lock_change(str(idea_id), str(node_id), True, changed_by)

        mock_group_send.assert_called_once()
        args = mock_group_send.call_args[0]
        assert args[0] == f"idea_{idea_id}"
        event = args[1]
        assert event["type"] == "board_lock_change"
        assert event["payload"]["node_id"] == str(node_id)
        assert event["payload"]["is_locked"] is True
        assert event["payload"]["changed_by"] == changed_by

    @override_settings(CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}})
    @patch("apps.board.views.async_to_sync")
    def test_broadcast_unlock(self, mock_a2s):
        from apps.board.views import _broadcast_board_lock_change

        mock_group_send = MagicMock()
        mock_a2s.return_value = mock_group_send

        _broadcast_board_lock_change(
            str(uuid.uuid4()), str(uuid.uuid4()), False,
            {"id": str(uuid.uuid4()), "display_name": "Bob"},
        )

        event = mock_group_send.call_args[0][1]
        assert event["payload"]["is_locked"] is False
