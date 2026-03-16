from django.urls import path

from . import views

urlpatterns = [
    path("", views.comments_root),
    path("mark-read", views.mark_comments_read),
    path("unread-count", views.unread_comment_count),
    path("<str:comment_id>/", views.comment_detail),
    path("<str:comment_id>/react", views.comment_reaction),
]
