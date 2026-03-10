import uuid

import pytest
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.test import override_settings

from apps.authentication.models import User
from apps.board.models import BoardNode
from apps.ideas.models import ChatMessage, Idea, IdeaCollaborator
from apps.websocket.middleware import WebSocketAuthMiddleware
from apps.websocket.routing import websocket_urlpatterns


def _make_application():
    return WebSocketAuthMiddleware(URLRouter(websocket_urlpatterns))


@database_sync_to_async
def _create_user(**kwargs):
    defaults = {
        "id": uuid.uuid4(),
        "email": f"test-{uuid.uuid4().hex[:8]}@ziqreq.local",
        "first_name": "Test",
        "last_name": "User",
        "display_name": "Test User",
        "roles": ["user"],
    }
    defaults.update(kwargs)
    return User.objects.create(**defaults)


@database_sync_to_async
def _create_idea(owner_id, **kwargs):
    defaults = {
        "id": uuid.uuid4(),
        "title": "Test Idea",
        "owner_id": owner_id,
    }
    defaults.update(kwargs)
    return Idea.objects.create(**defaults)


@database_sync_to_async
def _add_collaborator(idea_id, user_id):
    return IdeaCollaborator.objects.create(idea_id=idea_id, user_id=user_id)


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@override_settings(DEBUG=True, AUTH_BYPASS=True)
async def test_connection_valid_token():
    """T-6.1.01: WebSocket connection with valid token succeeds."""
    user = await _create_user()
    app = _make_application()
    communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")

    connected, _ = await communicator.connect()
    assert connected is True

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@override_settings(DEBUG=True, AUTH_BYPASS=True)
async def test_connection_invalid_token():
    """T-6.1.02: Connection with invalid token rejected."""
    app = _make_application()
    communicator = WebsocketCommunicator(app, "/ws/?token=expired")

    connected, code = await communicator.connect()
    assert connected is False


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@override_settings(DEBUG=True, AUTH_BYPASS=True)
async def test_connection_missing_token():
    """T-6.1.02b: Connection with missing token rejected."""
    app = _make_application()
    communicator = WebsocketCommunicator(app, "/ws/")

    connected, code = await communicator.connect()
    assert connected is False


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@override_settings(DEBUG=True, AUTH_BYPASS=True)
async def test_connection_nonexistent_user_token():
    """T-6.1.02c: Connection with valid UUID but nonexistent user rejected."""
    app = _make_application()
    fake_id = uuid.uuid4()
    communicator = WebsocketCommunicator(app, f"/ws/?token={fake_id}")

    connected, code = await communicator.connect()
    assert connected is False


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@override_settings(DEBUG=True, AUTH_BYPASS=True)
async def test_error_on_unknown_message_type():
    """T-6.1.03: Unknown message types return error to client."""
    user = await _create_user()
    app = _make_application()
    communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")

    connected, _ = await communicator.connect()
    assert connected is True

    await communicator.send_json_to({"type": "nonexistent_action"})
    response = await communicator.receive_json_from()
    assert response["type"] == "error"
    assert "Unknown message type" in response["payload"]["message"]

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@override_settings(DEBUG=True, AUTH_BYPASS=True)
async def test_error_on_missing_message_type():
    """T-6.1.03b: Missing message type returns error to client."""
    user = await _create_user()
    app = _make_application()
    communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")

    connected, _ = await communicator.connect()
    assert connected is True

    await communicator.send_json_to({"data": "no type field"})
    response = await communicator.receive_json_from()
    assert response["type"] == "error"
    assert "Missing message type" in response["payload"]["message"]

    await communicator.disconnect()


