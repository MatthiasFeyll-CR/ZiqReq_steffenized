from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.ideas_root),
    path("<str:idea_id>", views.ideas_detail),
    path("<str:idea_id>/restore", views.restore_idea),
    path("<str:idea_id>/chat", include("apps.chat.urls")),
]
