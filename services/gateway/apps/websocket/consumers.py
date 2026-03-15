import asyncio
import logging
import uuid
from collections import defaultdict

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

DEFAULT_IDLE_DISCONNECT = 120  # seconds

logger = logging.getLogger(__name__)

# Server-side presence registry: group_name -> {user_id: set(channel_names)}
# Used for multi-tab dedup: a user appears once in presence even if connected from multiple tabs.
_presence_registry: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))


class IdeaConsumer(AsyncJsonWebsocketConsumer):
    """Session-level WebSocket consumer with token auth and lifecycle management.

    Auth is handled by WebSocketAuthMiddleware which populates scope["user_id"]
    and scope["user_display_name"] before the consumer is reached.
    """

    async def connect(self):
        user_id = self.scope.get("user_id")
        if not user_id:
            await self.close(code=4003)
            return

        self.user_id: str = user_id
        self.user_display_name: str = self.scope.get("user_display_name", "")
        self.connection_id: str = str(uuid.uuid4())
        self.subscribed_groups: set[str] = set()
        self._idle_disconnect_task: asyncio.Task | None = None

        await self.accept()

        # Join a user-specific group so we can deliver targeted notifications
        self.user_group = f"user_{self.user_id}"
        await self.channel_layer.group_add(self.user_group, self.channel_name)

        logger.info("WebSocket connected: user=%s connection=%s", self.user_id, self.connection_id)

    async def disconnect(self, close_code):
        self._cancel_idle_disconnect()
        user_id = getattr(self, "user_id", "unknown")
        connection_id = getattr(self, "connection_id", "unknown")

        # Leave user-specific group
        user_group = getattr(self, "user_group", None)
        if user_group:
            try:
                await self.channel_layer.group_discard(user_group, self.channel_name)
            except Exception:
                logger.exception("Error leaving user group %s on disconnect", user_group)

        for group_name in list(getattr(self, "subscribed_groups", set())):
            try:
                await self._remove_presence(group_name)
                await self.channel_layer.group_discard(group_name, self.channel_name)
            except Exception:
                logger.exception("Error leaving group %s on disconnect", group_name)

        logger.info("WebSocket disconnected: user=%s connection=%s code=%s", user_id, connection_id, close_code)

    async def receive_json(self, content, **kwargs):
        try:
            msg_type = content.get("type")
            if not msg_type:
                await self.send_json({"type": "error", "payload": {"message": "Missing message type"}})
                return

            handler = getattr(self, f"handle_{msg_type}", None)
            if handler:
                await handler(content)
            else:
                await self.send_json({"type": "error", "payload": {"message": f"Unknown message type: {msg_type}"}})
        except Exception:
            logger.exception("Unexpected error processing WebSocket message")
            try:
                await self.send_json({"type": "error", "payload": {"message": "Internal server error"}})
            except Exception:
                pass
            await self.close(code=4500)

    # ---- Channel group management (subscribe/unsubscribe) ----

    async def handle_subscribe_idea(self, content: dict) -> None:
        idea_id = content.get("idea_id")
        if not idea_id:
            await self.send_json({"type": "error", "payload": {"message": "Missing idea_id"}})
            return

        try:
            uuid.UUID(idea_id)
        except (ValueError, AttributeError):
            await self.send_json({"type": "error", "payload": {"message": "Invalid idea_id format"}})
            return

        group_name = f"idea_{idea_id}"

        if group_name in self.subscribed_groups:
            return

        has_access = await self._check_idea_access(idea_id, self.user_id)
        if not has_access:
            await self.send_json({
                "type": "error",
                "payload": {"message": "Access denied to idea"},
            })
            return

        await self.channel_layer.group_add(group_name, self.channel_name)
        self.subscribed_groups.add(group_name)

        # Add to presence registry and broadcast if this is the user's first tab on this idea
        await self._add_presence(group_name)

        logger.info(
            "User %s subscribed to %s (connection=%s)",
            self.user_id, group_name, self.connection_id,
        )

    async def handle_unsubscribe_idea(self, content: dict) -> None:
        idea_id = content.get("idea_id")
        if not idea_id:
            await self.send_json({"type": "error", "payload": {"message": "Missing idea_id"}})
            return

        group_name = f"idea_{idea_id}"

        if group_name not in self.subscribed_groups:
            return

        await self._remove_presence(group_name)
        await self.channel_layer.group_discard(group_name, self.channel_name)
        self.subscribed_groups.discard(group_name)
        logger.info(
            "User %s unsubscribed from %s (connection=%s)",
            self.user_id, group_name, self.connection_id,
        )

    # ---- Presence tracking ----

    async def handle_presence_update(self, content: dict) -> None:
        """Handle client presence_update (e.g. state='active')."""
        payload = content.get("payload", {})
        idea_id = payload.get("idea_id")
        if not idea_id:
            await self.send_json({"type": "error", "payload": {"message": "Missing idea_id in payload"}})
            return

        group_name = f"idea_{idea_id}"
        if group_name not in self.subscribed_groups:
            await self.send_json({"type": "error", "payload": {"message": "Not subscribed to idea"}})
            return

        state = payload.get("state", "active")

        # Manage idle disconnect timer
        if state == "idle":
            self._start_idle_disconnect()
        else:
            self._cancel_idle_disconnect()

        # Broadcast presence update to idea group
        await self.channel_layer.group_send(
            group_name,
            {
                "type": "presence_update",
                "idea_id": idea_id,
                "payload": {
                    "user": {
                        "id": self.user_id,
                        "display_name": self.user_display_name,
                    },
                    "state": "online" if state == "active" else state,
                },
            },
        )

    async def _add_presence(self, group_name: str) -> None:
        """Add this channel to presence registry and broadcast online if first tab."""
        registry = _presence_registry[group_name]
        was_present = len(registry.get(self.user_id, set())) > 0
        registry[self.user_id].add(self.channel_name)

        if not was_present:
            idea_id = group_name.removeprefix("idea_")
            await self.channel_layer.group_send(
                group_name,
                {
                    "type": "presence_update",
                    "idea_id": idea_id,
                    "payload": {
                        "user": {
                            "id": self.user_id,
                            "display_name": self.user_display_name,
                        },
                        "state": "online",
                    },
                },
            )

    async def _remove_presence(self, group_name: str) -> None:
        """Remove this channel from presence registry and broadcast offline if last tab."""
        registry = _presence_registry[group_name]
        channels = registry.get(self.user_id, set())
        channels.discard(self.channel_name)

        if not channels:
            # Last tab for this user — remove from registry and broadcast offline
            registry.pop(self.user_id, None)
            if not registry:
                _presence_registry.pop(group_name, None)

            idea_id = group_name.removeprefix("idea_")
            try:
                await self.channel_layer.group_send(
                    group_name,
                    {
                        "type": "presence_update",
                        "idea_id": idea_id,
                        "payload": {
                            "user": {
                                "id": self.user_id,
                                "display_name": self.user_display_name,
                            },
                            "state": "offline",
                        },
                    },
                )
            except Exception:
                logger.exception("Error broadcasting offline presence for user=%s group=%s", self.user_id, group_name)

    # ---- Board awareness (ephemeral, no persistence) ----

    async def handle_board_selection(self, content: dict) -> None:
        """Broadcast node selection/deselection to idea group (excluding sender)."""
        idea_id = content.get("idea_id")
        if not idea_id:
            await self.send_json({"type": "error", "payload": {"message": "Missing idea_id"}})
            return

        group_name = f"idea_{idea_id}"
        if group_name not in self.subscribed_groups:
            await self.send_json({"type": "error", "payload": {"message": "Not subscribed to idea"}})
            return

        payload = content.get("payload", {})
        await self.channel_layer.group_send(
            group_name,
            {
                "type": "board_selection",
                "idea_id": idea_id,
                "payload": {
                    "node_id": payload.get("node_id"),
                    "user": {
                        "id": self.user_id,
                        "display_name": self.user_display_name,
                    },
                },
                "sender_channel": self.channel_name,
            },
        )

    # ---- Group message handlers (forwarded to WebSocket clients) ----

    async def chat_message(self, event: dict) -> None:
        """Forward chat.message.created group_send to the WebSocket client."""
        await self.send_json({
            "type": "chat_message",
            "idea_id": event["idea_id"],
            "payload": event["payload"],
        })

    async def board_update(self, event: dict) -> None:
        """Forward board_update group_send to the WebSocket client."""
        await self.send_json({
            "type": "board_update",
            "idea_id": event["idea_id"],
            "payload": event["payload"],
        })

    async def board_selection(self, event: dict) -> None:
        """Forward board_selection to all subscribers except the sender."""
        if event.get("sender_channel") == self.channel_name:
            return
        await self.send_json({
            "type": "board_selection",
            "idea_id": event["idea_id"],
            "payload": event["payload"],
        })

    async def board_lock_change(self, event: dict) -> None:
        """Forward board_lock_change group_send to the WebSocket client."""
        await self.send_json({
            "type": "board_lock_change",
            "idea_id": event["idea_id"],
            "payload": event["payload"],
        })

    async def presence_update(self, event: dict) -> None:
        """Forward presence_update group_send to the WebSocket client."""
        await self.send_json({
            "type": "presence_update",
            "idea_id": event["idea_id"],
            "payload": event["payload"],
        })

    async def ai_reaction(self, event: dict) -> None:
        """Forward ai_reaction group_send to the WebSocket client."""
        await self.send_json({
            "type": "ai_reaction",
            "idea_id": event["idea_id"],
            "payload": event["payload"],
        })

    async def title_update(self, event: dict) -> None:
        """Forward title_update group_send to the WebSocket client."""
        await self.send_json({
            "type": "title_update",
            "idea_id": event["idea_id"],
            "payload": event["payload"],
        })

    async def ai_processing(self, event: dict) -> None:
        """Forward ai_processing group_send to the WebSocket client."""
        await self.send_json({
            "type": "ai_processing",
            "idea_id": event["idea_id"],
            "payload": event["payload"],
        })

    async def rate_limit(self, event: dict) -> None:
        """Forward rate_limit group_send to the WebSocket client."""
        await self.send_json({
            "type": "rate_limit",
            "idea_id": event["idea_id"],
            "payload": event["payload"],
        })

    async def notification(self, event: dict) -> None:
        """Forward notification group_send to the WebSocket client."""
        await self.send_json({
            "type": "notification",
            "payload": event["payload"],
        })

    async def merge_request(self, event: dict) -> None:
        """Forward merge_request group_send to the WebSocket client."""
        await self.send_json({
            "type": "merge_request",
            "payload": event["payload"],
        })

    async def merge_complete(self, event: dict) -> None:
        """Forward merge_complete group_send to the WebSocket client."""
        await self.send_json({
            "type": "merge_complete",
            "payload": event["payload"],
        })

    async def append_complete(self, event: dict) -> None:
        """Forward append_complete group_send to the WebSocket client."""
        await self.send_json({
            "type": "append_complete",
            "payload": event["payload"],
        })

    async def brd_ready(self, event: dict) -> None:
        """Forward brd_ready group_send to the WebSocket client."""
        await self.send_json({
            "type": "brd_ready",
            "idea_id": event["idea_id"],
            "payload": event["payload"],
        })

    # ---- Idle disconnect timer ----

    def _start_idle_disconnect(self) -> None:
        """Start (or restart) the idle disconnect timer."""
        self._cancel_idle_disconnect()
        idle_disconnect = self._get_idle_disconnect_seconds()
        self._idle_disconnect_task = asyncio.ensure_future(
            self._idle_disconnect_countdown(idle_disconnect)
        )

    def _cancel_idle_disconnect(self) -> None:
        """Cancel the idle disconnect timer if running."""
        task = getattr(self, "_idle_disconnect_task", None)
        if task is not None and not task.done():
            task.cancel()
        self._idle_disconnect_task = None

    async def _idle_disconnect_countdown(self, seconds: int) -> None:
        """Wait for the given duration, then close the WebSocket."""
        try:
            await asyncio.sleep(seconds)
            logger.info(
                "Idle disconnect: user=%s connection=%s after %ds idle",
                self.user_id, self.connection_id, seconds,
            )
            await self.close(code=4008)
        except asyncio.CancelledError:
            pass

    @staticmethod
    def _get_idle_disconnect_seconds() -> int:
        try:
            from apps.admin_config.services import get_parameter
            return get_parameter("idle_disconnect", default=DEFAULT_IDLE_DISCONNECT, cast=int)
        except Exception:
            return DEFAULT_IDLE_DISCONNECT

    @database_sync_to_async
    def _check_idea_access(self, idea_id: str, user_id: str) -> bool:
        from apps.ideas.models import Idea, IdeaCollaborator

        try:
            idea = Idea.objects.filter(id=idea_id, deleted_at__isnull=True).first()
            if idea is None:
                return False

            if str(idea.owner_id) == user_id:
                return True
            if idea.co_owner_id and str(idea.co_owner_id) == user_id:
                return True

            return IdeaCollaborator.objects.filter(idea_id=idea_id, user_id=user_id).exists()
        except Exception:
            logger.exception("Error checking idea access for user=%s idea=%s", user_id, idea_id)
            return False
