from django.urls import include, path

from apps.review import views as review_views

from . import views

urlpatterns = [
    path("", views.ideas_root),
    path("<str:idea_id>", views.ideas_detail),
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
]
