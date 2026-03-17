"""Tests for AIEventConsumer — event processing, retry, idempotency, DLQ."""

import asyncio
import json
import sys
import uuid
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from django.test import TestCase, override_settings

# Force-load the gateway events.consumers module (not the AI service's).
# Both services share the `events.consumers` namespace on the test pythonpath.
_gateway_events_dir = str(Path(__file__).resolve().parents[3] / "events")
_orig = sys.path[:]
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
if "events.consumers" in sys.modules:
    del sys.modules["events.consumers"]
if "events" in sys.modules:
    del sys.modules["events"]
import events.consumers as _gw_consumers  # noqa: E402

AIEventConsumer = _gw_consumers.AIEventConsumer
_MODULE_PATH = _gw_consumers.__name__
sys.path[:] = _orig


def _make_event(event_type: str, **kwargs) -> dict:
    """Create a test event with defaults."""
    base = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "project_id": str(uuid.uuid4()),
    }
    base.update(kwargs)
    return base


class TestAIEventConsumerChatResponse(TestCase):
    """ai.chat_response.ready → persist + broadcast."""

    def setUp(self):
        self.core_client = MagicMock()
        self.core_client.persist_ai_chat_message.return_value = {
            "message_id": str(uuid.uuid4()),
            "created_at": "2026-03-11T12:00:00Z",
        }
        self.consumer = AIEventConsumer(core_client=self.core_client)

    @override_settings(CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}})
    @patch.object(_gw_consumers, "get_channel_layer")
    def test_chat_response_persists_and_broadcasts(self, mock_gcl):
        mock_group_send = AsyncMock()
        mock_layer = MagicMock()
        mock_layer.group_send = mock_group_send
        mock_gcl.return_value = mock_layer

        event = _make_event(
            "ai.chat_response.ready",
            content="Hello from AI",
            message_type="regular",
            sender_type="ai",
            ai_agent="facilitator",
        )

        result = asyncio.get_event_loop().run_until_complete(
            self.consumer.process_event(event)
        )

        assert result is True
        self.core_client.persist_ai_chat_message.assert_called_once_with(
            project_id=event["project_id"],
            content="Hello from AI",
            message_type="regular",
        )
        mock_group_send.assert_called_once()
        call_args = mock_group_send.call_args[0]
        assert call_args[0] == f"project_{event['project_id']}"
        ws_event = call_args[1]
        assert ws_event["type"] == "chat_message"
        assert ws_event["payload"]["sender_type"] == "ai"
        assert ws_event["payload"]["ai_agent"] == "facilitator"
        assert ws_event["payload"]["content"] == "Hello from AI"
        assert ws_event["payload"]["message_type"] == "regular"

    @override_settings(CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}})
    @patch.object(_gw_consumers, "get_channel_layer")
    def test_chat_response_includes_full_entity_data(self, mock_gcl):
        msg_id = str(uuid.uuid4())
        self.core_client.persist_ai_chat_message.return_value = {
            "message_id": msg_id,
            "created_at": "2026-03-11T12:00:00Z",
        }
        mock_layer = MagicMock()
        mock_layer.group_send = AsyncMock()
        mock_gcl.return_value = mock_layer

        event = _make_event(
            "ai.chat_response.ready",
            content="Test",
            ai_agent="facilitator",
        )

        asyncio.get_event_loop().run_until_complete(
            self.consumer.process_event(event)
        )

        payload = mock_layer.group_send.call_args[0][1]["payload"]
        assert payload["id"] == msg_id
        assert payload["created_at"] == "2026-03-11T12:00:00Z"
        assert payload["sender_id"] is None  # AI messages have no user sender


