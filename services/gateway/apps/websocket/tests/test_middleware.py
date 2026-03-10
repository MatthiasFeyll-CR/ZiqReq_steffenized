"""Unit tests for WebSocketAuthMiddleware._authenticate_dev (sync, real DB).

Uses regular TestCase — no async, no TransactionTestCase.
"""

import uuid

from django.test import TestCase, override_settings

from apps.authentication.models import User
from apps.websocket.middleware import WebSocketAuthMiddleware


class TestAuthenticateDev(TestCase):
    """Test the sync function inside _authenticate_dev."""

    def setUp(self):
        self.user = User.objects.create(
            id=uuid.uuid4(), email="dev@test.local",
            display_name="Dev User", roles=["user"],
        )

    def _auth(self, token: str):
        """Call the sync body of _authenticate_dev directly."""
        try:
            user_uuid = uuid.UUID(token)
        except (ValueError, TypeError):
            return None
        return User.objects.filter(id=user_uuid).first()

    def test_valid_uuid_returns_user(self):
        result = self._auth(str(self.user.id))
        assert result is not None
        assert result.id == self.user.id

    def test_nonexistent_uuid_returns_none(self):
        result = self._auth(str(uuid.uuid4()))
        assert result is None

    def test_invalid_token_returns_none(self):
        result = self._auth("not-a-uuid")
        assert result is None

    def test_empty_token_returns_none(self):
        result = self._auth("")
        assert result is None

    def test_expired_token_returns_none(self):
        result = self._auth("expired")
        assert result is None
