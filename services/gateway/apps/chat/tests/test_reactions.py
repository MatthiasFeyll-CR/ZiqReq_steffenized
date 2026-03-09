import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.ideas.models import ChatMessage, Idea, IdeaCollaborator, UserReaction

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
class TestUserReactionsAPI(TestCase):
    """Integration tests for the User Reactions API (T-2.8.01 through T-2.8.05)."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = _create_user(USER_1_ID, "user1@test.local", "Test User1")
        self.user2 = _create_user(USER_2_ID, "user2@test.local", "Test User2")
        self.user3 = _create_user(USER_3_ID, "user3@test.local", "Test User3")

        self.idea = Idea.objects.create(owner_id=self.user1.id, title="Test Idea")
        # user2 is a collaborator
        IdeaCollaborator.objects.create(idea=self.idea, user_id=self.user2.id)

        # user1 sends a message (other users can react to it)
        self.user1_message = ChatMessage.objects.create(
            idea_id=self.idea.id,
            sender_type="user",
            sender_id=self.user1.id,
            content="Hello from user1",
        )
        # user2 sends a message
        self.user2_message = ChatMessage.objects.create(
            idea_id=self.idea.id,
            sender_type="user",
            sender_id=self.user2.id,
            content="Hello from user2",
        )
        # AI sends a message
        self.ai_message = ChatMessage.objects.create(
            idea_id=self.idea.id,
            sender_type="ai",
            sender_id=None,
            content="AI response",
        )

        # Login as user2 by default
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.user2.id)},
            format="json",
        )

    def _login_as(self, user: User):
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(user.id)},
            format="json",
        )

    def _reactions_url(self, message_id, idea_id=None):
        iid = idea_id or self.idea.id
        return f"/api/ideas/{iid}/chat/{message_id}/reactions"

    # --- T-2.8.01: User can react to other user's message ---

    def test_react_to_other_user_message_returns_201(self):
        """T-2.8.01: POST reaction on another user's message returns 201."""
        response = self.client.post(
            self._reactions_url(self.user1_message.id),
            {"reaction_type": "thumbs_up"},
            format="json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["message_id"] == str(self.user1_message.id)
        assert data["user_id"] == str(self.user2.id)
        assert data["reaction_type"] == "thumbs_up"
        assert "id" in data
        assert "created_at" in data

    def test_react_persists_in_database(self):
        """Reaction is persisted in the database."""
        self.client.post(
            self._reactions_url(self.user1_message.id),
            {"reaction_type": "heart"},
            format="json",
        )
        assert UserReaction.objects.filter(
            message_id=self.user1_message.id,
            user_id=self.user2.id,
            reaction_type="heart",
        ).exists()

    def test_react_thumbs_down_valid(self):
        """thumbs_down is a valid reaction type."""
        response = self.client.post(
            self._reactions_url(self.user1_message.id),
            {"reaction_type": "thumbs_down"},
            format="json",
        )
        assert response.status_code == 201

    def test_react_invalid_type_returns_400(self):
        """Invalid reaction_type returns 400."""
        response = self.client.post(
            self._reactions_url(self.user1_message.id),
            {"reaction_type": "fire"},
            format="json",
        )
        assert response.status_code == 400

    # --- T-2.8.02: Cannot react to AI message ---

    def test_react_to_ai_message_returns_400(self):
        """T-2.8.02: POST reaction on AI message returns 400 CANNOT_REACT_TO_AI."""
        response = self.client.post(
            self._reactions_url(self.ai_message.id),
            {"reaction_type": "thumbs_up"},
            format="json",
        )
        assert response.status_code == 400
        assert response.json()["error"] == "CANNOT_REACT_TO_AI"

    # --- T-2.8.03: Cannot react to own message ---

    def test_react_to_own_message_returns_400(self):
        """T-2.8.03: POST reaction on own message returns 400 CANNOT_REACT_TO_SELF."""
        response = self.client.post(
            self._reactions_url(self.user2_message.id),
            {"reaction_type": "thumbs_up"},
            format="json",
        )
        assert response.status_code == 400
        assert response.json()["error"] == "CANNOT_REACT_TO_SELF"

    # --- T-2.8.04: Cannot react twice ---

    def test_duplicate_reaction_returns_409(self):
        """T-2.8.04: POST duplicate reaction returns 409 ALREADY_REACTED."""
        self.client.post(
            self._reactions_url(self.user1_message.id),
            {"reaction_type": "thumbs_up"},
            format="json",
        )
        response = self.client.post(
            self._reactions_url(self.user1_message.id),
            {"reaction_type": "heart"},
            format="json",
        )
        assert response.status_code == 409
        assert response.json()["error"] == "ALREADY_REACTED"

    # --- T-2.8.05: Remove reaction ---

    def test_remove_reaction_returns_204(self):
        """T-2.8.05: DELETE reaction returns 204."""
        self.client.post(
            self._reactions_url(self.user1_message.id),
            {"reaction_type": "thumbs_up"},
            format="json",
        )
        response = self.client.delete(self._reactions_url(self.user1_message.id))
        assert response.status_code == 204
        assert not UserReaction.objects.filter(
            message_id=self.user1_message.id, user_id=self.user2.id
        ).exists()

    def test_remove_nonexistent_reaction_returns_404(self):
        """DELETE when no reaction exists returns 404."""
        response = self.client.delete(self._reactions_url(self.user1_message.id))
        assert response.status_code == 404

    # --- Auth / access tests ---

    def test_react_unauthenticated_returns_401(self):
        """POST without auth returns 401."""
        client = APIClient()
        response = client.post(
            self._reactions_url(self.user1_message.id),
            {"reaction_type": "thumbs_up"},
            format="json",
        )
        assert response.status_code == 401

    def test_react_no_access_returns_403(self):
        """POST by non-collaborator returns 403."""
        self._login_as(self.user3)
        response = self.client.post(
            self._reactions_url(self.user1_message.id),
            {"reaction_type": "thumbs_up"},
            format="json",
        )
        assert response.status_code == 403

    def test_react_nonexistent_message_returns_404(self):
        """POST on nonexistent message returns 404."""
        fake_msg_id = str(uuid.uuid4())
        response = self.client.post(
            self._reactions_url(fake_msg_id),
            {"reaction_type": "thumbs_up"},
            format="json",
        )
        assert response.status_code == 404
