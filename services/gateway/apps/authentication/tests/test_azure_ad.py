import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt as pyjwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.authentication.models import User

TENANT_ID = "test-tenant-id"
CLIENT_ID = "test-client-id"


def _generate_rsa_keypair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
    return private_pem, public_pem, private_key, public_key


def _create_token(private_key, claims: dict, headers: dict | None = None) -> str:
    return pyjwt.encode(claims, private_key, algorithm="RS256", headers=headers or {})


PRIVATE_PEM, PUBLIC_PEM, PRIVATE_KEY, PUBLIC_KEY = _generate_rsa_keypair()


def _mock_get_signing_key(token: str):
    return PUBLIC_KEY


@pytest.mark.django_db
@override_settings(
    DEBUG=False,
    AUTH_BYPASS=False,
    AZURE_AD_TENANT_ID=TENANT_ID,
    AZURE_AD_CLIENT_ID=CLIENT_ID,
)
class TestAzureADAuth(TestCase):
    """Tests for Azure AD token validation."""

    def setUp(self):
        self.client = APIClient()

    def _valid_claims(self, **overrides) -> dict:
        now = datetime.now(tz=timezone.utc)
        claims = {
            "oid": str(uuid.uuid4()),
            "preferred_username": "testuser@example.com",
            "given_name": "Test",
            "family_name": "User",
            "name": "Test User",
            "groups": [],
            "iss": f"https://login.microsoftonline.com/{TENANT_ID}/v2.0",
            "aud": CLIENT_ID,
            "exp": int((now + timedelta(hours=1)).timestamp()),
            "iat": int(now.timestamp()),
            "nbf": int(now.timestamp()),
        }
        claims.update(overrides)
        return claims

    @patch("apps.authentication.azure_ad._get_signing_key", side_effect=_mock_get_signing_key)
    def test_valid_token_validates_and_syncs(self, mock_key):
        """T-7.2.01: Valid Azure AD token validates and syncs user."""
        claims = self._valid_claims()
        token = _create_token(PRIVATE_KEY, claims)

        response = self.client.post(
            "/api/auth/validate",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "testuser@example.com"
        assert data["first_name"] == "Test"
        assert data["last_name"] == "User"
        assert data["display_name"] == "Test User"

        user = User.objects.get(id=claims["oid"])
        assert user.email == "testuser@example.com"

    @patch("apps.authentication.azure_ad._get_signing_key", side_effect=_mock_get_signing_key)
    def test_expired_token_returns_401(self, mock_key):
        """T-7.2.02: Expired token returns 401."""
        now = datetime.now(tz=timezone.utc)
        claims = self._valid_claims(
            exp=int((now - timedelta(hours=1)).timestamp()),
        )
        token = _create_token(PRIVATE_KEY, claims)

        response = self.client.post(
            "/api/auth/validate",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "TOKEN_INVALID"

    @patch("apps.authentication.azure_ad._get_signing_key", side_effect=_mock_get_signing_key)
    @override_settings(
        AZURE_AD_ROLE_MAPPING={
            "group-reviewers": "reviewer",
            "group-admins": "admin",
        },
    )
    def test_roles_synced_from_ad_groups(self, mock_key):
        """T-7.2.03: Roles synced from AD groups on login."""
        claims = self._valid_claims(
            groups=["group-reviewers", "group-admins"],
        )
        token = _create_token(PRIVATE_KEY, claims)

        response = self.client.post(
            "/api/auth/validate",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        assert response.status_code == 200
        data = response.json()
        assert "user" in data["roles"]
        assert "reviewer" in data["roles"]
        assert "admin" in data["roles"]

        user = User.objects.get(id=claims["oid"])
        assert "user" in user.roles
        assert "reviewer" in user.roles
        assert "admin" in user.roles

    def test_missing_token_returns_401(self):
        """Missing Authorization header returns 401."""
        response = self.client.post("/api/auth/validate")
        assert response.status_code == 401

    def test_malformed_token_returns_401(self):
        """Malformed token returns 401."""
        response = self.client.post(
            "/api/auth/validate",
            HTTP_AUTHORIZATION="Bearer not-a-valid-jwt",
        )
        assert response.status_code == 401

    @patch("apps.authentication.azure_ad._get_signing_key", side_effect=_mock_get_signing_key)
    def test_validate_upserts_existing_user(self, mock_key):
        """Validate endpoint updates existing user data on re-login."""
        user_id = str(uuid.uuid4())
        User.objects.create(
            id=user_id,
            email="old@example.com",
            first_name="Old",
            last_name="Name",
            display_name="Old Name",
            roles=["user"],
        )

        claims = self._valid_claims(
            oid=user_id,
            preferred_username="new@example.com",
            given_name="New",
            family_name="Name",
            name="New Name",
        )
        token = _create_token(PRIVATE_KEY, claims)

        response = self.client.post(
            "/api/auth/validate",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        assert response.status_code == 200
        user = User.objects.get(id=user_id)
        assert user.email == "new@example.com"
        assert user.first_name == "New"
        assert user.display_name == "New Name"
