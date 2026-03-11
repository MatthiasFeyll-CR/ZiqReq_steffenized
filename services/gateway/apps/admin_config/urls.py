from django.urls import path

from . import views

urlpatterns = [
    path("parameters", views.parameter_list),
    path("parameters/<str:key>", views.parameter_update),
]
