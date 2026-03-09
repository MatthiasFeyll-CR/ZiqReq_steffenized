import logging
from urllib.parse import parse_qs, urlparse

import jwt
from django.conf import settings
from django.http import JsonResponse

from .azure_ad import extract_user_data, validate_azure_ad_token
from .models import User

logger = logging.getLogger(__name__)

AUTH_EXEMPT_PATHS = [
    "/api/auth/validate",
    "/api/auth/dev-users",
    "/api/auth/dev-login",
    "/api/auth/dev-switch",
]


class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.rstrip("/")

        if any(path == exempt.rstrip("/") for exempt in AUTH_EXEMPT_PATHS):
            return self.get_response(request)

        if self._is_dev_bypass_enabled():
            user = self._authenticate_dev_session(request)
        elif self._is_websocket(request):
            user = self._authenticate_websocket(request)
        else:
            user = self._authenticate_bearer(request)

        if user is None and not self._is_dev_bypass_enabled():
            return JsonResponse(
                {"error": "UNAUTHORIZED", "message": "Authentication required"},
                status=401,
            )

        request.user_obj = user  # type: ignore[attr-defined]
        return self.get_response(request)

    def _is_dev_bypass_enabled(self) -> bool:
        return bool(getattr(settings, "DEBUG", False) and getattr(settings, "AUTH_BYPASS", False))

    def _is_websocket(self, request) -> bool:
        return request.path.startswith("/ws/")

    def _authenticate_dev_session(self, request) -> User | None:
        user_id = request.session.get("user_id") if hasattr(request, "session") else None
        if not user_id:
            return None
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def _authenticate_bearer(self, request) -> User | None:
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return None

        token = auth_header[7:]
        try:
            claims = validate_azure_ad_token(token)
            user_data = extract_user_data(claims)
            user = User.objects.filter(id=user_data["id"]).first()
            return user
        except (jwt.InvalidTokenError, Exception) as exc:
            logger.debug("Bearer token validation failed: %s", exc)
            return None

    def _authenticate_websocket(self, request) -> User | None:
        query_string = request.META.get("QUERY_STRING", "")
        if not query_string:
            full_path = request.get_full_path()
            parsed = urlparse(full_path)
            query_string = parsed.query

        params = parse_qs(query_string)
        token_list = params.get("token", [])
        if not token_list:
            return None

        token = token_list[0]
        try:
            claims = validate_azure_ad_token(token)
            user_data = extract_user_data(claims)
            user = User.objects.filter(id=user_data["id"]).first()
            return user
        except (jwt.InvalidTokenError, Exception) as exc:
            logger.debug("WebSocket token validation failed: %s", exc)
            return None
