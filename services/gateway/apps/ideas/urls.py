from django.urls import path

from . import views

urlpatterns = [
    path("", views.ideas_root),
    path("<str:idea_id>", views.ideas_detail),
    path("<str:idea_id>/restore", views.restore_idea),
]
