from django.urls import path

from . import views

urlpatterns = [
    path("nodes", views.board_nodes),
    path("nodes/<str:node_id>", views.board_node_detail),
    path("connections", views.board_connections),
    path("connections/<str:connection_id>", views.board_connection_detail),
]
