import logging
import uuid

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
