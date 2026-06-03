"""GET /v1/graph/subgraph - session-scoped graph for vis-network."""

from fastapi import APIRouter, HTTPException, Query, Request

from app.models.schemas import GraphEdge, GraphNode, GraphSubgraphResponse
from app.utils.session_lookup import get_session_payload

router = APIRouter(prefix="/v1/graph", tags=["graph"])


@router.get("/subgraph", response_model=GraphSubgraphResponse)
async def get_subgraph(
    request: Request,
    session_id: str = Query(..., description="Session from /v1/profile/match"),
) -> GraphSubgraphResponse:
    stored = await get_session_payload(request, session_id)
    if not stored:
        raise HTTPException(status_code=404, detail="Unknown session_id")
    sg = stored.get("subgraph") or {}
    nodes = [GraphNode(**n) for n in sg.get("nodes", [])]
    edges = [GraphEdge.model_validate(e) for e in sg.get("edges", [])]
    return GraphSubgraphResponse(nodes=nodes, edges=edges, highlights=[])
