from django.urls import include, path

from apps.collaboration import views as collab_views
from apps.review import views as review_views

from . import requirements_views, views

urlpatterns = [
    path("", views.projects_root),
    path("<str:project_id>/", views.projects_detail),
    path("<str:project_id>/restore", views.restore_project),
    path("<str:project_id>/submit", review_views.submit_project),
    path("<str:project_id>/chat/", include("apps.chat.urls")),
    path("<str:project_id>/context-window", views.context_window),
    path("<str:project_id>/brd/", include("apps.requirements_document.urls")),
    # Requirements endpoints (US-002)
    path("<str:project_id>/requirements/", requirements_views.requirements_root),
    path("<str:project_id>/requirements/items", requirements_views.requirements_items),
    path("<str:project_id>/requirements/items/<str:item_id>", requirements_views.requirements_item_detail),
    path("<str:project_id>/requirements/items/<str:item_id>/children", requirements_views.requirements_children),
    path("<str:project_id>/requirements/items/<str:item_id>/children/<str:child_id>", requirements_views.requirements_child_detail),
    path("<str:project_id>/requirements/reorder", requirements_views.requirements_reorder),
    path("<str:project_id>/requirements/generate", requirements_views.requirements_generate),
    path("<str:project_id>/review/accept", review_views.accept_review),
    path("<str:project_id>/review/reject", review_views.reject_review),
    path("<str:project_id>/review/drop", review_views.drop_review),
    path("<str:project_id>/review/undo", review_views.undo_review),
    path("<str:project_id>/review/timeline", review_views.review_timeline),
    path("<str:project_id>/review/reviewers", review_views.get_project_reviewers),
    path("<str:project_id>/invitations", collab_views.project_pending_invitations),
    path("<str:project_id>/collaborators/invite", collab_views.send_invitation),
    path("<str:project_id>/collaborators", collab_views.list_collaborators),
    path("<str:project_id>/collaborators/<str:user_id_param>", collab_views.remove_collaborator),
    path("<str:project_id>/transfer-ownership", collab_views.transfer_ownership),
    path("<str:project_id>/leave", collab_views.leave_project),
    path("<str:project_id>/share-link", views.generate_share_link),
    path("<str:project_id>/comments/", include("apps.comments.urls")),
]
