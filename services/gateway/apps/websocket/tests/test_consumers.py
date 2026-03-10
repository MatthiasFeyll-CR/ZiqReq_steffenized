"""WebSocket consumer tests — DB-free via mocked auth and access checks.

All tests mock ``WebSocketAuthMiddleware._authenticate`` and
``IdeaConsumer._check_idea_access`` so that no ``database_sync_to_async``
calls hit the real database. This avoids the TransactionTestCase +
async worker-thread race condition that made the original tests flaky.
"""

import uuid
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from channels.layers import get_channel_layer
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator

from apps.websocket.consumers import IdeaConsumer, _presence_registry
from apps.websocket.middleware import WebSocketAuthMiddleware
from apps.websocket.routing import websocket_urlpatterns

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fake_user(user_id=None, display_name="Test User"):
    """Return a SimpleNamespace that quacks like a User model instance."""
    return SimpleNamespace(id=user_id or uuid.uuid4(), display_name=display_name)


def _make_application():
    return WebSocketAuthMiddleware(URLRouter(websocket_urlpatterns))


def _patch_auth(user):
    """Patch middleware._authenticate to return *user* (or None to reject)."""
    async def _auth(self, token):
        return user
    return patch.object(WebSocketAuthMiddleware, "_authenticate", _auth)


def _patch_access(allowed=True):
    """Patch consumer._check_idea_access to return *allowed*."""
    async def _access(self, idea_id, user_id):
        return allowed
    return patch.object(IdeaConsumer, "_check_idea_access", _access)


async def _subscribe_and_drain(communicator, idea_id: str) -> None:
    """Subscribe to idea and drain the resulting presence_update message."""
    await communicator.send_json_to({"type": "subscribe_idea", "idea_id": idea_id})
    resp = await communicator.receive_json_from(timeout=2)
    assert resp["type"] == "presence_update"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _clear_presence_registry():
    _presence_registry.clear()
    yield
    _presence_registry.clear()


# ---------------------------------------------------------------------------
# US-001: Connection lifecycle
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_connection_valid_token():
    """T-6.1.01: WebSocket connection with valid token succeeds."""
    user = _fake_user()
    app = _make_application()

    with _patch_auth(user):
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
        connected, _ = await communicator.connect()
        assert connected is True
        await communicator.disconnect()


@pytest.mark.asyncio
async def test_connection_invalid_token():
    """T-6.1.02: Connection with invalid token rejected."""
    app = _make_application()

    with _patch_auth(None):
        communicator = WebsocketCommunicator(app, "/ws/?token=expired")
        connected, code = await communicator.connect()
        assert connected is False


@pytest.mark.asyncio
async def test_connection_missing_token():
    """T-6.1.02b: Connection with missing token rejected."""
    app = _make_application()
    communicator = WebsocketCommunicator(app, "/ws/")
    connected, code = await communicator.connect()
    assert connected is False


@pytest.mark.asyncio
async def test_connection_nonexistent_user_token():
    """T-6.1.02c: Connection with valid UUID but nonexistent user rejected."""
    app = _make_application()

    with _patch_auth(None):
        communicator = WebsocketCommunicator(app, f"/ws/?token={uuid.uuid4()}")
        connected, code = await communicator.connect()
        assert connected is False


@pytest.mark.asyncio
async def test_error_on_unknown_message_type():
    """T-6.1.03: Unknown message types return error to client."""
    user = _fake_user()
    app = _make_application()

    with _patch_auth(user):
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
        connected, _ = await communicator.connect()
        assert connected is True

        await communicator.send_json_to({"type": "nonexistent_action"})
        response = await communicator.receive_json_from()
        assert response["type"] == "error"
        assert "Unknown message type" in response["payload"]["message"]

        await communicator.disconnect()


@pytest.mark.asyncio
async def test_error_on_missing_message_type():
    """T-6.1.03b: Missing message type returns error to client."""
    user = _fake_user()
    app = _make_application()

    with _patch_auth(user):
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
        connected, _ = await communicator.connect()
        assert connected is True

        await communicator.send_json_to({"data": "no type field"})
        response = await communicator.receive_json_from()
        assert response["type"] == "error"
        assert "Missing message type" in response["payload"]["message"]

        await communicator.disconnect()


