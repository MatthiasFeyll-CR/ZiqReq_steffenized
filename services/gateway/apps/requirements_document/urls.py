from django.urls import path

from . import views

urlpatterns = [
    path("", views.requirements_document_draft),
    path("generate", views.requirements_generate),
    path("pdf/preview", views.requirements_preview_pdf),
]
