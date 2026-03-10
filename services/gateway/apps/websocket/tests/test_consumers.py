import uuid

import pytest
from channels.db import database_sync_to_async
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.test import override_settings

from apps.authentication.models import User
from apps.ideas.models import Idea, IdeaCollaborator
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
