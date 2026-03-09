from django.urls import path

from . import views

urlpatterns = [
    path("validate", views.validate_token),
    path("dev-users", views.dev_users),
    path("dev-login", views.dev_login),
    path("dev-switch", views.dev_switch),
]
