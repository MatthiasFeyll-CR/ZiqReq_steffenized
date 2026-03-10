import logging
import uuid
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.conf import settings

logger = logging.getLogger(__name__)


class WebSocketAuthMiddleware:
    """ASGI middleware that validates JWT token from query string on WebSocket handshake.

    Populates scope["user_id"], scope["user_display_name"] on success.
    Rejects the connection (closes with 403) if the token is invalid/missing/expired.
    In dev bypass mode (DEBUG + AUTH_BYPASS), accepts the user_id from token as-is.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "websocket":
            return await self.app(scope, receive, send)

        query_string = scope.get("query_string", b"").decode("utf-8")
        params = parse_qs(query_string)
        token_list = params.get("token", [])

        if not token_list:
            await self._reject(send)
            return

        token = token_list[0]
        user = await self._authenticate(token)

        if user is None:
            await self._reject(send)
            return

        scope["user_id"] = str(user.id)
        scope["user_display_name"] = user.display_name
        return await self.app(scope, receive, send)

    async def _authenticate(self, token: str):
        if self._is_dev_bypass_enabled():
            return await self._authenticate_dev(token)
        return await self._authenticate_azure(token)

    def _is_dev_bypass_enabled(self) -> bool:
        return bool(getattr(settings, "DEBUG", False) and getattr(settings, "AUTH_BYPASS", False))

    @database_sync_to_async
    def _authenticate_dev(self, token: str):
        from apps.authentication.models import User

        try:
            user_uuid = uuid.UUID(token)
            return User.objects.filter(id=user_uuid).first()
        except (ValueError, Exception):
            return None

    @database_sync_to_async
    def _authenticate_azure(self, token: str):
        import jwt as pyjwt

        from apps.authentication.azure_ad import extract_user_data, validate_azure_ad_token
        from apps.authentication.models import User

        try:
            claims = validate_azure_ad_token(token)
            user_data = extract_user_data(claims)
            return User.objects.filter(id=user_data["id"]).first()
        except (pyjwt.InvalidTokenError, Exception) as exc:
            logger.debug("WebSocket token validation failed: %s", exc)
            return None

    @staticmethod
    async def _reject(send):
        """Reject the WebSocket handshake with a 403 close code."""
        await send({"type": "websocket.close", "code": 4003})
