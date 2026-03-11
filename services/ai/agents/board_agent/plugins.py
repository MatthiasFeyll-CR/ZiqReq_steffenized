"""Board Agent SK plugins (8 tools).

Each method is decorated with @kernel_function so SK registers it as a
callable tool for the Azure OpenAI function-calling loop.
"""

from __future__ import annotations

import logging
from typing import Any

from semantic_kernel.functions import kernel_function

from events.publishers import publish_event
from grpc_clients.core_client import CoreClient

logger = logging.getLogger(__name__)


def _error_response(code: str, message: str) -> dict[str, Any]:
    """Standard error format returned to the model."""
    return {"error": {"code": code, "message": message}}


class BoardPlugin:
    """8 tools for the Board Agent to manipulate board nodes and connections."""

    def __init__(self, idea_id: str, board_state: dict[str, Any] | None = None) -> None:
        self.idea_id = idea_id
        self.board_state = board_state or {}
        self.mutations: list[dict[str, Any]] = []
        self._core_client = CoreClient()

    def _is_locked(self, node_id: str) -> bool:
        """Check if a node is locked by looking up board state."""
        for node in self.board_state.get("nodes", []):
            if str(node.get("id", "")) == node_id:
                return bool(node.get("is_locked", False))
        return False

    def _find_node(self, node_id: str) -> dict[str, Any] | None:
        """Find a node by ID in the board state."""
        for node in self.board_state.get("nodes", []):
            if str(node.get("id", "")) == node_id:
                return node
        return None

    @kernel_function(
        name="create_node",
        description=(
            "Create a new node on the board. Use node_type='box' for topic boxes, "
            "'group' for grouping containers, 'free_text' for annotations."
        ),
    )
    async def create_node(
        self,
        node_type: str,
        title: str,
        body: str = "",
        position_x: float = 0.0,
        position_y: float = 0.0,
        width: float | None = None,
        height: float | None = None,
        parent_id: str | None = None,
    ) -> dict[str, Any]:
        """Create a board node via Core gRPC."""
        if node_type not in ("box", "group", "free_text"):
            return _error_response(
                "validation_error",
                f"Invalid node_type '{node_type}'. Must be box, group, or free_text.",
            )

        result = self._core_client.create_board_node(
            idea_id=self.idea_id,
            node_type=node_type,
            title=title,
            body=body,
            position_x=position_x,
            position_y=position_y,
            width=width,
            height=height,
            parent_id=parent_id,
        )

        mutation = {
            "action": "create_node",
            "node_type": node_type,
            "title": title,
            "node_id": result.get("node_id"),
        }
        self.mutations.append(mutation)

        await publish_event("ai.board.updated", {
            "idea_id": self.idea_id,
            "mutation": mutation,
        })

        return result

    @kernel_function(
        name="update_node",
        description="Update the title or body of an existing board node.",
    )
    async def update_node(
        self,
        node_id: str,
        title: str | None = None,
        body: str | None = None,
    ) -> dict[str, Any]:
        """Update a board node via Core gRPC."""
        if self._is_locked(node_id):
            return _error_response("node_locked", f"Node {node_id} is locked and cannot be modified.")

        updated_fields = []
        if title is not None:
            updated_fields.append("title")
        if body is not None:
            updated_fields.append("body")

        result = self._core_client.update_board_node(
            node_id=node_id,
            title=title,
            body=body,
        )

        mutation = {
            "action": "update_node",
            "node_id": node_id,
            "updated_fields": updated_fields,
        }
        self.mutations.append(mutation)

        await publish_event("ai.board.updated", {
            "idea_id": self.idea_id,
            "mutation": mutation,
        })

        return result

    @kernel_function(
        name="delete_node",
        description="Delete a board node. Children of deleted groups become orphans.",
    )
    async def delete_node(self, node_id: str) -> dict[str, Any]:
        """Delete a board node via Core gRPC."""
        if self._is_locked(node_id):
            return _error_response("node_locked", f"Node {node_id} is locked and cannot be deleted.")

        result = self._core_client.delete_board_node(node_id=node_id)

        mutation = {"action": "delete_node", "node_id": node_id}
        self.mutations.append(mutation)

        await publish_event("ai.board.updated", {
            "idea_id": self.idea_id,
            "mutation": mutation,
        })

        return result

    @kernel_function(
        name="move_node",
        description="Move a node to a new position. Optionally reparent into a group.",
    )
    async def move_node(
        self,
        node_id: str,
        position_x: float,
        position_y: float,
        new_parent_id: str | None = None,
    ) -> dict[str, Any]:
        """Move a board node via Core gRPC."""
        if self._is_locked(node_id):
            return _error_response("node_locked", f"Node {node_id} is locked and cannot be moved.")

        result = self._core_client.move_board_node(
            node_id=node_id,
            position_x=position_x,
            position_y=position_y,
            new_parent_id=new_parent_id,
        )

        mutation = {
            "action": "move_node",
            "node_id": node_id,
            "position_x": position_x,
            "position_y": position_y,
        }
        self.mutations.append(mutation)

        await publish_event("ai.board.updated", {
            "idea_id": self.idea_id,
            "mutation": mutation,
        })

        return result

    @kernel_function(
        name="resize_group",
        description="Resize a group node to the specified width and height.",
    )
    async def resize_group(
        self,
        node_id: str,
        width: float,
        height: float,
    ) -> dict[str, Any]:
        """Resize a group node via Core gRPC."""
        node = self._find_node(node_id)
        if node and node.get("node_type") != "group":
            return _error_response("validation_error", "resize_group can only be used on group nodes.")

        result = self._core_client.resize_board_group(
            node_id=node_id,
            width=width,
            height=height,
        )

        mutation = {
            "action": "resize_group",
            "node_id": node_id,
            "width": width,
            "height": height,
        }
        self.mutations.append(mutation)

        await publish_event("ai.board.updated", {
            "idea_id": self.idea_id,
            "mutation": mutation,
        })

        return result

    @kernel_function(
        name="create_connection",
        description="Create a connection (edge) between two board nodes.",
    )
    async def create_connection(
        self,
        source_node_id: str,
        target_node_id: str,
        label: str = "",
    ) -> dict[str, Any]:
        """Create a board connection via Core gRPC."""
        result = self._core_client.create_board_connection(
            idea_id=self.idea_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            label=label,
        )

        mutation = {
            "action": "create_connection",
            "source_node_id": source_node_id,
            "target_node_id": target_node_id,
            "connection_id": result.get("connection_id"),
        }
        self.mutations.append(mutation)

        await publish_event("ai.board.updated", {
            "idea_id": self.idea_id,
            "mutation": mutation,
        })

        return result

    @kernel_function(
        name="update_connection",
        description="Update the label of an existing board connection.",
    )
    async def update_connection(
        self,
        connection_id: str,
        label: str,
    ) -> dict[str, Any]:
        """Update a board connection via Core gRPC."""
        result = self._core_client.update_board_connection(
            connection_id=connection_id,
            label=label,
        )

        mutation = {
            "action": "update_connection",
            "connection_id": connection_id,
            "label": label,
        }
        self.mutations.append(mutation)

        await publish_event("ai.board.updated", {
            "idea_id": self.idea_id,
            "mutation": mutation,
        })

        return result

    @kernel_function(
        name="delete_connection",
        description="Delete a board connection between two nodes.",
    )
    async def delete_connection(self, connection_id: str) -> dict[str, Any]:
        """Delete a board connection via Core gRPC."""
        result = self._core_client.delete_board_connection(connection_id=connection_id)

        mutation = {"action": "delete_connection", "connection_id": connection_id}
        self.mutations.append(mutation)

        await publish_event("ai.board.updated", {
            "idea_id": self.idea_id,
            "mutation": mutation,
        })

        return result
