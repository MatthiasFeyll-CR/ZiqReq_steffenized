from django.urls import path

from . import views

urlpatterns = [
    path("monitoring/dashboard/", views.monitoring_dashboard),
]
