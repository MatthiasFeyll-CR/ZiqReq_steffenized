from django.urls import path

from . import views

urlpatterns = [
    path("", views.chat_messages),
    path("<str:message_id>/reactions", views.message_reactions),
]
