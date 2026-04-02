"""POST /v1/bridge/explain — Cultural Bridge agent."""

from fastapi import APIRouter

from app.agents.cultural_bridge_agent import explain_term
from app.config import get_settings
from app.models.schemas import BridgeExplainRequest, BridgeExplainResponse

router = APIRouter(prefix="/v1/bridge", tags=["bridge"])


@router.post("/explain", response_model=BridgeExplainResponse)
async def bridge_explain(payload: BridgeExplainRequest) -> BridgeExplainResponse:
    settings = get_settings()
    return await explain_term(
        settings,
        term=payload.term.strip(),
        home_country=payload.home_country.strip(),
        context=payload.context.strip(),
    )