# ---- US-002: Channel group management tests ----


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@override_settings(DEBUG=True, AUTH_BYPASS=True)
async def test_subscribe_idea_as_owner():
    """T-6.1.04: Owner can subscribe to idea group."""
    user = await _create_user()
    idea = await _create_idea(owner_id=user.id)
    app = _make_application()
    communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")

    connected, _ = await communicator.connect()
    assert connected is True

    await communicator.send_json_to({"type": "subscribe_idea", "idea_id": str(idea.id)})
    # No error response expected — successful subscribe is silent
    assert await communicator.receive_nothing(timeout=0.5) is True

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@override_settings(DEBUG=True, AUTH_BYPASS=True)
async def test_subscribe_idea_as_co_owner():
    """T-6.1.04b: Co-owner can subscribe to idea group."""
    owner = await _create_user(display_name="Owner")
    co_owner = await _create_user(display_name="CoOwner")
    idea = await _create_idea(owner_id=owner.id, co_owner_id=co_owner.id)
    app = _make_application()
    communicator = WebsocketCommunicator(app, f"/ws/?token={co_owner.id}")

    connected, _ = await communicator.connect()
    assert connected is True

    await communicator.send_json_to({"type": "subscribe_idea", "idea_id": str(idea.id)})
    assert await communicator.receive_nothing(timeout=0.5) is True

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@override_settings(DEBUG=True, AUTH_BYPASS=True)
async def test_subscribe_idea_as_collaborator():
    """T-6.1.04c: Collaborator can subscribe to idea group."""
    owner = await _create_user(display_name="Owner")
    collaborator = await _create_user(display_name="Collaborator")
    idea = await _create_idea(owner_id=owner.id)
    await _add_collaborator(idea_id=idea.id, user_id=collaborator.id)
    app = _make_application()
    communicator = WebsocketCommunicator(app, f"/ws/?token={collaborator.id}")

    connected, _ = await communicator.connect()
    assert connected is True

    await communicator.send_json_to({"type": "subscribe_idea", "idea_id": str(idea.id)})
    assert await communicator.receive_nothing(timeout=0.5) is True

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@override_settings(DEBUG=True, AUTH_BYPASS=True)
async def test_subscribe_idea_access_denied():
    """T-6.1.05: Non-member cannot subscribe to idea group."""
    owner = await _create_user(display_name="Owner")
    stranger = await _create_user(display_name="Stranger")
    idea = await _create_idea(owner_id=owner.id)
    app = _make_application()
    communicator = WebsocketCommunicator(app, f"/ws/?token={stranger.id}")

    connected, _ = await communicator.connect()
    assert connected is True

    await communicator.send_json_to({"type": "subscribe_idea", "idea_id": str(idea.id)})
    response = await communicator.receive_json_from()
    assert response["type"] == "error"
    assert "Access denied" in response["payload"]["message"]

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@override_settings(DEBUG=True, AUTH_BYPASS=True)
async def test_subscribe_idea_nonexistent():
    """T-6.1.05b: Subscribe to nonexistent idea returns access denied."""
    user = await _create_user()
    app = _make_application()
    communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")

    connected, _ = await communicator.connect()
    assert connected is True

    fake_idea_id = str(uuid.uuid4())
    await communicator.send_json_to({"type": "subscribe_idea", "idea_id": fake_idea_id})
    response = await communicator.receive_json_from()
    assert response["type"] == "error"
    assert "Access denied" in response["payload"]["message"]

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@override_settings(DEBUG=True, AUTH_BYPASS=True)
async def test_subscribe_idea_missing_idea_id():
    """T-6.1.05c: Subscribe without idea_id returns error."""
    user = await _create_user()
    app = _make_application()
    communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")

    connected, _ = await communicator.connect()
    assert connected is True

    await communicator.send_json_to({"type": "subscribe_idea"})
    response = await communicator.receive_json_from()
    assert response["type"] == "error"
    assert "Missing idea_id" in response["payload"]["message"]

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@override_settings(DEBUG=True, AUTH_BYPASS=True)
async def test_subscribe_idea_invalid_uuid():
    """T-6.1.05d: Subscribe with invalid UUID returns error."""
    user = await _create_user()
    app = _make_application()
    communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")

    connected, _ = await communicator.connect()
    assert connected is True

    await communicator.send_json_to({"type": "subscribe_idea", "idea_id": "not-a-uuid"})
    response = await communicator.receive_json_from()
    assert response["type"] == "error"
    assert "Invalid idea_id" in response["payload"]["message"]

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@override_settings(DEBUG=True, AUTH_BYPASS=True)
async def test_unsubscribe_idea():
    """T-6.1.06: Unsubscribe removes consumer from idea group."""
    user = await _create_user()
    idea = await _create_idea(owner_id=user.id)
    app = _make_application()
    communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")

    connected, _ = await communicator.connect()
    assert connected is True

    # Subscribe first
    await communicator.send_json_to({"type": "subscribe_idea", "idea_id": str(idea.id)})
    assert await communicator.receive_nothing(timeout=0.5) is True

    # Unsubscribe
    await communicator.send_json_to({"type": "unsubscribe_idea", "idea_id": str(idea.id)})
    assert await communicator.receive_nothing(timeout=0.5) is True

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@override_settings(DEBUG=True, AUTH_BYPASS=True)
async def test_unsubscribe_idea_not_subscribed():
    """T-6.1.06b: Unsubscribe from non-subscribed idea is a no-op."""
    user = await _create_user()
    app = _make_application()
    communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")

    connected, _ = await communicator.connect()
    assert connected is True

    await communicator.send_json_to({"type": "unsubscribe_idea", "idea_id": str(uuid.uuid4())})
    assert await communicator.receive_nothing(timeout=0.5) is True

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@override_settings(DEBUG=True, AUTH_BYPASS=True)
async def test_disconnect_cleans_up_groups():
    """T-6.1.06c: Disconnect automatically unsubscribes from all groups."""
    user = await _create_user()
    idea1 = await _create_idea(owner_id=user.id, title="Idea 1")
    idea2 = await _create_idea(owner_id=user.id, title="Idea 2")
    app = _make_application()
    communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")

    connected, _ = await communicator.connect()
    assert connected is True

    # Subscribe to two ideas
    await communicator.send_json_to({"type": "subscribe_idea", "idea_id": str(idea1.id)})
    assert await communicator.receive_nothing(timeout=0.5) is True
    await communicator.send_json_to({"type": "subscribe_idea", "idea_id": str(idea2.id)})
    assert await communicator.receive_nothing(timeout=0.5) is True

    # Disconnect should clean up without errors
    await communicator.disconnect()


