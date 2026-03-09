import json
import logging
import time
from urllib.request import urlopen

import jwt
from django.conf import settings

logger = logging.getLogger(__name__)

_jwks_cache: dict[str, object] = {"keys": None, "fetched_at": 0.0}
JWKS_CACHE_DURATION = 86400  # 24 hours


def _get_jwks_url() -> str:
    tenant_id = settings.AZURE_AD_TENANT_ID
    return f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"


def _fetch_jwks() -> dict:
    now = time.time()
    if _jwks_cache["keys"] and (now - _jwks_cache["fetched_at"]) < JWKS_CACHE_DURATION:  # type: ignore[operator]
        return _jwks_cache["keys"]  # type: ignore[return-value]

    url = _get_jwks_url()
    with urlopen(url, timeout=10) as response:  # noqa: S310
        data = json.loads(response.read())

    _jwks_cache["keys"] = data
    _jwks_cache["fetched_at"] = now
    return data


def _get_signing_key(token: str) -> jwt.algorithms.RSAAlgorithm:
    jwks = _fetch_jwks()
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")

    for key_data in jwks.get("keys", []):
        if key_data.get("kid") == kid:
            return jwt.algorithms.RSAAlgorithm.from_jwk(key_data)

    raise jwt.InvalidTokenError("No matching signing key found in JWKS")


def validate_azure_ad_token(token: str) -> dict:
    """Validate an Azure AD JWT and return decoded claims.

    Raises jwt.InvalidTokenError or subclasses on failure.
    """
    public_key = _get_signing_key(token)
    tenant_id = settings.AZURE_AD_TENANT_ID
    client_id = settings.AZURE_AD_CLIENT_ID

    decoded = jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        audience=client_id,
        issuer=f"https://login.microsoftonline.com/{tenant_id}/v2.0",
    )
    return decoded


def extract_user_data(claims: dict) -> dict:
    """Extract user data from Azure AD token claims."""
    role_mapping = getattr(settings, "AZURE_AD_ROLE_MAPPING", {})

    groups = claims.get("groups", [])
    roles = ["user"]  # everyone gets 'user' role
    for group_id in groups:
        if group_id in role_mapping:
            role = role_mapping[group_id]
            if role not in roles:
                roles.append(role)

    return {
        "id": claims.get("oid", claims.get("sub", "")),
        "email": claims.get("preferred_username", claims.get("email", "")),
        "first_name": claims.get("given_name", ""),
        "last_name": claims.get("family_name", ""),
        "display_name": claims.get("name", ""),
        "roles": roles,
    }
