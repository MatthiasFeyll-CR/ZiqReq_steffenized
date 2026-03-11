from django.urls import include, path

from apps.ideas import views as ideas_views

urlpatterns = [
    path("api/auth/", include("apps.authentication.urls")),
    path("api/ideas/", include("apps.ideas.urls")),
    path("api/", include("apps.notifications.urls")),
    path("api/", include("apps.monitoring.urls")),
    path("api/admin/", include("apps.admin_config.urls")),
    path("api/admin/", include("apps.admin_ai_context.urls")),
    path("api/reviews/", include("apps.review.urls")),
    path("api/invitations/", include("apps.collaboration.urls")),
    path("api/users/", include("apps.authentication.user_urls")),
    path("api/merge-requests/<str:merge_request_id>/consent", ideas_views.consent_merge_request),
]