# ---------------------------------------------------------------------------
# US-002: Channel group management
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_subscribe_idea_as_owner():
    """T-6.1.04: Owner can subscribe to idea group."""
    user = _fake_user()
    idea_id = str(uuid.uuid4())
    app = _make_application()

    with _patch_auth(user), _patch_access(True):
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
        connected, _ = await communicator.connect()
        assert connected is True

        await _subscribe_and_drain(communicator, idea_id)

        await communicator.disconnect()


@pytest.mark.asyncio
async def test_subscribe_idea_access_denied():
    """T-6.1.05: Non-member cannot subscribe to idea group."""
    user = _fake_user(display_name="Stranger")
    idea_id = str(uuid.uuid4())
    app = _make_application()

    with _patch_auth(user), _patch_access(False):
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
        connected, _ = await communicator.connect()
        assert connected is True

        await communicator.send_json_to({"type": "subscribe_idea", "idea_id": idea_id})
        response = await communicator.receive_json_from()
        assert response["type"] == "error"
        assert "Access denied" in response["payload"]["message"]

        await communicator.disconnect()


@pytest.mark.asyncio
async def test_subscribe_idea_missing_idea_id():
    """T-6.1.05c: Subscribe without idea_id returns error."""
    user = _fake_user()
    app = _make_application()

    with _patch_auth(user):
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
        connected, _ = await communicator.connect()
        assert connected is True

        await communicator.send_json_to({"type": "subscribe_idea"})
        response = await communicator.receive_json_from()
        assert response["type"] == "error"
        assert "Missing idea_id" in response["payload"]["message"]

        await communicator.disconnect()


@pytest.mark.asyncio
async def test_subscribe_idea_invalid_uuid():
    """T-6.1.05d: Subscribe with invalid UUID returns error."""
    user = _fake_user()
    app = _make_application()

    with _patch_auth(user):
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
        connected, _ = await communicator.connect()
        assert connected is True

        await communicator.send_json_to({"type": "subscribe_idea", "idea_id": "not-a-uuid"})
        response = await communicator.receive_json_from()
        assert response["type"] == "error"
        assert "Invalid idea_id" in response["payload"]["message"]

        await communicator.disconnect()


@pytest.mark.asyncio
async def test_unsubscribe_idea():
    """T-6.1.06: Unsubscribe removes consumer from idea group."""
    user = _fake_user()
    idea_id = str(uuid.uuid4())
    app = _make_application()

    with _patch_auth(user), _patch_access(True):
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
        connected, _ = await communicator.connect()
        assert connected is True

        await _subscribe_and_drain(communicator, idea_id)

        await communicator.send_json_to({"type": "unsubscribe_idea", "idea_id": idea_id})
        resp = await communicator.receive_json_from(timeout=2)
        assert resp["type"] == "presence_update"
        assert resp["payload"]["state"] == "offline"

        await communicator.disconnect()


@pytest.mark.asyncio
async def test_unsubscribe_idea_not_subscribed():
    """T-6.1.06b: Unsubscribe from non-subscribed idea is a no-op."""
    user = _fake_user()
    app = _make_application()

    with _patch_auth(user):
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
        connected, _ = await communicator.connect()
        assert connected is True

        await communicator.send_json_to({"type": "unsubscribe_idea", "idea_id": str(uuid.uuid4())})
        assert await communicator.receive_nothing(timeout=0.5) is True

        await communicator.disconnect()


@pytest.mark.asyncio
async def test_disconnect_cleans_up_groups():
    """T-6.1.06c: Disconnect automatically unsubscribes from all groups."""
    user = _fake_user()
    idea1 = str(uuid.uuid4())
    idea2 = str(uuid.uuid4())
    app = _make_application()

    with _patch_auth(user), _patch_access(True):
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
        connected, _ = await communicator.connect()
        assert connected is True

        await _subscribe_and_drain(communicator, idea1)
        await _subscribe_and_drain(communicator, idea2)

        await communicator.disconnect()


