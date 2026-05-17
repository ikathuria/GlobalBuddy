"""Auth router — stub wired for Milestone 5 (LinkedIn OAuth) and Milestone 4 (Supabase Auth).

Endpoints here will delegate to Supabase Auth once SUPABASE_URL and
SUPABASE_SERVICE_ROLE_KEY are configured. Until then they return 501.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/v1/auth", tags=["auth"])


class SignUpRequest(BaseModel):
    email: str
    password: str
    full_name: str = ""


class SignInRequest(BaseModel):
    email: str
    password: str


@router.post("/signup")
async def signup(payload: SignUpRequest) -> dict:
    # TODO (Milestone 4): delegate to supabase.auth.admin.create_user(...)
    raise HTTPException(status_code=501, detail="Supabase Auth not yet configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")


@router.post("/login")
async def login(payload: SignInRequest) -> dict:
    # TODO (Milestone 4): delegate to supabase.auth.sign_in_with_password(...)
    raise HTTPException(status_code=501, detail="Supabase Auth not yet configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")


@router.get("/linkedin")
async def linkedin_oauth_start() -> dict:
    # TODO (Milestone 5): redirect to Supabase LinkedIn OAuth URL
    raise HTTPException(status_code=501, detail="LinkedIn OAuth not yet configured. Set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET.")


@router.get("/linkedin/callback")
async def linkedin_oauth_callback(code: str = "", state: str = "", error: str = "") -> dict:
    # TODO (Milestone 5): exchange code via Supabase, return user + pre-fill data
    raise HTTPException(status_code=501, detail="LinkedIn OAuth callback not yet implemented.")
