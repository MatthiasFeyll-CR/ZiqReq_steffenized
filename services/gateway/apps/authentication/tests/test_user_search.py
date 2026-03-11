import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User

USER_1_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
USER_2_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
USER_3_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")
USER_4_ID = uuid.UUID("00000000-0000-0000-0000-000000000004")


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
class TestUserSearchByNameAndEmail(TestCase):
    """API-USERS.01: GET /api/users/search — search by display_name and email."""

    def setUp(self):
        self.client = APIClient()
        self.current_user = _create_user(USER_1_ID, "current@test.local", "Current User")
        self.alice = _create_user(USER_2_ID, "alice@example.com", "Alice Smith")
        self.bob = _create_user(USER_3_ID, "bob@example.com", "Bob Jones")
        self.charlie = _create_user(USER_4_ID, "charlie@example.com", "Charlie Alpha")
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.current_user.id)},
            format="json",
        )

    def test_search_by_display_name(self):
        response = self.client.get("/api/users/search", {"q": "Alice"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["display_name"] == "Alice Smith"

    def test_search_by_email(self):
        response = self.client.get("/api/users/search", {"q": "bob@"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["email"] == "bob@example.com"

    def test_search_case_insensitive(self):
        response = self.client.get("/api/users/search", {"q": "alice"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["display_name"] == "Alice Smith"

    def test_search_excludes_current_user(self):
        response = self.client.get("/api/users/search", {"q": "Current"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_search_ordered_by_display_name(self):
        response = self.client.get("/api/users/search", {"q": "example.com"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        names = [u["display_name"] for u in data]
        assert names == ["Alice Smith", "Bob Jones", "Charlie Alpha"]

    def test_search_returns_user_fields(self):
        response = self.client.get("/api/users/search", {"q": "Alice"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        user = data[0]
        assert "id" in user
        assert "display_name" in user
        assert "email" in user
        assert "roles" in user


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestUserSearchMinLength(TestCase):
    """API-USERS.02: GET /api/users/search — min query length validation."""

    def setUp(self):
        self.client = APIClient()
        self.user = _create_user(USER_1_ID, "user@test.local", "Test User")
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.user.id)},
            format="json",
        )

    def test_query_too_short_returns_400(self):
        response = self.client.get("/api/users/search", {"q": "a"})
        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "BAD_REQUEST"

    def test_empty_query_returns_400(self):
        response = self.client.get("/api/users/search", {"q": ""})
        assert response.status_code == 400

    def test_missing_query_returns_400(self):
        response = self.client.get("/api/users/search")
        assert response.status_code == 400

    def test_two_char_query_is_valid(self):
        response = self.client.get("/api/users/search", {"q": "Te"})
        assert response.status_code == 200


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestUserSearchMaxResults(TestCase):
    """API-USERS.03: GET /api/users/search — max 20 results."""

    def setUp(self):
        self.client = APIClient()
        self.user = _create_user(USER_1_ID, "searcher@test.local", "Searcher User")
        # Create 25 users matching "testuser"
        for i in range(25):
            User.objects.create(
                id=uuid.uuid4(),
                email=f"testuser{i:02d}@example.com",
                first_name="TestUser",
                last_name=f"Number{i:02d}",
                display_name=f"TestUser Number{i:02d}",
                roles=["user"],
            )
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.user.id)},
            format="json",
        )

    def test_max_20_results(self):
        response = self.client.get("/api/users/search", {"q": "TestUser"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 20
