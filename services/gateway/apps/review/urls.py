from django.urls import path

from . import views

urlpatterns = [
    path("<str:idea_id>/assign", views.assign_review),
    path("<str:idea_id>/unassign", views.unassign_review),
]
