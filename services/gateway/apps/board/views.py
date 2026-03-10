import logging
import uuid

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response

from apps.ideas.authentication import MiddlewareAuthentication
from apps.ideas.models import Idea, IdeaCollaborator

from .models import BoardConnection, BoardNode
from .serializers import (
    BoardConnectionCreateSerializer,
    BoardConnectionResponseSerializer,
    BoardConnectionUpdateSerializer,
    BoardNodeCreateSerializer,
    BoardNodeResponseSerializer,
    BoardNodeUpdateSerializer,
)

logger = logging.getLogger(__name__)


def _require_auth(request: Request):
    """Return user or None. If None, caller should return 401."""
    user = request.user
    if user is None or not getattr(user, "id", None):
        return None
    return user


def _unauthorized_response() -> Response:
    return Response(
        {"error": "UNAUTHORIZED", "message": "Authentication required"},
        status=status.HTTP_401_UNAUTHORIZED,
    )


def _get_idea_or_error(idea_id: str):
    """Validate UUID and fetch idea. Returns (idea, None) or (None, Response)."""
    try:
        uuid.UUID(idea_id)
    except ValueError:
        return None, Response(
            {"error": "NOT_FOUND", "message": "Idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        idea = Idea.objects.get(id=idea_id, deleted_at__isnull=True)
    except Idea.DoesNotExist:
        return None, Response(
            {"error": "NOT_FOUND", "message": "Idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    return idea, None


def _check_access(user, idea) -> bool:
    """Check if user has access to idea (owner, co-owner, or collaborator)."""
    if idea.owner_id == user.id:
        return True
    if idea.co_owner_id == user.id:
        return True
    return IdeaCollaborator.objects.filter(
        idea_id=idea.id, user_id=user.id
    ).exists()


def _access_denied_response() -> Response:
    return Response(
        {"error": "ACCESS_DENIED", "message": "You do not have access to this idea"},
        status=status.HTTP_403_FORBIDDEN,
    )


def _broadcast_board_update(
    idea_id: str,
    *,
    nodes_created: list | None = None,
    nodes_updated: list | None = None,
    nodes_deleted: list | None = None,
    connections_created: list | None = None,
    connections_updated: list | None = None,
    connections_deleted: list | None = None,
    source: str = "user",
) -> None:
    """Broadcast a board_update event to the idea's WebSocket group."""
    try:
        channel_layer = get_channel_layer()
        if channel_layer is None:
            return

        group_name = f"idea_{idea_id}"
        payload = {
            "nodes_created": nodes_created or [],
            "nodes_updated": nodes_updated or [],
            "nodes_deleted": nodes_deleted or [],
            "connections_created": connections_created or [],
            "connections_updated": connections_updated or [],
            "connections_deleted": connections_deleted or [],
            "source": source,
        }
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "board_update",
                "idea_id": str(idea_id),
                "payload": payload,
            },
        )
    except Exception:
        logger.exception("Failed to broadcast board_update for idea %s", idea_id)


def _node_to_broadcast_dict(node) -> dict:
    """Serialize a BoardNode to a dict for WebSocket broadcast."""
    return {
        "id": str(node.id),
        "node_type": node.node_type,
        "title": node.title,
        "body": node.body,
        "position_x": node.position_x,
        "position_y": node.position_y,
        "width": node.width,
        "height": node.height,
        "parent_id": str(node.parent_id) if node.parent_id else None,
        "is_locked": node.is_locked,
        "created_by": node.created_by,
    }


def _connection_to_broadcast_dict(conn) -> dict:
    """Serialize a BoardConnection to a dict for WebSocket broadcast."""
    return {
        "id": str(conn.id),
        "source_node_id": str(conn.source_node_id),
        "target_node_id": str(conn.target_node_id),
        "label": conn.label,
    }


@api_view(["GET", "POST"])
@authentication_classes([MiddlewareAuthentication])
def board_nodes(request: Request, idea_id: str) -> Response:
    """Route /api/ideas/:id/board/nodes — GET lists, POST creates."""
    if request.method == "POST":
        return _create_node(request, idea_id)
    return _list_nodes(request, idea_id)


def _list_nodes(request: Request, idea_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    idea, error = _get_idea_or_error(idea_id)
    if error:
        return error

    if not _check_access(user, idea):
        return _access_denied_response()

    nodes = BoardNode.objects.filter(idea_id=idea.id).order_by("created_at")
    serializer = BoardNodeResponseSerializer(nodes, many=True)
    return Response({"nodes": serializer.data})


def _create_node(request: Request, idea_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    idea, error = _get_idea_or_error(idea_id)
    if error:
        return error

    if not _check_access(user, idea):
        return _access_denied_response()

    serializer = BoardNodeCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    parent_id = data.get("parent_id")

    if parent_id:
        try:
            parent = BoardNode.objects.get(id=parent_id, idea_id=idea.id)
        except BoardNode.DoesNotExist:
            return Response(
                {"error": "PARENT_NOT_FOUND", "message": "Parent node not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if parent.node_type != "group":
            return Response(
                {"error": "PARENT_NOT_GROUP", "message": "Parent must be a group node"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    node = BoardNode.objects.create(
        idea_id=idea.id,
        node_type=data["node_type"],
        title=data.get("title"),
        body=data.get("body"),
        position_x=data.get("position_x", 0),
        position_y=data.get("position_y", 0),
        width=data.get("width"),
        height=data.get("height"),
        parent_id=parent_id,
        is_locked=data.get("is_locked", False),
        created_by=data.get("created_by", "user"),
    )

    response_serializer = BoardNodeResponseSerializer(node)

    _broadcast_board_update(
        idea.id,
        nodes_created=[_node_to_broadcast_dict(node)],
        source=node.created_by,
    )

    return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@api_view(["PATCH", "DELETE"])
@authentication_classes([MiddlewareAuthentication])
def board_node_detail(request: Request, idea_id: str, node_id: str) -> Response:
    """Route /api/ideas/:id/board/nodes/:nodeId — PATCH updates, DELETE removes."""
    if request.method == "DELETE":
        return _delete_node(request, idea_id, node_id)
    return _update_node(request, idea_id, node_id)


def _get_node_or_error(node_id: str, idea_id: str):
    """Validate UUID and fetch node. Returns (node, None) or (None, Response)."""
    try:
        uuid.UUID(node_id)
    except ValueError:
        return None, Response(
            {"error": "NOT_FOUND", "message": "Node not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        node = BoardNode.objects.get(id=node_id, idea_id=idea_id)
    except BoardNode.DoesNotExist:
        return None, Response(
            {"error": "NOT_FOUND", "message": "Node not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    return node, None


def _update_node(request: Request, idea_id: str, node_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    idea, error = _get_idea_or_error(idea_id)
    if error:
        return error

    if not _check_access(user, idea):
        return _access_denied_response()

    node, error = _get_node_or_error(node_id, str(idea.id))
    if error:
        return error

    # Allow lock toggle on locked nodes: if the ONLY field is is_locked, skip lock check.
    request_fields = set(request.data.keys())
    is_lock_toggle_only = request_fields == {"is_locked"}

    if node.is_locked and not is_lock_toggle_only:
        return Response(
            {"error": "NODE_LOCKED", "message": "Cannot update a locked node"},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = BoardNodeUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    if "parent_id" in data:
        parent_id = data["parent_id"]
        if parent_id is not None:
            try:
                parent = BoardNode.objects.get(id=parent_id, idea_id=str(idea.id))
            except BoardNode.DoesNotExist:
                return Response(
                    {"error": "PARENT_NOT_FOUND", "message": "Parent node not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if parent.node_type != "group":
                return Response(
                    {"error": "PARENT_NOT_GROUP", "message": "Parent must be a group node"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    for field, value in data.items():
        if field == "parent_id":
            setattr(node, "parent_id", value)
        else:
            setattr(node, field, value)

    node.save()

    response_serializer = BoardNodeResponseSerializer(node)

    _broadcast_board_update(
        idea.id,
        nodes_updated=[_node_to_broadcast_dict(node)],
        source="user",
    )

    return Response(response_serializer.data)


def _delete_node(request: Request, idea_id: str, node_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    idea, error = _get_idea_or_error(idea_id)
    if error:
        return error

    if not _check_access(user, idea):
        return _access_denied_response()

    node, error = _get_node_or_error(node_id, str(idea.id))
    if error:
        return error

    deleted_node_id = str(node.id)
    node.delete()

    _broadcast_board_update(
        idea.id,
        nodes_deleted=[deleted_node_id],
        source="user",
    )

    return Response(status=status.HTTP_204_NO_CONTENT)


# --- Board Connections ---


@api_view(["GET", "POST"])
@authentication_classes([MiddlewareAuthentication])
def board_connections(request: Request, idea_id: str) -> Response:
    """Route /api/ideas/:id/board/connections — GET lists, POST creates."""
    if request.method == "POST":
        return _create_connection(request, idea_id)
    return _list_connections(request, idea_id)


def _list_connections(request: Request, idea_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    idea, error = _get_idea_or_error(idea_id)
    if error:
        return error

    if not _check_access(user, idea):
        return _access_denied_response()

    connections = BoardConnection.objects.filter(idea_id=idea.id).order_by("created_at")
    serializer = BoardConnectionResponseSerializer(connections, many=True)
    return Response({"connections": serializer.data})


def _create_connection(request: Request, idea_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    idea, error = _get_idea_or_error(idea_id)
    if error:
        return error

    if not _check_access(user, idea):
        return _access_denied_response()

    serializer = BoardConnectionCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    source_node_id = data["source_node_id"]
    target_node_id = data["target_node_id"]

    # No self-connections
    if source_node_id == target_node_id:
        return Response(
            {"error": "SELF_CONNECTION", "message": "Cannot connect a node to itself"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Verify both nodes exist and belong to this idea
    if not BoardNode.objects.filter(id=source_node_id, idea_id=idea.id).exists():
        return Response(
            {"error": "NOT_FOUND", "message": "Source node not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if not BoardNode.objects.filter(id=target_node_id, idea_id=idea.id).exists():
        return Response(
            {"error": "NOT_FOUND", "message": "Target node not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Check for duplicate connection
    if BoardConnection.objects.filter(
        source_node_id=source_node_id, target_node_id=target_node_id
    ).exists():
        return Response(
            {
                "error": "DUPLICATE_CONNECTION",
                "message": "A connection between these nodes already exists",
            },
            status=status.HTTP_409_CONFLICT,
        )

    connection = BoardConnection.objects.create(
        idea_id=idea.id,
        source_node_id=source_node_id,
        target_node_id=target_node_id,
        label=data.get("label"),
    )

    response_serializer = BoardConnectionResponseSerializer(connection)

    _broadcast_board_update(
        idea.id,
        connections_created=[_connection_to_broadcast_dict(connection)],
        source="user",
    )

    return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@api_view(["PATCH", "DELETE"])
@authentication_classes([MiddlewareAuthentication])
def board_connection_detail(
    request: Request, idea_id: str, connection_id: str
) -> Response:
    """Route /api/ideas/:id/board/connections/:connId — PATCH updates, DELETE removes."""
    if request.method == "DELETE":
        return _delete_connection(request, idea_id, connection_id)
    return _update_connection(request, idea_id, connection_id)


def _get_connection_or_error(connection_id: str, idea_id: str):
    """Validate UUID and fetch connection. Returns (conn, None) or (None, Response)."""
    try:
        uuid.UUID(connection_id)
    except ValueError:
        return None, Response(
            {"error": "NOT_FOUND", "message": "Connection not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        connection = BoardConnection.objects.get(id=connection_id, idea_id=idea_id)
    except BoardConnection.DoesNotExist:
        return None, Response(
            {"error": "NOT_FOUND", "message": "Connection not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    return connection, None


def _update_connection(
    request: Request, idea_id: str, connection_id: str
) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    idea, error = _get_idea_or_error(idea_id)
    if error:
        return error

    if not _check_access(user, idea):
        return _access_denied_response()

    connection, error = _get_connection_or_error(connection_id, str(idea.id))
    if error:
        return error

    serializer = BoardConnectionUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    for field, value in data.items():
        setattr(connection, field, value)

    connection.save()

    response_serializer = BoardConnectionResponseSerializer(connection)

    _broadcast_board_update(
        idea.id,
        connections_updated=[_connection_to_broadcast_dict(connection)],
        source="user",
    )

    return Response(response_serializer.data)


def _delete_connection(
    request: Request, idea_id: str, connection_id: str
) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    idea, error = _get_idea_or_error(idea_id)
    if error:
        return error

    if not _check_access(user, idea):
        return _access_denied_response()

    connection, error = _get_connection_or_error(connection_id, str(idea.id))
    if error:
        return error

    deleted_conn_id = str(connection.id)
    connection.delete()

    _broadcast_board_update(
        idea.id,
        connections_deleted=[deleted_conn_id],
        source="user",
    )

    return Response(status=status.HTTP_204_NO_CONTENT)
