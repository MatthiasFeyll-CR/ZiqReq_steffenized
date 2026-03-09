from django.urls import path

from . import views

urlpatterns = [
    path("nodes", views.board_nodes),
    path("nodes/<str:node_id>", views.board_node_detail),
]