# ---- US-003: Chat message broadcast tests ----


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@override_settings(DEBUG=True, AUTH_BYPASS=True)
async def test_chat_message_broadcast_to_subscriber():
    """T-6.4.01: chat_message group_send is forwarded to subscribed WebSocket client."""
    user = await _create_user()
    idea = await _create_idea(owner_id=user.id)
    app = _make_application()
    communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")

    connected, _ = await communicator.connect()
    assert connected is True

    # Subscribe to idea group
    await communicator.send_json_to({"type": "subscribe_idea", "idea_id": str(idea.id)})
    assert await communicator.receive_nothing(timeout=0.5) is True

    # Simulate a group_send (as the chat view would do)
    channel_layer = get_channel_layer()
    group_name = f"idea_{idea.id}"
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
        group_name,
        {
            "type": "chat_message",
            "idea_id": str(idea.id),
            "payload": payload,
        },
    )

    response = await communicator.receive_json_from(timeout=2)
    assert response["type"] == "chat_message"
    assert response["idea_id"] == str(idea.id)
    assert response["payload"]["content"] == "Hello from broadcast"
    assert response["payload"]["sender_type"] == "user"
    assert response["payload"]["sender"]["id"] == str(user.id)
    assert response["payload"]["sender"]["display_name"] == user.display_name
    assert response["payload"]["ai_agent"] is None
    assert response["payload"]["message_type"] == "regular"
    assert response["payload"]["created_at"] == "2026-03-10T12:00:00+00:00"

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@override_settings(DEBUG=True, AUTH_BYPASS=True)
async def test_chat_message_broadcast_not_received_by_unsubscribed():
    """T-6.4.01b: Unsubscribed clients do not receive chat_message broadcasts."""
    user = await _create_user()
    idea = await _create_idea(owner_id=user.id)
    app = _make_application()
    communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")

    connected, _ = await communicator.connect()
    assert connected is True

    # Do NOT subscribe — send group message
    channel_layer = get_channel_layer()
    group_name = f"idea_{idea.id}"
    await channel_layer.group_send(
        group_name,
        {
            "type": "chat_message",
            "idea_id": str(idea.id),
            "payload": {"content": "should not arrive"},
        },
    )

    assert await communicator.receive_nothing(timeout=1) is True

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@override_settings(DEBUG=True, AUTH_BYPASS=True)
async def test_chat_message_broadcast_via_view_helper():
    """T-6.4.02: _broadcast_chat_message sends chat_message to idea group after REST POST."""
    user = await _create_user()
    idea = await _create_idea(owner_id=user.id)
    app = _make_application()
    communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")

    connected, _ = await communicator.connect()
    assert connected is True

    # Subscribe to idea group
    await communicator.send_json_to({"type": "subscribe_idea", "idea_id": str(idea.id)})
    assert await communicator.receive_nothing(timeout=0.5) is True

    # Create a chat message in DB and broadcast via the view helper
    @database_sync_to_async
    def create_and_broadcast():
        from apps.chat.views import _broadcast_chat_message

        message = ChatMessage.objects.create(
            idea_id=idea.id,
            sender_type="user",
            sender_id=user.id,
            content="Integration test message",
        )
        _broadcast_chat_message(message, user)
        return message

    message = await create_and_broadcast()

    response = await communicator.receive_json_from(timeout=2)
    assert response["type"] == "chat_message"
    assert response["idea_id"] == str(idea.id)
    assert response["payload"]["id"] == str(message.id)
    assert response["payload"]["content"] == "Integration test message"
    assert response["payload"]["sender_type"] == "user"
    assert response["payload"]["sender"]["id"] == str(user.id)
    assert response["payload"]["sender"]["display_name"] == user.display_name

    await communicator.disconnect()


