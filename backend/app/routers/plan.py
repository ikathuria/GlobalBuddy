"""POST /v1/plan/generate — Judge agent + RocketRide / fallback."""

from fastapi import APIRouter, HTTPException

from app.agents.judge_agent import generate_survival_plan
from app.config import get_settings
from app.models.schemas import PlanGenerateRequest, PlanGenerateResponse
from app.utils.session_store import session_store

router = APIRouter(prefix="/v1/plan", tags=["plan"])


@router.post("/generate", response_model=PlanGenerateResponse)
async def plan_generate(payload: PlanGenerateRequest) -> PlanGenerateResponse:
    settings = get_settings()
    sid = str(payload.session_id)
    stored = session_store.get(sid)
    evidence = payload.evidence_bundle or (stored or {}).get("evidence_bundle") or {}
    profile = payload.student_profile or (stored or {}).get("student_profile") or {}
    if not evidence:
        raise HTTPException(
            status_code=400,
            detail="Missing evidence_bundle. Run POST /v1/profile/match first or pass evidence_bundle.",
        )
    return await generate_survival_plan(settings, evidence, profile)
