"""Tests for rate limit integration (US-010, T-2.11.01, T-2.11.02)."""

import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.chat.views import (
    _rate_limit_counters,
    get_rate_limit_counter,
    increment_rate_limit_counter,
    reset_rate_limit_counter,
)
from apps.ideas.models import Idea

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
class TestRateLimitCounters(TestCase):
    """Unit tests for rate limit counter functions."""

    def setUp(self):
        _rate_limit_counters.clear()

    def test_counter_starts_at_zero(self):
        assert get_rate_limit_counter("idea-1") == 0

    def test_increment_returns_new_count(self):
        assert increment_rate_limit_counter("idea-1") == 1
        assert increment_rate_limit_counter("idea-1") == 2

    def test_reset_clears_counter(self):
        increment_rate_limit_counter("idea-1")
        increment_rate_limit_counter("idea-1")
        reset_rate_limit_counter("idea-1")
        assert get_rate_limit_counter("idea-1") == 0

    def test_reset_nonexistent_is_noop(self):
        reset_rate_limit_counter("nonexistent")
        assert get_rate_limit_counter("nonexistent") == 0


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestRateLimitAPI(TestCase):
    """Integration tests for rate limit on POST /api/ideas/:id/chat (T-2.11.01)."""

    def setUp(self):
        _rate_limit_counters.clear()
        self.client = APIClient()
        self.user = _create_user(USER_1_ID, "ratelimit@test.local", "Rate Limiter")
        self.idea = Idea.objects.create(owner_id=self.user.id, title="Rate Test")
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.user.id)},
            format="json",
        )

    def _chat_url(self):
        return f"/api/ideas/{self.idea.id}/chat"

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

    def test_rate_limit_resets_on_complete(self):
        """T-2.11.02: ai.processing.complete resets counter to 0."""
        idea_id_str = str(self.idea.id)

        # Fill counter to cap
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

        # Reset (simulating ai.processing.complete)
        reset_rate_limit_counter(idea_id_str)

        # Should be able to send again
        resp = self.client.post(
            self._chat_url(),
            {"content": "After reset"},
            format="json",
        )
        assert resp.status_code == 201

    def test_counter_increments_per_message(self):
        """Counter increments for each successfully sent message."""
        idea_id_str = str(self.idea.id)

        self.client.post(self._chat_url(), {"content": "msg1"}, format="json")
        assert get_rate_limit_counter(idea_id_str) == 1

        self.client.post(self._chat_url(), {"content": "msg2"}, format="json")
        assert get_rate_limit_counter(idea_id_str) == 2

    def test_rate_limit_per_idea(self):
        """Rate limit counters are per-idea."""
        idea2 = Idea.objects.create(owner_id=self.user.id, title="Other Idea")

        # Fill first idea's counter
        for i in range(5):
            self.client.post(self._chat_url(), {"content": f"msg {i}"}, format="json")

        # Second idea should still accept messages
        resp = self.client.post(
            f"/api/ideas/{idea2.id}/chat",
            {"content": "Different idea"},
            format="json",
        )
        assert resp.status_code == 201