# ---------------------------------------------------------------------------
# US-003: Chat message broadcast
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_chat_message_broadcast_to_subscriber():
    """T-6.4.01: chat_message group_send is forwarded to subscribed WebSocket client."""
    user = _fake_user()
    idea_id = str(uuid.uuid4())
    app = _make_application()

    with _patch_auth(user), _patch_access(True):
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
        connected, _ = await communicator.connect()
        assert connected is True

        await _subscribe_and_drain(communicator, idea_id)

        channel_layer = get_channel_layer()
        payload = {
            "id": str(uuid.uuid4()),
            "sender_type": "user",
            "sender": {"id": str(user.id), "display_name": user.display_name},
            "ai_agent": None,
            "content": "Hello from broadcast",
            "message_type": "regular",
            "created_at": "2026-03-10T12:00:00+00:00",
        }
        await channel_layer.group_send(
            f"idea_{idea_id}",
            {"type": "chat_message", "idea_id": idea_id, "payload": payload},
        )

        response = await communicator.receive_json_from(timeout=2)
        assert response["type"] == "chat_message"
        assert response["idea_id"] == idea_id
        assert response["payload"]["content"] == "Hello from broadcast"
        assert response["payload"]["sender_type"] == "user"
        assert response["payload"]["sender"]["id"] == str(user.id)
        assert response["payload"]["ai_agent"] is None
        assert response["payload"]["message_type"] == "regular"

        await communicator.disconnect()


@pytest.mark.asyncio
async def test_chat_message_broadcast_not_received_by_unsubscribed():
    """T-6.4.01b: Unsubscribed clients do not receive chat_message broadcasts."""
    user = _fake_user()
    idea_id = str(uuid.uuid4())
    app = _make_application()

    with _patch_auth(user):
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
        connected, _ = await communicator.connect()
        assert connected is True

        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f"idea_{idea_id}",
            {"type": "chat_message", "idea_id": idea_id, "payload": {"content": "should not arrive"}},
        )

        assert await communicator.receive_nothing(timeout=1) is True

        await communicator.disconnect()


# ---------------------------------------------------------------------------
# US-004: Board sync broadcast
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_board_update_broadcast_to_subscriber():
    """T-6.4.03: board_update group_send is forwarded to subscribed WebSocket client."""
    user = _fake_user()
    idea_id = str(uuid.uuid4())
    app = _make_application()

    with _patch_auth(user), _patch_access(True):
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
        connected, _ = await communicator.connect()
        assert connected is True

        await _subscribe_and_drain(communicator, idea_id)

        channel_layer = get_channel_layer()
        payload = {
            "nodes_created": [],
            "nodes_updated": [{"id": str(uuid.uuid4()), "position_x": 150, "position_y": 250}],
            "nodes_deleted": [],
            "connections_created": [],
            "connections_updated": [],
            "connections_deleted": [],
            "source": "user",
        }
        await channel_layer.group_send(
            f"idea_{idea_id}",
            {"type": "board_update", "idea_id": idea_id, "payload": payload},
        )

        response = await communicator.receive_json_from(timeout=2)
        assert response["type"] == "board_update"
        assert response["idea_id"] == idea_id
        assert response["payload"]["nodes_updated"] == payload["nodes_updated"]
        assert response["payload"]["source"] == "user"

        await communicator.disconnect()


@pytest.mark.asyncio
async def test_board_update_not_received_by_unsubscribed():
    """T-6.4.03b: Unsubscribed clients do not receive board_update broadcasts."""
    user = _fake_user()
    idea_id = str(uuid.uuid4())
    app = _make_application()

    with _patch_auth(user):
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
        connected, _ = await communicator.connect()
        assert connected is True

        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f"idea_{idea_id}",
            {"type": "board_update", "idea_id": idea_id, "payload": {"nodes_updated": [], "source": "user"}},
        )

        assert await communicator.receive_nothing(timeout=1) is True

        await communicator.disconnect()


@pytest.mark.asyncio
async def test_board_update_broadcast_node_delete():
    """T-3.6.01: board_update with nodes_deleted broadcast."""
    user = _fake_user()
    idea_id = str(uuid.uuid4())
    node_id = str(uuid.uuid4())
    app = _make_application()

    with _patch_auth(user), _patch_access(True):
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
        connected, _ = await communicator.connect()
        assert connected is True

        await _subscribe_and_drain(communicator, idea_id)

        channel_layer = get_channel_layer()
        payload = {
            "nodes_created": [],
            "nodes_updated": [],
            "nodes_deleted": [node_id],
            "connections_created": [],
            "connections_updated": [],
            "connections_deleted": [],
            "source": "user",
        }
        await channel_layer.group_send(
            f"idea_{idea_id}",
            {"type": "board_update", "idea_id": idea_id, "payload": payload},
        )

        response = await communicator.receive_json_from(timeout=2)
        assert response["type"] == "board_update"
        assert node_id in response["payload"]["nodes_deleted"]
        assert response["payload"]["source"] == "user"

        await communicator.disconnect()


