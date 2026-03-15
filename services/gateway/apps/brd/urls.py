from django.urls import path

from . import views

urlpatterns = [
    path("", views.brd_draft),
    path("generate", views.brd_generate),
    path("preview-pdf", views.brd_preview_pdf),
    path("versions/<str:version>/pdf", views.brd_version_pdf),
]
