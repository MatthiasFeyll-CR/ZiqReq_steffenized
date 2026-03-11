from django.urls import path

from . import views

urlpatterns = [
    path("search", views.search_users),
    path(
        "me/notification-preferences",
        views.notification_preferences,
        name="notification-preferences",
    ),
]