@pytest.mark.asyncio
async def test_board_update_broadcast_source_ai():
    """T-3.6.02: board_update payload source is 'ai' when node created by AI."""
    user = _fake_user()
    idea_id = str(uuid.uuid4())
    app = _make_application()

    with _patch_auth(user), _patch_access(True):
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
        connected, _ = await communicator.connect()
        assert connected is True

        await _subscribe_and_drain(communicator, idea_id)

        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f"idea_{idea_id}",
            {
                "type": "board_update",
                "idea_id": idea_id,
                "payload": {
                    "nodes_created": [{"id": str(uuid.uuid4()), "title": "AI Node"}],
                    "nodes_updated": [], "nodes_deleted": [],
                    "connections_created": [], "connections_updated": [], "connections_deleted": [],
                    "source": "ai",
                },
            },
        )

        response = await communicator.receive_json_from(timeout=2)
        assert response["type"] == "board_update"
        assert response["payload"]["source"] == "ai"

        await communicator.disconnect()


# ---------------------------------------------------------------------------
# US-005: Board awareness events
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_board_selection_broadcast_excludes_sender():
    """T-3.5.01: board_selection from client is broadcast to other subscribers, not sender."""
    owner = _fake_user(display_name="Owner")
    other = _fake_user(display_name="Other")
    idea_id = str(uuid.uuid4())
    app = _make_application()

    with _patch_access(True):
        with _patch_auth(owner):
            comm_sender = WebsocketCommunicator(app, f"/ws/?token={owner.id}")
            connected1, _ = await comm_sender.connect()
            assert connected1

        with _patch_auth(other):
            comm_receiver = WebsocketCommunicator(app, f"/ws/?token={other.id}")
            connected2, _ = await comm_receiver.connect()
            assert connected2

        await _subscribe_and_drain(comm_sender, idea_id)
        await _subscribe_and_drain(comm_receiver, idea_id)
        # Drain cross-presence
        await comm_sender.receive_json_from(timeout=2)

        node_id = str(uuid.uuid4())
        await comm_sender.send_json_to({
            "type": "board_selection",
            "idea_id": idea_id,
            "payload": {"node_id": node_id},
        })

        response = await comm_receiver.receive_json_from(timeout=2)
        assert response["type"] == "board_selection"
        assert response["idea_id"] == idea_id
        assert response["payload"]["node_id"] == node_id
        assert response["payload"]["user"]["id"] == str(owner.id)
        assert response["payload"]["user"]["display_name"] == "Owner"

        assert await comm_sender.receive_nothing(timeout=0.5) is True

        await comm_sender.disconnect()
        await comm_receiver.disconnect()


@pytest.mark.asyncio
async def test_board_selection_deselect_null_node():
    """T-3.5.03: board_selection with node_id=null broadcasts deselection."""
    owner = _fake_user(display_name="Owner")
    other = _fake_user(display_name="Other")
    idea_id = str(uuid.uuid4())
    app = _make_application()

    with _patch_access(True):
        with _patch_auth(owner):
            comm_sender = WebsocketCommunicator(app, f"/ws/?token={owner.id}")
            connected1, _ = await comm_sender.connect()
            assert connected1

        with _patch_auth(other):
            comm_receiver = WebsocketCommunicator(app, f"/ws/?token={other.id}")
            connected2, _ = await comm_receiver.connect()
            assert connected2

        await _subscribe_and_drain(comm_sender, idea_id)
        await _subscribe_and_drain(comm_receiver, idea_id)
        await comm_sender.receive_json_from(timeout=2)

        await comm_sender.send_json_to({
            "type": "board_selection",
            "idea_id": idea_id,
            "payload": {"node_id": None},
        })

        response = await comm_receiver.receive_json_from(timeout=2)
        assert response["type"] == "board_selection"
        assert response["payload"]["node_id"] is None
        assert response["payload"]["user"]["id"] == str(owner.id)

        await comm_sender.disconnect()
        await comm_receiver.disconnect()


