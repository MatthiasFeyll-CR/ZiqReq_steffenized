"""Tests for rate limit integration (US-010, T-2.11.01, T-2.11.02)."""

import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.chat.views import get_unprocessed_message_count
from apps.projects.models import ChatMessage, Project

USER_1_ID = uuid.UUID("00000000-0000-0000-0000-000000000011")


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
class TestUnprocessedMessageCount(TestCase):
    """Unit tests for DB-based unprocessed message counting."""

    def setUp(self):
        self.user = _create_user(USER_1_ID, "counter@test.local", "Counter User")
        self.project = Project.objects.create(owner_id=self.user.id, title="Counter Test")
        self.project_id_str = str(self.project.id)

    def test_count_starts_at_zero(self):
        assert get_unprocessed_message_count(self.project_id_str) == 0

    def test_count_increments_with_user_messages(self):
        ChatMessage.objects.create(
            project_id=self.project.id, sender_type="user",
            sender_id=self.user.id, content="msg1",
        )
        assert get_unprocessed_message_count(self.project_id_str) == 1

        ChatMessage.objects.create(
            project_id=self.project.id, sender_type="user",
            sender_id=self.user.id, content="msg2",
        )
        assert get_unprocessed_message_count(self.project_id_str) == 2

    def test_count_resets_after_ai_response(self):
        ChatMessage.objects.create(
            project_id=self.project.id, sender_type="user",
            sender_id=self.user.id, content="msg1",
        )
        ChatMessage.objects.create(
            project_id=self.project.id, sender_type="user",
            sender_id=self.user.id, content="msg2",
        )
        assert get_unprocessed_message_count(self.project_id_str) == 2

        # AI responds — count should reset
        ChatMessage.objects.create(
            project_id=self.project.id, sender_type="ai",
            content="AI response",
        )
        assert get_unprocessed_message_count(self.project_id_str) == 0

    def test_count_tracks_messages_after_ai_response(self):
        ChatMessage.objects.create(
            project_id=self.project.id, sender_type="user",
            sender_id=self.user.id, content="msg1",
        )
        ChatMessage.objects.create(
            project_id=self.project.id, sender_type="ai",
            content="AI response",
        )
        ChatMessage.objects.create(
            project_id=self.project.id, sender_type="user",
            sender_id=self.user.id, content="msg2",
        )
        assert get_unprocessed_message_count(self.project_id_str) == 1

    def test_nonexistent_idea_returns_zero(self):
        fake_id = str(uuid.uuid4())
        assert get_unprocessed_message_count(fake_id) == 0


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestRateLimitAPI(TestCase):
    """Integration tests for rate limit on POST /api/projects/:id/chat (T-2.11.01)."""

    def setUp(self):
        self.client = APIClient()
        self.user = _create_user(USER_1_ID, "ratelimit@test.local", "Rate Limiter")
        self.project = Project.objects.create(owner_id=self.user.id, title="Rate Test")
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.user.id)},
            format="json",
        )

    def _chat_url(self):
        return f"/api/projects/{self.project.id}/chat/"

    def test_rate_limit_locks_chat_at_cap(self):
        """T-2.11.01: Send chat_message_cap messages (default 5), 429 on next."""
        # Send 5 messages (default cap)
        for i in range(5):
            resp = self.client.post(
                self._chat_url(),
                {"content": f"Message {i}"},
                format="json",
            )
            assert resp.status_code == 201, f"Message {i} should succeed, got {resp.status_code}"

        # 6th message should be rate limited
        resp = self.client.post(
            self._chat_url(),
            {"content": "This should be blocked"},
            format="json",
        )
        assert resp.status_code == 429
        data = resp.json()
        assert data["error"]["code"] == "rate_limited"
        assert "locked" in data["error"]["message"].lower()

    def test_rate_limit_resets_after_ai_response(self):
        """T-2.11.02: AI response resets unprocessed count, allowing new messages."""
        # Fill to cap
        for i in range(5):
            self.client.post(
                self._chat_url(),
                {"content": f"Message {i}"},
                format="json",
            )

        # Verify we're rate limited
        resp = self.client.post(
            self._chat_url(),
            {"content": "Blocked"},
            format="json",
        )
        assert resp.status_code == 429

        # Simulate AI response (this is what ai.processing.complete leads to)
        ChatMessage.objects.create(
            project_id=self.project.id,
            sender_type="ai",
            content="AI has processed your messages.",
        )

        # Should be able to send again
        resp = self.client.post(
            self._chat_url(),
            {"content": "After AI response"},
            format="json",
        )
        assert resp.status_code == 201

    def test_counter_increments_per_message(self):
        """Unprocessed count increments for each successfully sent message."""
        project_id_str = str(self.project.id)

        self.client.post(self._chat_url(), {"content": "msg1"}, format="json")
        assert get_unprocessed_message_count(project_id_str) == 1

        self.client.post(self._chat_url(), {"content": "msg2"}, format="json")
        assert get_unprocessed_message_count(project_id_str) == 2

    def test_rate_limit_per_idea(self):
        """Rate limit counters are per-project."""
        idea2 = Project.objects.create(owner_id=self.user.id, title="Other Project")

        # Fill first project's counter
        for i in range(5):
            self.client.post(self._chat_url(), {"content": f"msg {i}"}, format="json")

        # Second project should still accept messages
        resp = self.client.post(
            f"/api/projects/{idea2.id}/chat/",
            {"content": "Different project"},
            format="json",
        )
        assert resp.status_code == 201
