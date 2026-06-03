"""Authenticated plan progress routes backed by Neon Postgres."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.auth import require_principal
from app.db import repositories

router = APIRouter(prefix="/v1/progress", tags=["progress"])


class PlanProgressItem(BaseModel):
    task_id: str
    completed: bool
    updated_at: str


class PlanProgressResponse(BaseModel):
    items: list[PlanProgressItem]


class PlanProgressUpdate(BaseModel):
    completed: bool


@router.get("/plan", response_model=PlanProgressResponse)
async def get_plan_progress(request: Request) -> PlanProgressResponse:
    principal = require_principal(request)
    db = request.app.state.db
    if not db.enabled:
        raise HTTPException(status_code=503, detail="Postgres persistence is not configured.")

    profile = await repositories.get_or_create_profile_from_claims(db, principal.claims)
    rows = await repositories.list_plan_progress(db, user_id=str(profile["id"]))
    return PlanProgressResponse(
        items=[
            PlanProgressItem(
                task_id=str(row["task_id"]),
                completed=bool(row["completed"]),
                updated_at=row["updated_at"].isoformat(),
            )
            for row in rows
        ]
    )


@router.put("/plan/{task_id}", response_model=PlanProgressItem)
async def update_plan_progress(
    task_id: str,
    payload: PlanProgressUpdate,
    request: Request,
) -> PlanProgressItem:
    principal = require_principal(request)
    db = request.app.state.db
    if not db.enabled:
        raise HTTPException(status_code=503, detail="Postgres persistence is not configured.")

    profile = await repositories.get_or_create_profile_from_claims(db, principal.claims)
    row = await repositories.set_plan_progress(
        db,
        user_id=str(profile["id"]),
        task_id=task_id,
        completed=payload.completed,
    )
    return PlanProgressItem(
        task_id=str(row["task_id"]),
        completed=bool(row["completed"]),
        updated_at=row["updated_at"].isoformat(),
    )
