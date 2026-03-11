from django.urls import path

from . import views

urlpatterns = [
    path("ai-context/facilitator", views.facilitator_context),
    path("ai-context/company", views.company_context),
]
