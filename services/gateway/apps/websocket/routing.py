from django.urls import path

from .consumers import IdeaConsumer

websocket_urlpatterns = [
    path("ws/", IdeaConsumer.as_asgi()),
]
