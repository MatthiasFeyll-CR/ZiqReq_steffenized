import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User

USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000010")
ADMIN_ID = uuid.UUID("00000000-0000-0000-0000-000000000011")


def _create_user(
    user_id: uuid.UUID,
    email: str,
    display_name: str,
    roles: list[str] | None = None,
) -> User:
    return User.objects.create(
        id=user_id,
        email=email,
        first_name=display_name.split()[0],
        last_name=display_name.split()[-1],
        display_name=display_name,
        roles=roles or ["user"],
    )


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestGetNotificationPreferences(TestCase):
    """API-USER.02: GET /api/users/me/notification-preferences — 200 + categories."""

    def setUp(self):
        self.client = APIClient()
        self.user = _create_user(USER_ID, "prefs@test.local", "Prefs User")
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.user.id)},
            format="json",
        )

    def test_get_preferences_default(self):
        """All preferences default to True when empty."""
        response = self.client.get("/api/users/me/notification-preferences")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        cats = data["categories"]
        # Regular user sees Collaboration, Review, Chat (not Admin, not Review Management)
        assert "Collaboration" in cats
        assert "Review" in cats
        assert "Chat" in cats
        assert "Admin" not in cats
        assert "Review Management" not in cats
        # All values default to True
        for prefs in cats.values():
            for value in prefs["preferences"].values():
                assert value is True

    def test_get_preferences_with_stored_values(self):
        """Stored False values are reflected; missing keys default True."""
        self.user.email_notification_preferences = {
            "collaboration_invitation": False,
            "chat_mention": False,
        }
        self.user.save(update_fields=["email_notification_preferences"])

        response = self.client.get("/api/users/me/notification-preferences")
        assert response.status_code == 200
        cats = response.json()["categories"]
        assert cats["Collaboration"]["preferences"]["collaboration_invitation"] is False
        assert cats["Collaboration"]["preferences"]["collaborator_joined"] is True
        assert cats["Chat"]["preferences"]["chat_mention"] is False

    def test_get_preferences_unauthenticated(self):
        """Unauthenticated request returns 401."""
        client = APIClient()
        response = client.get("/api/users/me/notification-preferences")
        assert response.status_code == 401


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestGetNotificationPreferencesAdmin(TestCase):
    """Admin users see Admin category."""

    def setUp(self):
        self.client = APIClient()
        self.admin = _create_user(
            ADMIN_ID, "admin@test.local", "Admin User", roles=["user", "admin"]
        )
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.admin.id)},
            format="json",
        )

    def test_admin_sees_admin_category(self):
        response = self.client.get("/api/users/me/notification-preferences")
        assert response.status_code == 200
        cats = response.json()["categories"]
        assert "Admin" in cats
        assert "monitoring_alert" in cats["Admin"]["preferences"]
        assert cats["Admin"]["preferences"]["monitoring_alert"] is True


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestUpdateNotificationPreferences(TestCase):
    """API-USER.03: PATCH /api/users/me/notification-preferences — 200."""

    def setUp(self):
        self.client = APIClient()
        self.user = _create_user(USER_ID, "prefs@test.local", "Prefs User")
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.user.id)},
            format="json",
        )

    def test_update_preferences(self):
        """PATCH merges new preferences into stored prefs."""
        response = self.client.patch(
            "/api/users/me/notification-preferences",
            {"collaboration_invitation": False, "review_state_changed": True},
            format="json",
        )
        assert response.status_code == 200
        cats = response.json()["categories"]
        assert cats["Collaboration"]["preferences"]["collaboration_invitation"] is False
        assert cats["Review"]["preferences"]["review_state_changed"] is True

        # Verify persisted
        self.user.refresh_from_db()
        assert self.user.email_notification_preferences["collaboration_invitation"] is False
        assert self.user.email_notification_preferences["review_state_changed"] is True

    def test_partial_merge_preserves_existing(self):
        """Updating one key doesn't reset other stored keys."""
        self.user.email_notification_preferences = {"chat_mention": False}
        self.user.save(update_fields=["email_notification_preferences"])

        response = self.client.patch(
            "/api/users/me/notification-preferences",
            {"collaboration_invitation": False},
            format="json",
        )
        assert response.status_code == 200

        self.user.refresh_from_db()
        assert self.user.email_notification_preferences["chat_mention"] is False
        assert self.user.email_notification_preferences["collaboration_invitation"] is False

    def test_update_unauthenticated(self):
        """Unauthenticated PATCH returns 401."""
        client = APIClient()
        response = client.patch(
            "/api/users/me/notification-preferences",
            {"collaboration_invitation": False},
            format="json",
        )
        assert response.status_code == 401