class TestAIEventConsumerReaction(TestCase):
    """ai.reaction.ready → persist + broadcast."""

    def setUp(self):
        self.core_client = MagicMock()
        self.reaction_id = str(uuid.uuid4())
        self.core_client.persist_ai_reaction.return_value = {
            "reaction_id": self.reaction_id,
        }
        self.consumer = AIEventConsumer(core_client=self.core_client)

    @override_settings(CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}})
    @patch.object(_gw_consumers, "get_channel_layer")
    def test_reaction_persists_and_broadcasts(self, mock_gcl):
        mock_layer = MagicMock()
        mock_layer.group_send = AsyncMock()
        mock_gcl.return_value = mock_layer

        msg_id = str(uuid.uuid4())
        event = _make_event(
            "ai.reaction.ready",
            message_id=msg_id,
            reaction_type="thumbs_up",
        )

        result = asyncio.get_event_loop().run_until_complete(
            self.consumer.process_event(event)
        )

        assert result is True
        self.core_client.persist_ai_reaction.assert_called_once_with(
            project_id=event["project_id"],
            message_id=msg_id,
            reaction_type="thumbs_up",
        )
        ws_event = mock_layer.group_send.call_args[0][1]
        assert ws_event["type"] == "ai_reaction"
        assert ws_event["payload"]["message_id"] == msg_id
        assert ws_event["payload"]["reaction_type"] == "thumbs_up"
        assert ws_event["payload"]["id"] == self.reaction_id


class TestAIEventConsumerTitleUpdate(TestCase):
    """ai.title.updated → persist + broadcast."""

    def setUp(self):
        self.core_client = MagicMock()
        self.core_client.update_project_title.return_value = {"success": True}
        self.consumer = AIEventConsumer(core_client=self.core_client)

    @override_settings(CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}})
    @patch.object(_gw_consumers, "get_channel_layer")
    def test_title_update_persists_and_broadcasts(self, mock_gcl):
        mock_layer = MagicMock()
        mock_layer.group_send = AsyncMock()
        mock_gcl.return_value = mock_layer

        event = _make_event(
            "ai.title.updated",
            title="New Project Title",
        )

        result = asyncio.get_event_loop().run_until_complete(
            self.consumer.process_event(event)
        )

        assert result is True
        self.core_client.update_project_title.assert_called_once_with(
            project_id=event["project_id"],
            new_title="New Project Title",
        )
        ws_event = mock_layer.group_send.call_args[0][1]
        assert ws_event["type"] == "title_update"
        assert ws_event["payload"]["title"] == "New Project Title"
        assert ws_event["payload"]["project_id"] == event["project_id"]


class TestAIEventConsumerIdempotency(TestCase):
    """Duplicate event_id → skip processing."""

    def setUp(self):
        self.core_client = MagicMock()
        self.core_client.persist_ai_chat_message.return_value = {
            "message_id": "", "created_at": "",
        }
        self.consumer = AIEventConsumer(core_client=self.core_client)

    @patch.object(_gw_consumers, "get_channel_layer", return_value=None)
    def test_duplicate_event_skipped(self, _mock_gcl):
        event = _make_event(
            "ai.chat_response.ready",
            content="Hello",
            ai_agent="facilitator",
        )

        loop = asyncio.get_event_loop()
        result1 = loop.run_until_complete(self.consumer.process_event(event))
        assert result1 is True
        assert self.core_client.persist_ai_chat_message.call_count == 1

        result2 = loop.run_until_complete(self.consumer.process_event(event))
        assert result2 is True
        # Should NOT call persist again
        assert self.core_client.persist_ai_chat_message.call_count == 1
        assert event["event_id"] in self.consumer.processed_event_ids


class TestAIEventConsumerRetryAndDLQ(TestCase):
    """Retry with backoff then DLQ on persistent failure."""

    def setUp(self):
        self.core_client = MagicMock()
        self.consumer = AIEventConsumer(core_client=self.core_client)

    @patch.object(_gw_consumers.asyncio, "sleep", new_callable=AsyncMock)
    @patch.object(_gw_consumers, "get_channel_layer", return_value=None)
    def test_retries_three_times_then_dlq(self, _mock_gcl, mock_sleep):
        self.core_client.persist_ai_chat_message.side_effect = RuntimeError("gRPC down")

        event = _make_event(
            "ai.chat_response.ready",
            content="Fail",
            ai_agent="facilitator",
        )

        result = asyncio.get_event_loop().run_until_complete(
            self.consumer.process_event(event)
        )

        assert result is False
        assert self.core_client.persist_ai_chat_message.call_count == 3
        # Verify backoff delays: 1s, 2s, 4s
        assert mock_sleep.call_count == 3
        mock_sleep.assert_any_call(1)
        mock_sleep.assert_any_call(2)
        mock_sleep.assert_any_call(4)
        # Event should be in DLQ
        dlq = self.consumer.dead_letter_queue
        assert len(dlq) == 1
        assert dlq[0]["event_id"] == event["event_id"]

    @patch.object(_gw_consumers.asyncio, "sleep", new_callable=AsyncMock)
    @patch.object(_gw_consumers, "get_channel_layer", return_value=None)
    def test_succeeds_on_second_retry(self, _mock_gcl, mock_sleep):
        self.core_client.persist_ai_chat_message.side_effect = [
            RuntimeError("transient"),
            {"message_id": "ok", "created_at": "now"},
        ]

        event = _make_event(
            "ai.chat_response.ready",
            content="Retry success",
            ai_agent="facilitator",
        )

        result = asyncio.get_event_loop().run_until_complete(
            self.consumer.process_event(event)
        )

        assert result is True
        assert self.core_client.persist_ai_chat_message.call_count == 2
        assert mock_sleep.call_count == 1
        assert len(self.consumer.dead_letter_queue) == 0


