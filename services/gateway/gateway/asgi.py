import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gateway.settings.development")

django_asgi_app = get_asgi_application()

from apps.websocket.middleware import WebSocketAuthMiddleware  # noqa: E402
from apps.websocket.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": WebSocketAuthMiddleware(URLRouter(websocket_urlpatterns)),
    }
)