# ---- US-004: Board sync broadcast tests ----


@database_sync_to_async
def _create_board_node(idea_id, **kwargs):
    defaults = {
        "idea_id": idea_id,
        "node_type": "box",
        "title": "Test Node",
        "position_x": 100,
        "position_y": 200,
        "created_by": "user",
    }
    defaults.update(kwargs)
    return BoardNode.objects.create(**defaults)


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@override_settings(DEBUG=True, AUTH_BYPASS=True)
async def test_board_update_broadcast_to_subscriber():
    """T-6.4.03: board_update group_send is forwarded to subscribed WebSocket client."""
    user = await _create_user()
    idea = await _create_idea(owner_id=user.id)
    app = _make_application()
    communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")

    connected, _ = await communicator.connect()
    assert connected is True

    # Subscribe to idea group
    await communicator.send_json_to({"type": "subscribe_idea", "idea_id": str(idea.id)})
    assert await communicator.receive_nothing(timeout=0.5) is True

    # Simulate a board_update group_send
    channel_layer = get_channel_layer()
    group_name = f"idea_{idea.id}"
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
        group_name,
        {
            "type": "board_update",
            "idea_id": str(idea.id),
            "payload": payload,
        },
    )

    response = await communicator.receive_json_from(timeout=2)
    assert response["type"] == "board_update"
    assert response["idea_id"] == str(idea.id)
    assert response["payload"]["nodes_updated"] == payload["nodes_updated"]
    assert response["payload"]["source"] == "user"
    assert response["payload"]["nodes_created"] == []
    assert response["payload"]["nodes_deleted"] == []
    assert response["payload"]["connections_created"] == []
    assert response["payload"]["connections_updated"] == []
    assert response["payload"]["connections_deleted"] == []

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@override_settings(DEBUG=True, AUTH_BYPASS=True)
async def test_board_update_not_received_by_unsubscribed():
    """T-6.4.03b: Unsubscribed clients do not receive board_update broadcasts."""
    user = await _create_user()
    idea = await _create_idea(owner_id=user.id)
    app = _make_application()
    communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")

    connected, _ = await communicator.connect()
    assert connected is True

    # Do NOT subscribe — send group message
    channel_layer = get_channel_layer()
    group_name = f"idea_{idea.id}"
    await channel_layer.group_send(
        group_name,
        {
            "type": "board_update",
            "idea_id": str(idea.id),
            "payload": {"nodes_updated": [{"id": "test"}], "source": "user"},
        },
    )

    assert await communicator.receive_nothing(timeout=1) is True

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@override_settings(DEBUG=True, AUTH_BYPASS=True)
async def test_board_update_broadcast_via_view_helper():
    """T-6.4.04: _broadcast_board_update sends board_update with node data via view helper."""
    user = await _create_user()
    idea = await _create_idea(owner_id=user.id)
    app = _make_application()
    communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")

    connected, _ = await communicator.connect()
    assert connected is True

    await communicator.send_json_to({"type": "subscribe_idea", "idea_id": str(idea.id)})
    assert await communicator.receive_nothing(timeout=0.5) is True

    @database_sync_to_async
    def create_node_and_broadcast():
        from apps.board.views import _broadcast_board_update, _node_to_broadcast_dict

        node = BoardNode.objects.create(
            idea_id=idea.id,
            node_type="box",
            title="Broadcast Test",
            position_x=50,
            position_y=75,
            created_by="user",
        )
        _broadcast_board_update(
            idea.id,
            nodes_created=[_node_to_broadcast_dict(node)],
            source=node.created_by,
        )
        return node

    node = await create_node_and_broadcast()

    response = await communicator.receive_json_from(timeout=2)
    assert response["type"] == "board_update"
    assert response["idea_id"] == str(idea.id)
    assert len(response["payload"]["nodes_created"]) == 1
    assert response["payload"]["nodes_created"][0]["id"] == str(node.id)
    assert response["payload"]["nodes_created"][0]["title"] == "Broadcast Test"
    assert response["payload"]["source"] == "user"

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@override_settings(DEBUG=True, AUTH_BYPASS=True)
async def test_board_update_broadcast_node_delete():
    """T-3.6.01: board_update with nodes_deleted broadcast."""
    user = await _create_user()
    idea = await _create_idea(owner_id=user.id)
    app = _make_application()
    communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")

    connected, _ = await communicator.connect()
    assert connected is True

    await communicator.send_json_to({"type": "subscribe_idea", "idea_id": str(idea.id)})
    assert await communicator.receive_nothing(timeout=0.5) is True

    node = await _create_board_node(idea.id, title="To Delete")

    @database_sync_to_async
    def delete_and_broadcast(node_id):
        from apps.board.views import _broadcast_board_update

        _broadcast_board_update(
            idea.id,
            nodes_deleted=[str(node_id)],
            source="user",
        )

    await delete_and_broadcast(node.id)

    response = await communicator.receive_json_from(timeout=2)
    assert response["type"] == "board_update"
    assert response["idea_id"] == str(idea.id)
    assert str(node.id) in response["payload"]["nodes_deleted"]
    assert response["payload"]["source"] == "user"

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@override_settings(DEBUG=True, AUTH_BYPASS=True)
async def test_board_update_broadcast_source_ai():
    """T-3.6.02: board_update payload source is 'ai' when node created by AI."""
    user = await _create_user()
    idea = await _create_idea(owner_id=user.id)
    app = _make_application()
    communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")

    connected, _ = await communicator.connect()
    assert connected is True

    await communicator.send_json_to({"type": "subscribe_idea", "idea_id": str(idea.id)})
    assert await communicator.receive_nothing(timeout=0.5) is True

    @database_sync_to_async
    def create_ai_node_and_broadcast():
        from apps.board.views import _broadcast_board_update, _node_to_broadcast_dict

        node = BoardNode.objects.create(
            idea_id=idea.id,
            node_type="box",
            title="AI Node",
            position_x=0,
            position_y=0,
            created_by="ai",
        )
        _broadcast_board_update(
            idea.id,
            nodes_created=[_node_to_broadcast_dict(node)],
            source="ai",
        )
        return node

    await create_ai_node_and_broadcast()

    response = await communicator.receive_json_from(timeout=2)
    assert response["type"] == "board_update"
    assert response["payload"]["source"] == "ai"

    await communicator.disconnect()
