"""GET /v1/pre-arrival/checklist — returns PreArrivalChecklist nodes from Neo4j."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/v1/pre-arrival", tags=["pre-arrival"])


class PreArrivalItem(BaseModel):
    id: str
    name: str
    description: str
    when: str           # before_landing | arrival_day | first_week
    priority: str       # critical | high | medium | low
    category: str


_PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
_WHEN_ORDER = {"before_landing": 0, "arrival_day": 1, "first_week": 2}


@router.get("/checklist", response_model=list[PreArrivalItem])
async def get_checklist(request: Request) -> list[PreArrivalItem]:
    neo4j = request.app.state.neo4j_client
    rows = await neo4j.query(
        """
        MATCH (p:PreArrivalChecklist)
        RETURN p.id AS id, p.name AS name, p.description AS description,
               p.when AS when, p.priority AS priority, p.category AS category
        """,
        {},
    )
    items = [
        PreArrivalItem(
            id=row["id"] or "",
            name=row["name"] or "",
            description=row["description"] or "",
            when=row["when"] or "first_week",
            priority=row["priority"] or "medium",
            category=row["category"] or "",
        )
        for row in rows
        if row.get("id")
    ]
    return sorted(
        items,
        key=lambda i: (_WHEN_ORDER.get(i.when, 9), _PRIORITY_ORDER.get(i.priority, 9)),
    )
