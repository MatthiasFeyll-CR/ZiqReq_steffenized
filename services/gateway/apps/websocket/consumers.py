import logging
import uuid

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

logger = logging.getLogger(__name__)


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

        await self.accept()
        logger.info("WebSocket connected: user=%s connection=%s", self.user_id, self.connection_id)

    async def disconnect(self, close_code):
        for group_name in list(getattr(self, "subscribed_groups", set())):
            try:
                await self.channel_layer.group_discard(group_name, self.channel_name)
            except Exception:
                logger.exception("Error leaving group %s on disconnect", group_name)

        user_id = getattr(self, "user_id", "unknown")
        connection_id = getattr(self, "connection_id", "unknown")
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

        await self.channel_layer.group_discard(group_name, self.channel_name)
        self.subscribed_groups.discard(group_name)
        logger.info(
            "User %s unsubscribed from %s (connection=%s)",
            self.user_id, group_name, self.connection_id,
        )

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
