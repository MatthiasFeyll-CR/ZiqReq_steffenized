from django.urls import path

from . import views

urlpatterns = [
    path("monitoring/dashboard/", views.monitoring_dashboard),
    path("admin/monitoring", views.monitoring_dashboard),
    path("admin/monitoring/alerts", views.alert_config),
]
