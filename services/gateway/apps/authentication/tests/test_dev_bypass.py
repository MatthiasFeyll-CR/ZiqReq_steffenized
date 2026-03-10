import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User

DEV_USERS = [
    {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
        "email": "dev1@ziqreq.local",
        "first_name": "Dev",
        "last_name": "User1",
        "display_name": "Dev User 1",
        "roles": ["user"],
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000002"),
        "email": "dev2@ziqreq.local",
        "first_name": "Dev",
        "last_name": "User2",
        "display_name": "Dev User 2",
        "roles": ["user"],
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000003"),
        "email": "dev3@ziqreq.local",
        "first_name": "Dev",
        "last_name": "User3",
        "display_name": "Dev User 3",
        "roles": ["user", "reviewer"],
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000004"),
        "email": "dev4@ziqreq.local",
        "first_name": "Dev",
        "last_name": "User4",
        "display_name": "Dev User 4",
        "roles": ["user", "admin"],
    },
]


class TestDevBypass(TestCase):
    """Tests for dev bypass authentication endpoints."""

    def setUp(self):
        self.client = APIClient()
        for user_data in DEV_USERS:
            User.objects.create(**user_data)

    @override_settings(DEBUG=True, AUTH_BYPASS=True)
    def test_dev_users_endpoint_in_bypass_mode(self):
        """T-7.1.01: Dev users endpoint available in bypass mode."""
        response = self.client.get("/api/auth/dev-users")
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert len(data["users"]) >= 4
        emails = {u["email"] for u in data["users"]}
        for dev_user in DEV_USERS:
            assert dev_user["email"] in emails

    @override_settings(DEBUG=False, AUTH_BYPASS=False)
    def test_dev_users_endpoint_404_in_production(self):
        """T-7.1.02: Dev users endpoint 404 in production mode."""
        response = self.client.get("/api/auth/dev-users")
        assert response.status_code == 404

    @override_settings(DEBUG=True, AUTH_BYPASS=True)
    def test_dev_login_creates_session(self):
        """T-7.1.03: Dev login creates session."""
        user_id = str(DEV_USERS[0]["id"])
        response = self.client.post(
            "/api/auth/dev-login",
            {"user_id": user_id},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == "dev1@ziqreq.local"
        assert data["display_name"] == "Dev User 1"
        assert data["roles"] == ["user"]
        assert self.client.session["user_id"] == user_id

    @override_settings(DEBUG=True, AUTH_BYPASS=False)
    def test_dev_login_404_without_auth_bypass(self):
        """Dev login returns 404 if AUTH_BYPASS is False."""
        response = self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(DEV_USERS[0]["id"])},
            format="json",
        )
        assert response.status_code == 404

    @override_settings(DEBUG=True, AUTH_BYPASS=True)
    def test_dev_switch_works(self):
        """POST /api/auth/dev-switch switches dev user."""
        user_id = str(DEV_USERS[2]["id"])
        response = self.client.post(
            "/api/auth/dev-switch",
            {"user_id": user_id},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["roles"] == ["user", "reviewer"]

    @override_settings(DEBUG=False, AUTH_BYPASS=True)
    def test_dev_switch_404_without_debug(self):
        """POST /api/auth/dev-switch returns 404 if DEBUG is False."""
        response = self.client.post(
            "/api/auth/dev-switch",
            {"user_id": str(DEV_USERS[0]["id"])},
            format="json",
        )
        assert response.status_code == 404

    @override_settings(DEBUG=True, AUTH_BYPASS=True)
    def test_dev_login_nonexistent_user_returns_404(self):
        """Dev login with invalid user_id returns 404."""
        response = self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(uuid.uuid4())},
            format="json",
        )
        assert response.status_code == 404
