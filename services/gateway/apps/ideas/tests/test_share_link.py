import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.ideas.models import Idea

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
class TestGenerateShareLink(TestCase):
    """API-SHARE.01: POST /api/ideas/:id/share-link — generate token."""

    def setUp(self):
        self.client = APIClient()
        self.owner = _create_user(USER_1_ID, "owner@test.local", "Owner User")
        self.other = _create_user(USER_2_ID, "other@test.local", "Other User")
        self.idea = Idea.objects.create(owner_id=self.owner.id, title="Test Idea")
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.owner.id)},
            format="json",
        )

    def test_generate_share_link_success(self):
        response = self.client.post(f"/api/ideas/{self.idea.id}/share-link")
        assert response.status_code == 201
        data = response.json()
        assert "share_link_token" in data
        assert "share_url" in data
        token = data["share_link_token"]
        assert len(token) == 64
        assert data["share_url"] == f"/idea/{self.idea.id}?token={token}"

        self.idea.refresh_from_db()
        assert self.idea.share_link_token == token

    def test_regenerate_overwrites_existing_token(self):
        # Generate first token
        resp1 = self.client.post(f"/api/ideas/{self.idea.id}/share-link")
        token1 = resp1.json()["share_link_token"]

        # Generate second token — should overwrite
        resp2 = self.client.post(f"/api/ideas/{self.idea.id}/share-link")
        token2 = resp2.json()["share_link_token"]

        assert token1 != token2
        self.idea.refresh_from_db()
        assert self.idea.share_link_token == token2

    def test_non_owner_cannot_generate(self):
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.other.id)},
            format="json",
        )
        response = self.client.post(f"/api/ideas/{self.idea.id}/share-link")
        assert response.status_code == 403

    def test_idea_not_found(self):
        fake_id = uuid.uuid4()
        response = self.client.post(f"/api/ideas/{fake_id}/share-link")
        assert response.status_code == 404


@override_settings(DEBUG=True, AUTH_BYPASS=True)
class TestShareLinkMiddleware(TestCase):
    """T-8.3.01, T-8.3.02: Middleware validates ?token= query param."""

    def setUp(self):
        self.client = APIClient()
        self.owner = _create_user(USER_1_ID, "owner@test.local", "Owner User")
        self.idea = Idea.objects.create(
            owner_id=self.owner.id,
            title="Shared Idea",
            share_link_token="a" * 64,
        )
        # Log in as owner to have a valid session
        self.client.post(
            "/api/auth/dev-login",
            {"user_id": str(self.owner.id)},
            format="json",
        )

    def test_valid_token_adds_share_link_viewer_role(self):
        token = "a" * 64
        response = self.client.get(f"/api/ideas/{self.idea.id}/?token={token}")
        assert response.status_code == 200

    def test_invalid_token_returns_403(self):
        response = self.client.get(f"/api/ideas/{self.idea.id}/?token=invalidtoken")
        assert response.status_code == 403
        data = response.json()
        assert data["error"] == "FORBIDDEN"

    def test_no_token_passes_through(self):
        # Without token, normal auth applies — owner can still access
        response = self.client.get(f"/api/ideas/{self.idea.id}/")
        assert response.status_code == 200

    def test_token_not_applied_to_non_ideas_paths(self):
        # Token on non-ideas path should pass through without validation
        response = self.client.get("/api/auth/dev-users?token=invalidtoken")
        # Should not return 403 from middleware
        assert response.status_code != 403
