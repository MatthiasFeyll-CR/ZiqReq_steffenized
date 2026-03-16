import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.projects.models import ChatMessage, Project, ProjectCollaborator

USER_1_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
USER_2_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
USER_3_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")


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
class TestChatMessagesAPI(TestCase):
    """Integration tests for the Chat Messages API."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = _create_user(USER_1_ID, "user1@test.local", "Test User1")
        self.user2 = _create_user(USER_2_ID, "user2@test.local", "Test User2")
        self.user3 = _create_user(USER_3_ID, "user3@test.local", "Test User3")
        self.project = Project.objects.create(owner_id=self.user1.id, title="Test Project")
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

    def _chat_url(self, project_id=None):
        return f"/api/projects/{project_id or self.project.id}/chat/"

    # --- POST /api/projects/:id/chat ---

    def test_create_message_returns_201(self):
        """POST /api/projects/:id/chat creates message, returns 201."""
        response = self.client.post(
            self._chat_url(),
            {"content": "Hello world"},
            format="json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["project_id"] == str(self.project.id)
        assert data["sender_type"] == "user"
        assert data["sender_id"] == str(self.user1.id)
        assert data["content"] == "Hello world"
        assert data["message_type"] == "regular"
        assert "id" in data
        assert "created_at" in data

    def test_create_message_persists(self):
        """POST creates a ChatMessage in the database."""
        self.client.post(
            self._chat_url(),
            {"content": "Persisted message"},
            format="json",
        )
        assert ChatMessage.objects.filter(
            project_id=self.project.id, content="Persisted message"
        ).exists()

    def test_create_message_empty_content_returns_400(self):
        """POST with empty content returns 400."""
        response = self.client.post(
            self._chat_url(),
            {"content": ""},
            format="json",
        )
        assert response.status_code == 400

    def test_create_message_missing_content_returns_400(self):
        """POST without content field returns 400."""
        response = self.client.post(
            self._chat_url(),
            {},
            format="json",
        )
        assert response.status_code == 400

    def test_create_message_unauthenticated_returns_401(self):
        """POST without auth returns 401."""
        client = APIClient()
        response = client.post(
            self._chat_url(),
            {"content": "Hello"},
            format="json",
        )
        assert response.status_code == 401

    def test_create_message_no_access_returns_403(self):
        """POST by non-owner/non-collaborator returns 403."""
        self._login_as(self.user2)
        response = self.client.post(
            self._chat_url(),
            {"content": "Hello"},
            format="json",
        )
        assert response.status_code == 403

    def test_create_message_collaborator_allowed(self):
        """POST by collaborator returns 201."""
        ProjectCollaborator.objects.create(project=self.project, user_id=self.user2.id)
        self._login_as(self.user2)
        response = self.client.post(
            self._chat_url(),
            {"content": "Collaborator message"},
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["sender_id"] == str(self.user2.id)

    def test_create_message_nonexistent_project_returns_404(self):
        """POST to nonexistent project returns 404."""
        fake_id = str(uuid.uuid4())
        response = self.client.post(
            self._chat_url(fake_id),
            {"content": "Hello"},
            format="json",
        )
        assert response.status_code == 404

    # --- GET /api/projects/:id/chat ---

    def test_list_messages_returns_200(self):
        """GET /api/projects/:id/chat returns 200 with messages."""
        ChatMessage.objects.create(
            project_id=self.project.id,
            sender_type="user",
            sender_id=self.user1.id,
            content="First message",
        )
        ChatMessage.objects.create(
            project_id=self.project.id,
            sender_type="ai",
            sender_id=None,
            content="AI response",
        )

        response = self.client.get(self._chat_url())
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert data["total"] == 2
        assert len(data["messages"]) == 2

    def test_list_messages_ordered_by_created_at_asc(self):
        """GET returns messages ordered by created_at ASC."""
        m1 = ChatMessage.objects.create(
            project_id=self.project.id,
            sender_type="user",
            sender_id=self.user1.id,
            content="First",
        )
        m2 = ChatMessage.objects.create(
            project_id=self.project.id,
            sender_type="user",
            sender_id=self.user1.id,
            content="Second",
        )

        response = self.client.get(self._chat_url())
        data = response.json()
        assert data["messages"][0]["id"] == str(m1.id)
        assert data["messages"][1]["id"] == str(m2.id)

    def test_list_messages_pagination(self):
        """GET with limit and offset supports pagination."""
        for i in range(5):
            ChatMessage.objects.create(
                project_id=self.project.id,
                sender_type="user",
                sender_id=self.user1.id,
                content=f"Message {i}",
            )

        response = self.client.get(f"{self._chat_url()}?limit=2&offset=1")
        data = response.json()
        assert data["total"] == 5
        assert data["limit"] == 2
        assert data["offset"] == 1
        assert len(data["messages"]) == 2
        assert data["messages"][0]["content"] == "Message 1"

    def test_list_messages_unauthenticated_returns_401(self):
        """GET without auth returns 401."""
        client = APIClient()
        response = client.get(self._chat_url())
        assert response.status_code == 401

    def test_list_messages_non_owner_returns_200_read_only(self):
        """GET by non-owner/non-collaborator returns 200 (read-only access)."""
        self._login_as(self.user2)
        response = self.client.get(self._chat_url())
        assert response.status_code == 200

    def test_list_messages_nonexistent_project_returns_404(self):
        """GET for nonexistent project returns 404."""
        fake_id = str(uuid.uuid4())
        response = self.client.get(self._chat_url(fake_id))
        assert response.status_code == 404

    def test_list_messages_empty(self):
        """GET returns empty list when no messages."""
        response = self.client.get(self._chat_url())
        data = response.json()
        assert data["total"] == 0
        assert data["messages"] == []
