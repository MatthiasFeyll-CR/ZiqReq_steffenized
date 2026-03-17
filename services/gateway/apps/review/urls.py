from django.urls import path

from . import views

urlpatterns = [
    path("", views.list_reviews),
    path("reviewers", views.list_reviewer_users),
    path("<str:project_id>/assign", views.assign_review),
    path("<str:project_id>/unassign", views.unassign_review),
]
