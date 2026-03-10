# Test Results: pre-QA M6 cycle 1
Date: 2026-03-10T13:18:47+0100
Command: docker compose -f docker-compose.test.yml run --rm python-tests pytest
Exit code: 1
Result: FAIL

## Output
```
============================= test session starts ==============================
platform linux -- Python 3.12.12, pytest-8.4.2, pluggy-1.6.0
django: version: 5.2.12, settings: gateway.settings.test (from env)
rootdir: /app
configfile: pyproject.toml
plugins: django-4.12.0, cov-5.0.0, asyncio-0.26.0
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 142 items

services/gateway/apps/authentication/tests/test_azure_ad.py ......       [  4%]
services/gateway/apps/authentication/tests/test_dev_bypass.py .......    [  9%]
services/gateway/apps/board/tests/test_views.py ........................ [ 26%]
.......................                                                  [ 42%]
services/gateway/apps/chat/tests/test_chat_messages.py ...............   [ 52%]
services/gateway/apps/chat/tests/test_reactions.py ............          [ 61%]
services/gateway/apps/collaboration/tests/test_views.py .....            [ 64%]
services/gateway/apps/ideas/tests/test_views.py .................        [ 76%]
services/gateway/apps/websocket/tests/test_consumers.py F........F...F.F [ 88%]
F.F.........FF..                                                         [ 99%]
tests/test_smoke.py .                                                    [100%]

=================================== FAILURES ===================================
_________________________ test_connection_valid_token __________________________

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    @override_settings(DEBUG=True, AUTH_BYPASS=True)
    async def test_connection_valid_token():
        """T-6.1.01: WebSocket connection with valid token succeeds."""
        user = await _create_user()
        app = _make_application()
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
    
        connected, _ = await communicator.connect()
>       assert connected is True
E       assert False is True

services/gateway/apps/websocket/tests/test_consumers.py:118: AssertionError
______________________ test_subscribe_idea_access_denied _______________________

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    @override_settings(DEBUG=True, AUTH_BYPASS=True)
    async def test_subscribe_idea_access_denied():
        """T-6.1.05: Non-member cannot subscribe to idea group."""
        stranger = await _create_user(display_name="Stranger")
        owner, idea = await _setup_user_and_idea(user_kwargs={"display_name": "Owner"})
        app = _make_application()
        communicator = WebsocketCommunicator(app, f"/ws/?token={stranger.id}")
    
        connected, _ = await communicator.connect()
>       assert connected is True
E       assert False is True

services/gateway/apps/websocket/tests/test_consumers.py:271: AssertionError
____________________________ test_unsubscribe_idea _____________________________

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    @override_settings(DEBUG=True, AUTH_BYPASS=True)
    async def test_unsubscribe_idea():
        """T-6.1.06: Unsubscribe removes consumer from idea group."""
        user, idea = await _setup_user_and_idea()
        app = _make_application()
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
    
        connected, _ = await communicator.connect()
        assert connected is True
    
        # Subscribe first
>       await _subscribe_and_drain(communicator, str(idea.id))

services/gateway/apps/websocket/tests/test_consumers.py:355: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

communicator = <channels.testing.websocket.WebsocketCommunicator object at 0x73a5ea5f5ca0>
idea_id = '5587d91b-baf8-499b-b199-c82a5ca5e727'

    async def _subscribe_and_drain(communicator, idea_id: str) -> None:
        """Subscribe to idea and drain the resulting presence_update message."""
        await communicator.send_json_to({"type": "subscribe_idea", "idea_id": idea_id})
        # Drain the presence_update broadcast
        resp = await communicator.receive_json_from(timeout=2)
>       assert resp["type"] == "presence_update"
E       AssertionError: assert 'error' == 'presence_update'
E         
E         - presence_update
E         + error

services/gateway/apps/websocket/tests/test_consumers.py:35: AssertionError
_______________________ test_disconnect_cleans_up_groups _______________________

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    @override_settings(DEBUG=True, AUTH_BYPASS=True)
    async def test_disconnect_cleans_up_groups():
        """T-6.1.06c: Disconnect automatically unsubscribes from all groups."""
    
        @database_sync_to_async
        def _setup():
            user = _make_user()
            idea1 = Idea.objects.create(id=uuid.uuid4(), title="Idea 1", owner_id=user.id)
            idea2 = Idea.objects.create(id=uuid.uuid4(), title="Idea 2", owner_id=user.id)
            return user, idea1, idea2
    
        user, idea1, idea2 = await _setup()
        app = _make_application()
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
    
        connected, _ = await communicator.connect()
        assert connected is True
    
        # Subscribe to two ideas
        await _subscribe_and_drain(communicator, str(idea1.id))
>       await _subscribe_and_drain(communicator, str(idea2.id))

services/gateway/apps/websocket/tests/test_consumers.py:406: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

communicator = <channels.testing.websocket.WebsocketCommunicator object at 0x73a5ea4c75f0>
idea_id = '52a8db0f-f520-4b9a-84e3-524dda8b00c1'

    async def _subscribe_and_drain(communicator, idea_id: str) -> None:
        """Subscribe to idea and drain the resulting presence_update message."""
        await communicator.send_json_to({"type": "subscribe_idea", "idea_id": idea_id})
        # Drain the presence_update broadcast
        resp = await communicator.receive_json_from(timeout=2)
>       assert resp["type"] == "presence_update"
E       AssertionError: assert 'error' == 'presence_update'
E         
E         - presence_update
E         + error

services/gateway/apps/websocket/tests/test_consumers.py:35: AssertionError
__________________ test_chat_message_broadcast_to_subscriber ___________________

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    @override_settings(DEBUG=True, AUTH_BYPASS=True)
    async def test_chat_message_broadcast_to_subscriber():
        """T-6.4.01: chat_message group_send is forwarded to subscribed WebSocket client."""
        user, idea = await _setup_user_and_idea()
        app = _make_application()
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
    
        connected, _ = await communicator.connect()
        assert connected is True
    
        # Subscribe to idea group
>       await _subscribe_and_drain(communicator, str(idea.id))

services/gateway/apps/websocket/tests/test_consumers.py:428: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

communicator = <channels.testing.websocket.WebsocketCommunicator object at 0x73a5ea5f5bb0>
idea_id = '6893c57f-c8e0-4687-9730-2de0fc0c61e9'

    async def _subscribe_and_drain(communicator, idea_id: str) -> None:
        """Subscribe to idea and drain the resulting presence_update message."""
        await communicator.send_json_to({"type": "subscribe_idea", "idea_id": idea_id})
        # Drain the presence_update broadcast
        resp = await communicator.receive_json_from(timeout=2)
>       assert resp["type"] == "presence_update"
E       AssertionError: assert 'error' == 'presence_update'
E         
E         - presence_update
E         + error

services/gateway/apps/websocket/tests/test_consumers.py:35: AssertionError
_________________ test_chat_message_broadcast_via_view_helper __________________

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    @override_settings(DEBUG=True, AUTH_BYPASS=True)
    async def test_chat_message_broadcast_via_view_helper():
        """T-6.4.02: _broadcast_chat_message sends chat_message to idea group after REST POST."""
        user, idea = await _setup_user_and_idea()
        app = _make_application()
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
    
        connected, _ = await communicator.connect()
>       assert connected is True
E       assert False is True

services/gateway/apps/websocket/tests/test_consumers.py:504: AssertionError
_____________________ test_presence_broadcast_on_subscribe _____________________

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    @override_settings(DEBUG=True, AUTH_BYPASS=True)
    async def test_presence_broadcast_on_subscribe():
        """T-6.3.01: Subscribe to idea broadcasts presence_update 'online' to all subscribers."""
        owner, other, idea = await _setup_owner_collaborator_idea(
            owner_kwargs={"display_name": "Owner"},
            collab_kwargs={"display_name": "Other"},
        )
        app = _make_application()
    
        # First user subscribes
        comm1 = WebsocketCommunicator(app, f"/ws/?token={owner.id}")
        connected1, _ = await comm1.connect()
        assert connected1
        await comm1.send_json_to({"type": "subscribe_idea", "idea_id": str(idea.id)})
        # Owner gets their own presence broadcast
        resp1 = await comm1.receive_json_from(timeout=2)
        assert resp1["type"] == "presence_update"
        assert resp1["payload"]["user"]["id"] == str(owner.id)
        assert resp1["payload"]["state"] == "online"
    
        # Second user subscribes
        comm2 = WebsocketCommunicator(app, f"/ws/?token={other.id}")
        connected2, _ = await comm2.connect()
>       assert connected2
E       assert False

services/gateway/apps/websocket/tests/test_consumers.py:923: AssertionError
________________________ test_presence_multi_tab_dedup _________________________

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    @override_settings(DEBUG=True, AUTH_BYPASS=True)
    async def test_presence_multi_tab_dedup():
        """T-6.3.02: Same user in 2 tabs shows single presence, offline only after both disconnect."""
        user, other, idea = await _setup_owner_collaborator_idea(
            owner_kwargs={"display_name": "MultiTab User"},
            collab_kwargs={"display_name": "Observer"},
        )
        app = _make_application()
    
        # Observer subscribes
        comm_observer = WebsocketCommunicator(app, f"/ws/?token={other.id}")
        connected_obs, _ = await comm_observer.connect()
        assert connected_obs
        await comm_observer.send_json_to({"type": "subscribe_idea", "idea_id": str(idea.id)})
        # Receive observer's own presence
        resp = await comm_observer.receive_json_from(timeout=2)
>       assert resp["payload"]["user"]["id"] == str(other.id)
               ^^^^^^^^^^^^^^^^^^^^^^^
E       KeyError: 'user'

services/gateway/apps/websocket/tests/test_consumers.py:959: KeyError
=========================== short test summary info ============================
FAILED services/gateway/apps/websocket/tests/test_consumers.py::test_connection_valid_token
FAILED services/gateway/apps/websocket/tests/test_consumers.py::test_subscribe_idea_access_denied
FAILED services/gateway/apps/websocket/tests/test_consumers.py::test_unsubscribe_idea
FAILED services/gateway/apps/websocket/tests/test_consumers.py::test_disconnect_cleans_up_groups
FAILED services/gateway/apps/websocket/tests/test_consumers.py::test_chat_message_broadcast_to_subscriber
FAILED services/gateway/apps/websocket/tests/test_consumers.py::test_chat_message_broadcast_via_view_helper
FAILED services/gateway/apps/websocket/tests/test_consumers.py::test_presence_broadcast_on_subscribe
FAILED services/gateway/apps/websocket/tests/test_consumers.py::test_presence_multi_tab_dedup
======================== 8 failed, 134 passed in 34.80s ========================

```
