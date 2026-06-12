"""Auth router for Neon Auth metadata and current-user resolution."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.auth import get_optional_principal, require_principal
from app.config import get_settings
from app.db import repositories
from app.utils.stages import normalize_stage

router = APIRouter(prefix="/v1/auth", tags=["auth"])


class SignUpRequest(BaseModel):
    email: str
    password: str
    full_name: str = ""


class SignInRequest(BaseModel):
    email: str
    password: str


class StageUpdateRequest(BaseModel):
    stage: str


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


@router.patch("/me/stage")
async def update_my_stage(payload: StageUpdateRequest, request: Request) -> dict:
    db = request.app.state.db
    principal = require_principal(request)
    target_stage = normalize_stage(payload.stage, allow_mentor=False)
    if target_stage is None:
        raise HTTPException(status_code=400, detail="Stage must be newcomer, settler, or local.")
    if not db.enabled:
        raise HTTPException(status_code=503, detail="Database persistence is not configured.")

    await repositories.get_or_create_profile_from_claims(db, principal.claims)
    profile = await repositories.advance_user_stage(db, auth_user_id=principal.auth_user_id, stage=target_stage)
    return {"profile": _serialize_row(profile)}


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
    linkedin_url = _claim_value(
        principal.claims,
        "linkedin_url",
        "profile",
        "publicProfileUrl",
        "localizedProfileUrl",
    )
    full_name = principal.full_name or " ".join(
        part for part in (
            _claim_value(principal.claims, "given_name", "first_name"),
            _claim_value(principal.claims, "family_name", "last_name"),
        )
        if part
    )
    provider = _claim_value(principal.claims, "provider", "provider_id", "identity_provider", "idp").lower()
    return {
        "source": "linkedin" if "linkedin" in provider else "account",
        "full_name": full_name,
        "email": principal.email,
        "linkedin_url": linkedin_url if "linkedin.com" in linkedin_url else "",
        "country_of_origin": _claim_value(principal.claims, "country_of_origin", "country"),
        "target_university": _claim_value(principal.claims, "target_university", "school", "university"),
    }


def _serialize_row(row: dict) -> dict:
    result = dict(row)
    for key, value in list(result.items()):
        if hasattr(value, "isoformat"):
            result[key] = value.isoformat()
        else:
            result[key] = str(value) if key == "id" else value
    return result


def _claim_value(claims: dict, *keys: str) -> str:
    for key in keys:
        value = claims.get(key)
        if value:
            return str(value)
    return ""
