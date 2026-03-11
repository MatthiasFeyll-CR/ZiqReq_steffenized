from django.urls import include, path

from apps.collaboration import views as collab_views
from apps.review import views as review_views

from . import views

urlpatterns = [
    path("", views.ideas_root),
    path("<str:idea_id>/", views.ideas_detail),
    path("<str:idea_id>/restore", views.restore_idea),
    path("<str:idea_id>/submit", review_views.submit_idea),
    path("<str:idea_id>/chat", include("apps.chat.urls")),
    path("<str:idea_id>/board/", include("apps.board.urls")),
    path("<str:idea_id>/context-window", views.context_window),
    path("<str:idea_id>/brd", include("apps.brd.urls")),
    path("<str:idea_id>/review/accept", review_views.accept_review),
    path("<str:idea_id>/review/reject", review_views.reject_review),
    path("<str:idea_id>/review/drop", review_views.drop_review),
    path("<str:idea_id>/review/undo", review_views.undo_review),
    path("<str:idea_id>/review/timeline", review_views.review_timeline),
    path("<str:idea_id>/review/reviewers", review_views.get_idea_reviewers),
    path("<str:idea_id>/invitations", collab_views.idea_pending_invitations),
    path("<str:idea_id>/collaborators/invite", collab_views.send_invitation),
    path("<str:idea_id>/collaborators", collab_views.list_collaborators),
    path("<str:idea_id>/collaborators/<str:user_id_param>", collab_views.remove_collaborator),
    path("<str:idea_id>/transfer-ownership", collab_views.transfer_ownership),
    path("<str:idea_id>/leave", collab_views.leave_idea),
    path("<str:idea_id>/share-link", views.generate_share_link),
    path("<str:idea_id>/similar", views.get_similar_ideas),
    path("<str:idea_id>/merge-request", views.create_merge_request),
]
