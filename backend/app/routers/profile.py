"""POST /v1/profile/match - graph evidence + session storage."""

from fastapi import APIRouter, Request

from app.auth import get_optional_principal
from app.agents.profile_match_agent import run_profile_match
from app.db import repositories
from app.config import get_settings
from app.models.schemas import ProfileMatchRequest, ProfileMatchResponse
from app.utils.session_store import session_store

router = APIRouter(prefix="/v1/profile", tags=["profile"])


@router.post("/match", response_model=ProfileMatchResponse)
async def profile_match(payload: ProfileMatchRequest, request: Request) -> ProfileMatchResponse:
    graph_source = getattr(request.app.state, "graph_service", None) or request.app.state.neo4j_client
    result = await run_profile_match(graph_source, payload)
    session_payload = {
        "evidence_bundle": result.evidence_bundle,
        "student_profile": result.evidence_bundle.get("student_profile", {}),
        "subgraph": result.subgraph.model_dump(mode="json", by_alias=True),
    }
    session_store.set(result.session_id, session_payload)
    db = getattr(request.app.state, "db", None)
    if db is not None and db.enabled:
        await repositories.set_app_session(
            db,
            session_id=result.session_id,
            payload=session_payload,
            ttl_hours=get_settings().session_ttl_hours,
        )
    principal = get_optional_principal(request)
    if principal is not None and db is not None and db.enabled:
        await repositories.update_profile_from_match(db, auth_user_id=principal.auth_user_id, payload=payload)
    return result
