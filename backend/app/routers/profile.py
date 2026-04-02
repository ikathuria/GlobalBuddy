"""POST /v1/profile/match — Neo4j evidence + session storage."""

from fastapi import APIRouter, Request

from app.agents.profile_match_agent import run_profile_match
from app.models.schemas import ProfileMatchRequest, ProfileMatchResponse
from app.utils.session_store import session_store

router = APIRouter(prefix="/v1/profile", tags=["profile"])


@router.post("/match", response_model=ProfileMatchResponse)
async def profile_match(payload: ProfileMatchRequest, request: Request) -> ProfileMatchResponse:
    neo4j = request.app.state.neo4j_client
    result = await run_profile_match(neo4j, payload)
    session_store.set(
        result.session_id,
        {
            "evidence_bundle": result.evidence_bundle,
            "student_profile": result.evidence_bundle.get("student_profile", {}),
            "subgraph": result.subgraph.model_dump(mode="json", by_alias=True),
        },
    )
    return result
