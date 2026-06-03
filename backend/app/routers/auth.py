"""Auth router for Neon Auth metadata and current-user resolution."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.auth import get_optional_principal, require_principal
from app.config import get_settings
from app.db import repositories

router = APIRouter(prefix="/v1/auth", tags=["auth"])


class SignUpRequest(BaseModel):
    email: str
    password: str
    full_name: str = ""


class SignInRequest(BaseModel):
    email: str
    password: str


@router.get("/config")
async def auth_config() -> dict:
    settings = get_settings()
    return {
        "provider": "neon-auth",
        "configured": bool(settings.neon_auth_url.strip()),
        "auth_required": settings.auth_required,
    }


@router.get("/me")
async def me(request: Request) -> dict:
    db = request.app.state.db
    principal = require_principal(request)
    if db.enabled:
        profile = await repositories.get_or_create_profile_from_claims(db, principal.claims)
        return {
            "claims": principal.claims,
            "profile": _serialize_row(profile),
        }
    return {"claims": principal.claims, "profile": None}


@router.post("/signup")
async def signup(payload: SignUpRequest) -> dict:
    raise HTTPException(
        status_code=501,
        detail="Use the Neon Auth client on /auth for signup. Backend password proxying is intentionally disabled.",
    )


@router.post("/login")
async def login(payload: SignInRequest) -> dict:
    raise HTTPException(
        status_code=501,
        detail="Use the Neon Auth client on /auth for login. Backend password proxying is intentionally disabled.",
    )


@router.get("/linkedin/profile")
async def linkedin_profile(request: Request) -> dict:
    principal = get_optional_principal(request)
    if principal is None:
        raise HTTPException(status_code=401, detail="Authentication required.")
    return {
        "full_name": principal.full_name,
        "email": principal.email,
        "linkedin_url": "",
        "country_of_origin": "",
        "target_university": "",
    }


def _serialize_row(row: dict) -> dict:
    result = dict(row)
    for key, value in list(result.items()):
        if hasattr(value, "isoformat"):
            result[key] = value.isoformat()
        else:
            result[key] = str(value) if key == "id" else value
    return result
