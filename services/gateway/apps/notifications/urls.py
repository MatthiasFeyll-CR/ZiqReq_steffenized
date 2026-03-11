from django.urls import path

from . import views

urlpatterns = [
    path("notifications/", views.notification_list),
    path("notifications/unread-count", views.unread_count),
    path("notifications/mark-all-read", views.mark_all_read),
    path("notifications/<str:notification_id>", views.mark_notification),
]
