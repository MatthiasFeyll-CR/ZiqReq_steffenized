from django.urls import path

from . import views

urlpatterns = [
    path("", views.attachment_list),
    path("<str:attachment_id>/", views.attachment_delete),
    path("<str:attachment_id>/url/", views.attachment_url),
]
