from django.urls import path

from . import views

urlpatterns = [
    path("", views.brd_draft),
    path("/generate", views.brd_generate),
]
