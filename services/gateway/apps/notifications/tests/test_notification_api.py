import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.notifications.models import Notification

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


def _create_notification(user_id: uuid.UUID, **kwargs) -> Notification:
    defaults = {
        "user_id": user_id,
        "event_type": "collaboration_invitation",
        "title": "Test notification",
        "body": "Test body",
    }
    defaults.update(kwargs)
    return Notification.objects.create(**defaults)


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestListNotifications(TestCase):
    """API-NOTIF.01: GET /api/notifications — Happy path — 200 + paginated list."""

    def setUp(self):
        self.client = APIClient()
        self.user = _create_user(USER_1_ID, "user1@test.local", "User One")
        self.other = _create_user(USER_2_ID, "user2@test.local", "User Two")
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.user.id)},
            format="json",
        )

    def test_list_notifications(self):
        _create_notification(self.user.id, title="Notif 1")
        _create_notification(self.user.id, title="Notif 2", is_read=True)
        _create_notification(self.other.id, title="Other user notif")

        response = self.client.get("/api/notifications/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["notifications"]) == 2
        assert "unread_count" in data
        assert "count" in data
        assert data["count"] == 2
        assert data["page"] == 1
        assert data["page_size"] == 20

    def test_list_unread_only(self):
        _create_notification(self.user.id, title="Unread")
        _create_notification(self.user.id, title="Read", is_read=True)

        response = self.client.get("/api/notifications/?unread_only=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data["notifications"]) == 1
        assert data["notifications"][0]["title"] == "Unread"

    def test_pagination(self):
        for i in range(5):
            _create_notification(self.user.id, title=f"Notif {i}")

        response = self.client.get("/api/notifications/?page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["notifications"]) == 2
        assert data["count"] == 5

    def test_unread_count_excludes_actioned(self):
        _create_notification(self.user.id, title="Unread")
        _create_notification(self.user.id, title="Actioned", action_taken=True)

        response = self.client.get("/api/notifications/")
        data = response.json()
        assert data["unread_count"] == 1

    def test_unauthenticated(self):
        client = APIClient()
        response = client.get("/api/notifications/")
        assert response.status_code == 401


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestUnreadCount(TestCase):
    """API-NOTIF.02: GET /api/notifications/unread-count — Happy path — 200 + count."""

    def setUp(self):
        self.client = APIClient()
        self.user = _create_user(USER_1_ID, "user1@test.local", "User One")
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.user.id)},
            format="json",
        )

    def test_unread_count(self):
        _create_notification(self.user.id)
        _create_notification(self.user.id)
        _create_notification(self.user.id, is_read=True)

        response = self.client.get("/api/notifications/unread-count")
        assert response.status_code == 200
        data = response.json()
        assert data["unread_count"] == 2

    def test_unread_count_zero(self):
        response = self.client.get("/api/notifications/unread-count")
        assert response.status_code == 200
        assert response.json()["unread_count"] == 0


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestMarkNotification(TestCase):
    """API-NOTIF.03: PATCH /api/notifications/:id — Happy path — 200."""

    def setUp(self):
        self.client = APIClient()
        self.user = _create_user(USER_1_ID, "user1@test.local", "User One")
        self.other = _create_user(USER_2_ID, "user2@test.local", "User Two")
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.user.id)},
            format="json",
        )

    def test_mark_as_read(self):
        notif = _create_notification(self.user.id)
        response = self.client.patch(
            f"/api/notifications/{notif.id}",
            {"is_read": True},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_read"] is True

        notif.refresh_from_db()
        assert notif.is_read is True

    def test_mark_action_taken(self):
        notif = _create_notification(self.user.id)
        response = self.client.patch(
            f"/api/notifications/{notif.id}",
            {"action_taken": True},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["action_taken"] is True

    def test_not_found_wrong_user(self):
        notif = _create_notification(self.other.id)
        response = self.client.patch(
            f"/api/notifications/{notif.id}",
            {"is_read": True},
            format="json",
        )
        assert response.status_code == 404

    def test_not_found_nonexistent(self):
        fake_id = uuid.uuid4()
        response = self.client.patch(
            f"/api/notifications/{fake_id}",
            {"is_read": True},
            format="json",
        )
        assert response.status_code == 404


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestMarkAllRead(TestCase):
    """API-NOTIF.04: POST /api/notifications/mark-all-read — Happy path — 200."""

    def setUp(self):
        self.client = APIClient()
        self.user = _create_user(USER_1_ID, "user1@test.local", "User One")
        self.other = _create_user(USER_2_ID, "user2@test.local", "User Two")
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.user.id)},
            format="json",
        )

    def test_mark_all_read(self):
        _create_notification(self.user.id, title="N1")
        _create_notification(self.user.id, title="N2")
        _create_notification(self.other.id, title="Other")

        response = self.client.post("/api/notifications/mark-all-read")
        assert response.status_code == 200
        assert response.json()["message"] == "All notifications marked as read"

        assert Notification.objects.filter(user_id=self.user.id, is_read=False).count() == 0
        assert Notification.objects.filter(user_id=self.other.id, is_read=False).count() == 1