class TestAIEventConsumerMalformed(TestCase):
    """Malformed events go straight to DLQ."""

    def setUp(self):
        self.consumer = AIEventConsumer()

    def test_missing_event_id_goes_to_dlq(self):
        event = {"event_type": "ai.chat_response.ready", "content": "x"}
        result = asyncio.get_event_loop().run_until_complete(
            self.consumer.process_event(event)
        )
        assert result is False
        assert len(self.consumer.dead_letter_queue) == 1

    def test_missing_event_type_goes_to_dlq(self):
        event = {"event_id": str(uuid.uuid4()), "content": "x"}
        result = asyncio.get_event_loop().run_until_complete(
            self.consumer.process_event(event)
        )
        assert result is False
        assert len(self.consumer.dead_letter_queue) == 1

    def test_unknown_event_type_goes_to_dlq(self):
        event = _make_event("ai.unknown.event")
        result = asyncio.get_event_loop().run_until_complete(
            self.consumer.process_event(event)
        )
        assert result is False
        assert len(self.consumer.dead_letter_queue) == 1


class TestAIEventConsumerBrdReady(TestCase):
    """T-4.3.02: ai.brd.ready → persist BRD sections + broadcast brd_ready."""

    def setUp(self):
        self.core_client = MagicMock()
        self.core_client.update_brd_draft.return_value = {"success": True}
        self.consumer = AIEventConsumer(core_client=self.core_client)

    @override_settings(CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}})
    @patch.object(_gw_consumers, "get_channel_layer")
    def test_brd_ready_persists_and_broadcasts(self, mock_gcl):
        """T-4.3.02: ai.brd.ready event persists sections to DB and broadcasts."""
        mock_layer = MagicMock()
        mock_layer.group_send = AsyncMock()
        mock_gcl.return_value = mock_layer

        sections = {
            "section_title": "Test Title",
            "section_short_description": "Test desc",
            "section_current_workflow": "Test workflow",
            "section_affected_department": "IT",
            "section_core_capabilities": "Test caps",
            "section_success_criteria": "Test criteria",
        }
        readiness = {"title": "ready", "short_description": "insufficient"}
        fabrication_flags = [{"section": "section_title", "ungrounded_keywords": ["SAP"], "match_ratio": 0.3}]

        event = _make_event(
            "ai.brd.ready",
            sections=sections,
            readiness_evaluation=readiness,
            fabrication_flags=fabrication_flags,
            mode="full_generation",
        )

        result = asyncio.get_event_loop().run_until_complete(
            self.consumer.process_event(event)
        )

        assert result is True
        self.core_client.update_brd_draft.assert_called_once_with(
            project_id=event["project_id"],
            sections=sections,
            readiness_evaluation_json=json.dumps(readiness),
        )
        ws_event = mock_layer.group_send.call_args[0][1]
        assert ws_event["type"] == "brd_ready"
        assert ws_event["payload"]["sections"] == sections
        assert ws_event["payload"]["readiness_evaluation"] == readiness
        assert ws_event["payload"]["fabrication_flags"] == fabrication_flags
        assert ws_event["payload"]["mode"] == "full_generation"


class TestAIEventConsumerLifecycle(TestCase):
    """Start/stop lifecycle."""

    def test_start_stop(self):
        consumer = AIEventConsumer()
        assert consumer._running is False
        consumer.start()
        assert consumer._running is True
        consumer.stop()
        assert consumer._running is False
