from django.urls import path

from . import views

urlpatterns = [
    path("parameters", views.parameter_list),
    path("parameters/<str:key>", views.parameter_update),
    path("projects", views.admin_projects_list),
    path("attachments", views.admin_attachments_list),
    path("attachments/<str:attachment_id>", views.admin_attachment_delete),
    path("attachments/<str:attachment_id>/restore/", views.admin_attachment_restore),
]
