from django.urls import path

from . import views

urlpatterns = [
    path("", views.invitations_list),
    path("<str:invitation_id>/accept", views.accept_invitation),
    path("<str:invitation_id>/decline", views.decline_invitation),
    path("<str:invitation_id>/revoke", views.revoke_invitation),
]
