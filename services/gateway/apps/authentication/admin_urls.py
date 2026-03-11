from django.urls import path

from . import views

urlpatterns = [
    path("users/search", views.admin_users_search),
]
