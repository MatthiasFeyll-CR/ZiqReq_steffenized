import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.board.models import BoardConnection, BoardNode
from apps.ideas.models import Idea, IdeaCollaborator

USER_1_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
USER_2_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")


def _create_user(user_id: uuid.UUID, email: str, display_name: str) -> User:
    return User.objects.create(
        id=user_id,
        email=email,
        first_name=display_name.split()[0],
        last_name=display_name.split()[-1],
        display_name=display_name,
        roles=["user"],
    )


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestBoardNodesAPI(TestCase):
    """Integration tests for the Board Nodes API."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = _create_user(USER_1_ID, "user1@test.local", "Test User1")
        self.user2 = _create_user(USER_2_ID, "user2@test.local", "Test User2")
        self.idea = Idea.objects.create(owner_id=self.user1.id, title="Test Idea")
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.user1.id)},
            format="json",
        )

    def _login_as(self, user: User):
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(user.id)},
            format="json",
        )

    def _nodes_url(self, idea_id=None):
        return f"/api/ideas/{idea_id or self.idea.id}/board/nodes"

    def _node_url(self, node_id, idea_id=None):
        return f"/api/ideas/{idea_id or self.idea.id}/board/nodes/{node_id}"

    # --- GET /api/ideas/:id/board/nodes ---

    def test_list_nodes_returns_200(self):
        """API-BOARD.01: GET returns all nodes for an idea."""
        BoardNode.objects.create(
            idea_id=self.idea.id, node_type="box", title="Node 1", created_by="user"
        )
        BoardNode.objects.create(
            idea_id=self.idea.id, node_type="group", title="Group 1", created_by="user"
        )

        response = self.client.get(self._nodes_url())
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert len(data["nodes"]) == 2

    def test_list_nodes_empty(self):
        """GET returns empty list when no nodes exist."""
        response = self.client.get(self._nodes_url())
        data = response.json()
        assert data["nodes"] == []

    def test_list_nodes_unauthenticated_returns_401(self):
        """GET without auth returns 401."""
        client = APIClient()
        response = client.get(self._nodes_url())
        assert response.status_code == 401

    def test_list_nodes_no_access_returns_403(self):
        """GET by non-owner returns 403."""
        self._login_as(self.user2)
        response = self.client.get(self._nodes_url())
        assert response.status_code == 403

    def test_list_nodes_nonexistent_idea_returns_404(self):
        """GET for nonexistent idea returns 404."""
        fake_id = str(uuid.uuid4())
        response = self.client.get(self._nodes_url(fake_id))
        assert response.status_code == 404

    # --- POST /api/ideas/:id/board/nodes ---

    def test_create_box_node_returns_201(self):
        """API-BOARD.02: POST creates a box node."""
        response = self.client.post(
            self._nodes_url(),
            {
                "node_type": "box",
                "title": "My Box",
                "body": "Some content",
                "position_x": 100.0,
                "position_y": 200.0,
            },
            format="json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["node_type"] == "box"
        assert data["title"] == "My Box"
        assert data["body"] == "Some content"
        assert data["position_x"] == 100.0
        assert data["position_y"] == 200.0
        assert data["is_locked"] is False
        assert data["created_by"] == "user"
        assert "id" in data
        assert "created_at" in data

    def test_create_node_invalid_type_returns_400(self):
        """API-BOARD.02: POST with invalid node_type returns 400."""
        response = self.client.post(
            self._nodes_url(),
            {"node_type": "invalid", "title": "Bad"},
            format="json",
        )
        assert response.status_code == 400

    def test_create_node_missing_type_returns_400(self):
        """POST without node_type returns 400."""
        response = self.client.post(
            self._nodes_url(),
            {"title": "No type"},
            format="json",
        )
        assert response.status_code == 400

    def test_create_node_title_too_long_returns_400(self):
        """DB-NODE.02: POST with title > 500 chars returns 400."""
        response = self.client.post(
            self._nodes_url(),
            {"node_type": "box", "title": "x" * 501},
            format="json",
        )
        assert response.status_code == 400

    def test_create_node_body_too_long_returns_400(self):
        """DB-NODE.03: POST with body > 5000 chars returns 400."""
        response = self.client.post(
            self._nodes_url(),
            {"node_type": "box", "title": "Test", "body": "x" * 5001},
            format="json",
        )
        assert response.status_code == 400

    def test_create_node_with_group_parent(self):
        """DB-NODE.04: POST with parent_id referencing group node succeeds."""
        group = BoardNode.objects.create(
            idea_id=self.idea.id,
            node_type="group",
            title="Parent Group",
            created_by="user",
        )
        response = self.client.post(
            self._nodes_url(),
            {
                "node_type": "box",
                "title": "Child Box",
                "parent_id": str(group.id),
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["parent_id"] == str(group.id)

    def test_create_node_with_non_group_parent_returns_400(self):
        """API-BOARD.04b: POST with parent_id referencing non-group returns 400."""
        box = BoardNode.objects.create(
            idea_id=self.idea.id,
            node_type="box",
            title="Not a group",
            created_by="user",
        )
        response = self.client.post(
            self._nodes_url(),
            {
                "node_type": "box",
                "title": "Child",
                "parent_id": str(box.id),
            },
            format="json",
        )
        assert response.status_code == 400
        assert response.json()["error"] == "PARENT_NOT_GROUP"

    def test_create_node_unauthenticated_returns_401(self):
        """POST without auth returns 401."""
        client = APIClient()
        response = client.post(
            self._nodes_url(),
            {"node_type": "box", "title": "Test"},
            format="json",
        )
        assert response.status_code == 401

    def test_create_node_persists(self):
        """DB-NODE.01: POST creates a BoardNode in the database."""
        self.client.post(
            self._nodes_url(),
            {"node_type": "box", "title": "Persisted"},
            format="json",
        )
        assert BoardNode.objects.filter(
            idea_id=self.idea.id, title="Persisted"
        ).exists()

    # --- PATCH /api/ideas/:id/board/nodes/:nodeId ---

    def test_update_node_returns_200(self):
        """API-BOARD.03: PATCH updates node content and position."""
        node = BoardNode.objects.create(
            idea_id=self.idea.id, node_type="box", title="Old", created_by="user"
        )
        response = self.client.patch(
            self._node_url(node.id),
            {"title": "New Title", "position_x": 50.0},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title"
        assert data["position_x"] == 50.0

    def test_update_locked_node_returns_403(self):
        """API-BOARD.05: PATCH on locked node returns 403."""
        node = BoardNode.objects.create(
            idea_id=self.idea.id,
            node_type="box",
            title="Locked",
            is_locked=True,
            created_by="user",
        )
        response = self.client.patch(
            self._node_url(node.id),
            {"title": "Trying to update"},
            format="json",
        )
        assert response.status_code == 403
        assert response.json()["error"] == "NODE_LOCKED"

    def test_update_nonexistent_node_returns_404(self):
        """PATCH on nonexistent node returns 404."""
        fake_id = str(uuid.uuid4())
        response = self.client.patch(
            self._node_url(fake_id),
            {"title": "New"},
            format="json",
        )
        assert response.status_code == 404

    def test_update_node_parent_must_be_group(self):
        """API-BOARD.04c: PATCH parent_id must reference group node."""
        node = BoardNode.objects.create(
            idea_id=self.idea.id, node_type="box", title="Node", created_by="user"
        )
        box_parent = BoardNode.objects.create(
            idea_id=self.idea.id, node_type="box", title="Box Parent", created_by="user"
        )
        response = self.client.patch(
            self._node_url(node.id),
            {"parent_id": str(box_parent.id)},
            format="json",
        )
        assert response.status_code == 400
        assert response.json()["error"] == "PARENT_NOT_GROUP"

    # --- DELETE /api/ideas/:id/board/nodes/:nodeId ---

    def test_delete_node_returns_204(self):
        """API-BOARD.04: DELETE removes node."""
        node = BoardNode.objects.create(
            idea_id=self.idea.id, node_type="box", title="To Delete", created_by="user"
        )
        response = self.client.delete(self._node_url(node.id))
        assert response.status_code == 204
        assert not BoardNode.objects.filter(id=node.id).exists()

    def test_delete_node_detaches_children(self):
        """API-BOARD.06: DELETE group detaches children (parent_id set to NULL)."""
        group = BoardNode.objects.create(
            idea_id=self.idea.id,
            node_type="group",
            title="Parent Group",
            created_by="user",
        )
        child = BoardNode.objects.create(
            idea_id=self.idea.id,
            node_type="box",
            title="Child",
            parent=group,
            created_by="user",
        )
        response = self.client.delete(self._node_url(group.id))
        assert response.status_code == 204
        child.refresh_from_db()
        assert child.parent_id is None

    def test_delete_nonexistent_node_returns_404(self):
        """DELETE nonexistent node returns 404."""
        fake_id = str(uuid.uuid4())
        response = self.client.delete(self._node_url(fake_id))
        assert response.status_code == 404

    def test_delete_unauthenticated_returns_401(self):
        """DELETE without auth returns 401."""
        node = BoardNode.objects.create(
            idea_id=self.idea.id, node_type="box", title="Node", created_by="user"
        )
        client = APIClient()
        response = client.delete(self._node_url(node.id))
        assert response.status_code == 401

    # --- Access control ---

    def test_collaborator_can_access_nodes(self):
        """Collaborator can list and create nodes."""
        IdeaCollaborator.objects.create(idea=self.idea, user_id=self.user2.id)
        self._login_as(self.user2)
        response = self.client.get(self._nodes_url())
        assert response.status_code == 200

    def test_create_free_text_node(self):
        """POST creates a free_text node type."""
        response = self.client.post(
            self._nodes_url(),
            {"node_type": "free_text", "body": "Annotation text"},
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["node_type"] == "free_text"

    def test_create_group_node(self):
        """POST creates a group node type."""
        response = self.client.post(
            self._nodes_url(),
            {
                "node_type": "group",
                "title": "My Group",
                "width": 400.0,
                "height": 300.0,
            },
            format="json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["node_type"] == "group"
        assert data["width"] == 400.0
        assert data["height"] == 300.0


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestBoardConnectionsAPI(TestCase):
    """Integration tests for the Board Connections API."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = _create_user(USER_1_ID, "user1@test.local", "Test User1")
        self.user2 = _create_user(USER_2_ID, "user2@test.local", "Test User2")
        self.idea = Idea.objects.create(owner_id=self.user1.id, title="Test Idea")
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.user1.id)},
            format="json",
        )
        self.node_a = BoardNode.objects.create(
            idea_id=self.idea.id, node_type="box", title="Node A", created_by="user"
        )
        self.node_b = BoardNode.objects.create(
            idea_id=self.idea.id, node_type="box", title="Node B", created_by="user"
        )

    def _login_as(self, user: User):
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(user.id)},
            format="json",
        )

    def _conns_url(self, idea_id=None):
        return f"/api/ideas/{idea_id or self.idea.id}/board/connections"

    def _conn_url(self, conn_id, idea_id=None):
        return f"/api/ideas/{idea_id or self.idea.id}/board/connections/{conn_id}"

    # --- GET /api/ideas/:id/board/connections ---

    def test_list_connections_returns_200(self):
        """API-BOARD.08: GET returns all connections for an idea."""
        BoardConnection.objects.create(
            idea_id=self.idea.id,
            source_node=self.node_a,
            target_node=self.node_b,
        )
        response = self.client.get(self._conns_url())
        assert response.status_code == 200
        data = response.json()
        assert "connections" in data
        assert len(data["connections"]) == 1

    def test_list_connections_empty(self):
        """GET returns empty list when no connections exist."""
        response = self.client.get(self._conns_url())
        data = response.json()
        assert data["connections"] == []

    def test_list_connections_unauthenticated_returns_401(self):
        """GET without auth returns 401."""
        client = APIClient()
        response = client.get(self._conns_url())
        assert response.status_code == 401

    def test_list_connections_no_access_returns_403(self):
        """GET by non-owner returns 403."""
        self._login_as(self.user2)
        response = self.client.get(self._conns_url())
        assert response.status_code == 403

    # --- POST /api/ideas/:id/board/connections ---

    def test_create_connection_returns_201(self):
        """API-BOARD.09: POST creates a connection."""
        response = self.client.post(
            self._conns_url(),
            {
                "source_node_id": str(self.node_a.id),
                "target_node_id": str(self.node_b.id),
                "label": "relates to",
            },
            format="json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["source_node_id"] == str(self.node_a.id)
        assert data["target_node_id"] == str(self.node_b.id)
        assert data["label"] == "relates to"
        assert "id" in data
        assert "created_at" in data

    def test_create_connection_no_label(self):
        """POST creates a connection without label."""
        response = self.client.post(
            self._conns_url(),
            {
                "source_node_id": str(self.node_a.id),
                "target_node_id": str(self.node_b.id),
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["label"] is None

    def test_create_self_connection_returns_400(self):
        """DB-CONN.02: POST with source == target returns 400 SELF_CONNECTION."""
        response = self.client.post(
            self._conns_url(),
            {
                "source_node_id": str(self.node_a.id),
                "target_node_id": str(self.node_a.id),
            },
            format="json",
        )
        assert response.status_code == 400
        assert response.json()["error"] == "SELF_CONNECTION"

    def test_create_duplicate_connection_returns_409(self):
        """DB-CONN.03: POST duplicate source-target returns 409."""
        BoardConnection.objects.create(
            idea_id=self.idea.id,
            source_node=self.node_a,
            target_node=self.node_b,
        )
        response = self.client.post(
            self._conns_url(),
            {
                "source_node_id": str(self.node_a.id),
                "target_node_id": str(self.node_b.id),
            },
            format="json",
        )
        assert response.status_code == 409
        assert response.json()["error"] == "DUPLICATE_CONNECTION"

    def test_create_connection_nonexistent_source_returns_404(self):
        """POST with nonexistent source node returns 404."""
        response = self.client.post(
            self._conns_url(),
            {
                "source_node_id": str(uuid.uuid4()),
                "target_node_id": str(self.node_b.id),
            },
            format="json",
        )
        assert response.status_code == 404

    def test_create_connection_nonexistent_target_returns_404(self):
        """POST with nonexistent target node returns 404."""
        response = self.client.post(
            self._conns_url(),
            {
                "source_node_id": str(self.node_a.id),
                "target_node_id": str(uuid.uuid4()),
            },
            format="json",
        )
        assert response.status_code == 404

    def test_create_connection_unauthenticated_returns_401(self):
        """POST without auth returns 401."""
        client = APIClient()
        response = client.post(
            self._conns_url(),
            {
                "source_node_id": str(self.node_a.id),
                "target_node_id": str(self.node_b.id),
            },
            format="json",
        )
        assert response.status_code == 401

    def test_create_connection_persists(self):
        """DB-CONN.01: POST creates a BoardConnection in the database."""
        self.client.post(
            self._conns_url(),
            {
                "source_node_id": str(self.node_a.id),
                "target_node_id": str(self.node_b.id),
            },
            format="json",
        )
        assert BoardConnection.objects.filter(
            idea_id=self.idea.id,
            source_node=self.node_a,
            target_node=self.node_b,
        ).exists()

    # --- PATCH /api/ideas/:id/board/connections/:connId ---

    def test_update_connection_label_returns_200(self):
        """API-BOARD.10: PATCH updates connection label."""
        conn = BoardConnection.objects.create(
            idea_id=self.idea.id,
            source_node=self.node_a,
            target_node=self.node_b,
        )
        response = self.client.patch(
            self._conn_url(conn.id),
            {"label": "updated label"},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["label"] == "updated label"

    def test_update_connection_clear_label(self):
        """PATCH can set label to null."""
        conn = BoardConnection.objects.create(
            idea_id=self.idea.id,
            source_node=self.node_a,
            target_node=self.node_b,
            label="old",
        )
        response = self.client.patch(
            self._conn_url(conn.id),
            {"label": None},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["label"] is None

    def test_update_nonexistent_connection_returns_404(self):
        """PATCH on nonexistent connection returns 404."""
        fake_id = str(uuid.uuid4())
        response = self.client.patch(
            self._conn_url(fake_id),
            {"label": "new"},
            format="json",
        )
        assert response.status_code == 404

    # --- DELETE /api/ideas/:id/board/connections/:connId ---

    def test_delete_connection_returns_204(self):
        """API-BOARD.11: DELETE removes connection."""
        conn = BoardConnection.objects.create(
            idea_id=self.idea.id,
            source_node=self.node_a,
            target_node=self.node_b,
        )
        response = self.client.delete(self._conn_url(conn.id))
        assert response.status_code == 204
        assert not BoardConnection.objects.filter(id=conn.id).exists()

    def test_delete_nonexistent_connection_returns_404(self):
        """DELETE nonexistent connection returns 404."""
        fake_id = str(uuid.uuid4())
        response = self.client.delete(self._conn_url(fake_id))
        assert response.status_code == 404

    def test_delete_connection_unauthenticated_returns_401(self):
        """DELETE without auth returns 401."""
        conn = BoardConnection.objects.create(
            idea_id=self.idea.id,
            source_node=self.node_a,
            target_node=self.node_b,
        )
        client = APIClient()
        response = client.delete(self._conn_url(conn.id))
        assert response.status_code == 401

    def test_cascade_delete_node_removes_connections(self):
        """Deleting a node cascades to remove its connections."""
        BoardConnection.objects.create(
            idea_id=self.idea.id,
            source_node=self.node_a,
            target_node=self.node_b,
        )
        assert BoardConnection.objects.filter(idea_id=self.idea.id).count() == 1
        self.node_a.delete()
        assert BoardConnection.objects.filter(idea_id=self.idea.id).count() == 0

    def test_collaborator_can_access_connections(self):
        """Collaborator can list and create connections."""
        IdeaCollaborator.objects.create(idea=self.idea, user_id=self.user2.id)
        self._login_as(self.user2)
        response = self.client.get(self._conns_url())
        assert response.status_code == 200
