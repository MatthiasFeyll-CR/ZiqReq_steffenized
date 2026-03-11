from django.urls import path

from . import views

urlpatterns = [
    path("", views.list_reviews),
    path("reviewers", views.list_reviewer_users),
    path("<str:idea_id>/assign", views.assign_review),
    path("<str:idea_id>/unassign", views.unassign_review),
]
