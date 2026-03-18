from django.urls import path

from . import views

urlpatterns = [
    path("", views.attachment_list),
    path("<str:attachment_id>/url/", views.attachment_url),
    path("<str:attachment_id>/download/", views.attachment_download),
    path("<str:attachment_id>/restore/", views.attachment_restore),
    path("<str:attachment_id>/", views.attachment_delete),
]
