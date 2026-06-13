"""JWT authentication helpers for Neon Auth / JWKS-based providers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException, Request
from jwt import PyJWKClient, decode
from jwt.exceptions import InvalidTokenError

from app.config import Settings, get_settings


@dataclass(frozen=True)
class AuthPrincipal:
    claims: dict[str, Any]

    @property
    def auth_user_id(self) -> str:
        return str(self.claims.get("sub") or self.claims.get("id") or self.claims.get("user_id") or "")

    @property
    def email(self) -> str:
        return str(self.claims.get("email") or "")

    @property
    def full_name(self) -> str:
        return str(self.claims.get("name") or self.claims.get("full_name") or "")


_jwks_clients: dict[str, PyJWKClient] = {}


PUBLIC_V1_PREFIXES = (
    "/v1/auth",
    "/v1/profile/match",
    "/v1/plan/generate",
    "/v1/bridge/explain",
    "/v1/graph/subgraph",
    "/v1/pre-arrival/checklist",
    "/v1/feed",
)


def is_public_api_path(path: str) -> bool:
    if not path.startswith("/v1/"):
        return True
    return any(path.startswith(prefix) for prefix in PUBLIC_V1_PREFIXES)


def bearer_token_from_header(auth_header: str | None) -> str:
    if not auth_header:
        return ""
    scheme, _, token = auth_header.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        return ""
    return token.strip()


def verify_jwt_token(token: str, settings: Settings | None = None) -> AuthPrincipal:
    settings = settings or get_settings()
    jwks_url = settings.jwt_jwks_url
    if not jwks_url:
        raise HTTPException(status_code=401, detail="JWT verification is not configured.")

    try:
        client = _jwks_clients.setdefault(jwks_url, PyJWKClient(jwks_url))
        signing_key = client.get_signing_key_from_jwt(token)
        kwargs: dict[str, Any] = {
            "algorithms": ["RS256", "ES256", "EdDSA"],
            "options": {"verify_aud": bool(settings.neon_auth_audience.strip())},
        }
        if settings.neon_auth_audience.strip():
            kwargs["audience"] = settings.neon_auth_audience.strip()
        if settings.neon_auth_issuer.strip():
            kwargs["issuer"] = settings.neon_auth_issuer.strip()
        claims = decode(token, signing_key.key, **kwargs)
    except InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid authentication token.") from exc
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Unable to verify authentication token.") from exc

    principal = AuthPrincipal(claims=dict(claims))
    if not principal.auth_user_id:
        raise HTTPException(status_code=401, detail="Authentication token is missing subject.")
    return principal


def get_optional_principal(request: Request) -> AuthPrincipal | None:
    principal = getattr(request.state, "user", None)
    return principal if isinstance(principal, AuthPrincipal) else None


def require_principal(request: Request) -> AuthPrincipal:
    principal = get_optional_principal(request)
    if principal is None:
        raise HTTPException(status_code=401, detail="Authentication required.")
    return principal
