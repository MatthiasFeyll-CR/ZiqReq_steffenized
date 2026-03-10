import uuid

import pytest
from channels.db import database_sync_to_async
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.test import override_settings

from apps.authentication.models import User
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