@pytest.mark.asyncio
async def test_board_selection_not_subscribed_error():
    """T-3.5.02: board_selection fails if not subscribed to idea."""
    user = _fake_user()
    app = _make_application()

    with _patch_auth(user):
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
        connected, _ = await communicator.connect()
        assert connected is True

        await communicator.send_json_to({
            "type": "board_selection",
            "idea_id": str(uuid.uuid4()),
            "payload": {"node_id": str(uuid.uuid4())},
        })

        response = await communicator.receive_json_from(timeout=2)
        assert response["type"] == "error"
        assert "Not subscribed" in response["payload"]["message"]

        await communicator.disconnect()


@pytest.mark.asyncio
async def test_board_lock_change_broadcast():
    """T-3.5.03b: board_lock_change broadcast via channel layer."""
    user = _fake_user()
    idea_id = str(uuid.uuid4())
    node_id = str(uuid.uuid4())
    app = _make_application()

    with _patch_auth(user), _patch_access(True):
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
        connected, _ = await communicator.connect()
        assert connected is True

        await _subscribe_and_drain(communicator, idea_id)

        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f"idea_{idea_id}",
            {
                "type": "board_lock_change",
                "idea_id": idea_id,
                "payload": {
                    "node_id": str(node_id),
                    "is_locked": True,
                    "changed_by": {"id": str(user.id), "display_name": user.display_name},
                },
            },
        )

        response = await communicator.receive_json_from(timeout=2)
        assert response["type"] == "board_lock_change"
        assert response["idea_id"] == idea_id
        assert response["payload"]["node_id"] == str(node_id)
        assert response["payload"]["is_locked"] is True
        assert response["payload"]["changed_by"]["id"] == str(user.id)

        await communicator.disconnect()


# ---------------------------------------------------------------------------
# US-007: Presence tracking
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_presence_broadcast_on_subscribe():
    """T-6.3.01: Subscribe to idea broadcasts presence_update 'online' to all subscribers."""
    owner = _fake_user(display_name="Owner")
    other = _fake_user(display_name="Other")
    idea_id = str(uuid.uuid4())
    app = _make_application()

    with _patch_access(True):
        with _patch_auth(owner):
            comm1 = WebsocketCommunicator(app, f"/ws/?token={owner.id}")
            connected1, _ = await comm1.connect()
            assert connected1

        await comm1.send_json_to({"type": "subscribe_idea", "idea_id": idea_id})
        resp1 = await comm1.receive_json_from(timeout=2)
        assert resp1["type"] == "presence_update"
        assert resp1["payload"]["user"]["id"] == str(owner.id)
        assert resp1["payload"]["state"] == "online"

        with _patch_auth(other):
            comm2 = WebsocketCommunicator(app, f"/ws/?token={other.id}")
            connected2, _ = await comm2.connect()
            assert connected2

        await comm2.send_json_to({"type": "subscribe_idea", "idea_id": idea_id})

        resp_other = await comm1.receive_json_from(timeout=2)
        assert resp_other["type"] == "presence_update"
        assert resp_other["payload"]["user"]["id"] == str(other.id)
        assert resp_other["payload"]["state"] == "online"

        resp_self = await comm2.receive_json_from(timeout=2)
        assert resp_self["type"] == "presence_update"
        assert resp_self["payload"]["user"]["id"] == str(other.id)
        assert resp_self["payload"]["state"] == "online"

        await comm1.disconnect()
        await comm2.disconnect()


