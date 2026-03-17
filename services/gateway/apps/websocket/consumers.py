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


class ProjectConsumer(AsyncJsonWebsocketConsumer):
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

    async def handle_subscribe_project(self, content: dict) -> None:
        project_id = content.get("project_id")
        if not project_id:
            await self.send_json({"type": "error", "payload": {"message": "Missing project_id"}})
            return

        try:
            uuid.UUID(project_id)
        except (ValueError, AttributeError):
            await self.send_json({"type": "error", "payload": {"message": "Invalid project_id format"}})
            return

        group_name = f"project_{project_id}"

        if group_name in self.subscribed_groups:
            return

        has_access = await self._check_project_access(project_id, self.user_id)
        if not has_access:
            await self.send_json({
                "type": "error",
                "payload": {"message": "Access denied to project"},
            })
            return

        await self.channel_layer.group_add(group_name, self.channel_name)
        self.subscribed_groups.add(group_name)

        # Add to presence registry and broadcast if this is the user's first tab on this project
        await self._add_presence(group_name)

        logger.info(
            "User %s subscribed to %s (connection=%s)",
            self.user_id, group_name, self.connection_id,
        )

    async def handle_unsubscribe_project(self, content: dict) -> None:
        project_id = content.get("project_id")
        if not project_id:
            await self.send_json({"type": "error", "payload": {"message": "Missing project_id"}})
            return

        group_name = f"project_{project_id}"

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
        project_id = payload.get("project_id")
        if not project_id:
            await self.send_json({"type": "error", "payload": {"message": "Missing project_id in payload"}})
            return

        group_name = f"project_{project_id}"
        if group_name not in self.subscribed_groups:
            await self.send_json({"type": "error", "payload": {"message": "Not subscribed to project"}})
            return

        state = payload.get("state", "active")

        # Manage idle disconnect timer
        if state == "idle":
            self._start_idle_disconnect()
        else:
            self._cancel_idle_disconnect()

        # Broadcast presence update to project group
        await self.channel_layer.group_send(
            group_name,
            {
                "type": "presence_update",
                "project_id": project_id,
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
            project_id = group_name.removeprefix("project_")
            await self.channel_layer.group_send(
                group_name,
                {
                    "type": "presence_update",
                    "project_id": project_id,
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

            project_id = group_name.removeprefix("project_")
            try:
                await self.channel_layer.group_send(
                    group_name,
                    {
                        "type": "presence_update",
                        "project_id": project_id,
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

    # ---- Group message handlers (forwarded to WebSocket clients) ----

    async def chat_message(self, event: dict) -> None:
        """Forward chat.message.created group_send to the WebSocket client."""
        await self.send_json({
            "type": "chat_message",
            "project_id": event["project_id"],
            "payload": event["payload"],
        })

    async def presence_update(self, event: dict) -> None:
        """Forward presence_update group_send to the WebSocket client."""
        await self.send_json({
            "type": "presence_update",
            "project_id": event["project_id"],
            "payload": event["payload"],
        })

    async def ai_reaction(self, event: dict) -> None:
        """Forward ai_reaction group_send to the WebSocket client."""
        await self.send_json({
            "type": "ai_reaction",
            "project_id": event["project_id"],
            "payload": event["payload"],
        })

    async def title_update(self, event: dict) -> None:
        """Forward title_update group_send to the WebSocket client."""
        await self.send_json({
            "type": "title_update",
            "project_id": event["project_id"],
            "payload": event["payload"],
        })

    async def ai_processing(self, event: dict) -> None:
        """Forward ai_processing group_send to the WebSocket client."""
        await self.send_json({
            "type": "ai_processing",
            "project_id": event["project_id"],
            "payload": event["payload"],
        })

    async def rate_limit(self, event: dict) -> None:
        """Forward rate_limit group_send to the WebSocket client."""
        await self.send_json({
            "type": "rate_limit",
            "project_id": event["project_id"],
            "payload": event["payload"],
        })

    async def notification(self, event: dict) -> None:
        """Forward notification group_send to the WebSocket client."""
        await self.send_json({
            "type": "notification",
            "payload": event["payload"],
        })

    async def brd_generating(self, event: dict) -> None:
        """Forward brd_generating group_send to the WebSocket client."""
        await self.send_json({
            "type": "brd_generating",
            "project_id": event["project_id"],
            "payload": event["payload"],
        })

    async def brd_ready(self, event: dict) -> None:
        """Forward brd_ready group_send to the WebSocket client."""
        await self.send_json({
            "type": "brd_ready",
            "project_id": event["project_id"],
            "payload": event["payload"],
        })

    async def requirements_updated(self, event: dict) -> None:
        """Forward requirements_updated group_send to the WebSocket client."""
        await self.send_json({
            "type": "requirements_updated",
            "project_id": event["project_id"],
            "payload": event["payload"],
        })

    async def requirements_generating(self, event: dict) -> None:
        """Forward requirements_generating group_send to the WebSocket client."""
        await self.send_json({
            "type": "requirements_generating",
            "project_id": event["project_id"],
            "payload": event["payload"],
        })

    async def requirements_ready(self, event: dict) -> None:
        """Forward requirements_ready group_send to the WebSocket client."""
        await self.send_json({
            "type": "requirements_ready",
            "project_id": event["project_id"],
            "payload": event["payload"],
        })

    async def comment_created(self, event: dict) -> None:
        """Forward comment_created group_send to the WebSocket client."""
        await self.send_json({
            "type": "comment_created",
            "payload": event["payload"],
        })

    async def comment_updated(self, event: dict) -> None:
        """Forward comment_updated group_send to the WebSocket client."""
        await self.send_json({
            "type": "comment_updated",
            "payload": event["payload"],
        })

    async def comment_deleted(self, event: dict) -> None:
        """Forward comment_deleted group_send to the WebSocket client."""
        await self.send_json({
            "type": "comment_deleted",
            "payload": event["payload"],
        })

    async def comment_reaction(self, event: dict) -> None:
        """Forward comment_reaction group_send to the WebSocket client."""
        await self.send_json({
            "type": "comment_reaction",
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
    def _check_project_access(self, project_id: str, user_id: str) -> bool:
        from apps.projects.models import Project, ProjectCollaborator

        try:
            project = Project.objects.filter(id=project_id, deleted_at__isnull=True).first()
            if project is None:
                return False

            if str(project.owner_id) == user_id:
                return True

            return ProjectCollaborator.objects.filter(project_id=project_id, user_id=user_id).exists()
        except Exception:
            logger.exception("Error checking project access for user=%s project=%s", user_id, project_id)
            return False