@pytest.mark.asyncio
async def test_presence_multi_tab_dedup():
    """T-6.3.02: Same user in 2 tabs shows single presence, offline only after both disconnect."""
    user = _fake_user(display_name="MultiTab User")
    observer = _fake_user(display_name="Observer")
    idea_id = str(uuid.uuid4())
    app = _make_application()

    with _patch_access(True):
        with _patch_auth(observer):
            comm_observer = WebsocketCommunicator(app, f"/ws/?token={observer.id}")
            connected_obs, _ = await comm_observer.connect()
            assert connected_obs

        await comm_observer.send_json_to({"type": "subscribe_idea", "idea_id": idea_id})
        await comm_observer.receive_json_from(timeout=2)  # own presence

        # Tab 1 subscribes
        with _patch_auth(user):
            comm_tab1 = WebsocketCommunicator(app, f"/ws/?token={user.id}")
            connected1, _ = await comm_tab1.connect()
            assert connected1

        await comm_tab1.send_json_to({"type": "subscribe_idea", "idea_id": idea_id})
        resp_online = await comm_observer.receive_json_from(timeout=2)
        assert resp_online["payload"]["user"]["id"] == str(user.id)
        assert resp_online["payload"]["state"] == "online"
        await comm_tab1.receive_json_from(timeout=2)  # drain tab1's own presence

        # Tab 2 subscribes — no new online event (already present)
        with _patch_auth(user):
            comm_tab2 = WebsocketCommunicator(app, f"/ws/?token={user.id}")
            connected2, _ = await comm_tab2.connect()
            assert connected2

        await comm_tab2.send_json_to({"type": "subscribe_idea", "idea_id": idea_id})
        assert await comm_observer.receive_nothing(timeout=1) is True

        # Tab 1 disconnects — user still has tab 2, no offline
        await comm_tab1.disconnect()
        assert await comm_observer.receive_nothing(timeout=1) is True

        # Tab 2 disconnects — last tab, broadcast offline
        await comm_tab2.disconnect()
        resp_offline = await comm_observer.receive_json_from(timeout=2)
        assert resp_offline["type"] == "presence_update"
        assert resp_offline["payload"]["user"]["id"] == str(user.id)
        assert resp_offline["payload"]["state"] == "offline"

        await comm_observer.disconnect()


@pytest.mark.asyncio
async def test_presence_offline_on_unsubscribe():
    """T-6.3.03: Unsubscribe broadcasts offline presence for user."""
    owner = _fake_user(display_name="Owner")
    other = _fake_user(display_name="Observer")
    idea_id = str(uuid.uuid4())
    app = _make_application()

    with _patch_access(True):
        with _patch_auth(owner):
            comm_owner = WebsocketCommunicator(app, f"/ws/?token={owner.id}")
            connected1, _ = await comm_owner.connect()
            assert connected1

        with _patch_auth(other):
            comm_other = WebsocketCommunicator(app, f"/ws/?token={other.id}")
            connected2, _ = await comm_other.connect()
            assert connected2

        await comm_owner.send_json_to({"type": "subscribe_idea", "idea_id": idea_id})
        await comm_owner.receive_json_from(timeout=2)  # own presence

        await comm_other.send_json_to({"type": "subscribe_idea", "idea_id": idea_id})
        await comm_other.receive_json_from(timeout=2)  # own presence
        await comm_owner.receive_json_from(timeout=2)  # other's presence

        await comm_owner.send_json_to({"type": "unsubscribe_idea", "idea_id": idea_id})

        resp = await comm_other.receive_json_from(timeout=2)
        assert resp["type"] == "presence_update"
        assert resp["payload"]["user"]["id"] == str(owner.id)
        assert resp["payload"]["state"] == "offline"

        await comm_owner.disconnect()
        await comm_other.disconnect()


@pytest.mark.asyncio
async def test_presence_update_client_message():
    """T-6.3.04: Client presence_update message broadcasts to idea group."""
    owner = _fake_user(display_name="Owner")
    other = _fake_user(display_name="Observer")
    idea_id = str(uuid.uuid4())
    app = _make_application()

    with _patch_access(True):
        with _patch_auth(owner):
            comm_sender = WebsocketCommunicator(app, f"/ws/?token={owner.id}")
            connected1, _ = await comm_sender.connect()
            assert connected1

        with _patch_auth(other):
            comm_receiver = WebsocketCommunicator(app, f"/ws/?token={other.id}")
            connected2, _ = await comm_receiver.connect()
            assert connected2

        await comm_sender.send_json_to({"type": "subscribe_idea", "idea_id": idea_id})
        await comm_sender.receive_json_from(timeout=2)  # own presence

        await comm_receiver.send_json_to({"type": "subscribe_idea", "idea_id": idea_id})
        await comm_receiver.receive_json_from(timeout=2)  # own presence
        await comm_sender.receive_json_from(timeout=2)  # other's presence

        await comm_sender.send_json_to({
            "type": "presence_update",
            "payload": {"state": "active", "idea_id": idea_id},
        })

        resp = await comm_receiver.receive_json_from(timeout=2)
        assert resp["type"] == "presence_update"
        assert resp["payload"]["user"]["id"] == str(owner.id)
        assert resp["payload"]["state"] == "online"

        await comm_sender.disconnect()
        await comm_receiver.disconnect()
