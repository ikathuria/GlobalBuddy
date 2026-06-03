"""Authenticated document status routes backed by Neon Postgres."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.auth import require_principal
from app.db import repositories

router = APIRouter(prefix="/v1/documents", tags=["documents"])

VALID_STATUSES = {"pending", "in_progress", "done"}


class DocumentStatusItem(BaseModel):
    doc_type: str
    status: str
    updated_at: str


class DocumentStatusResponse(BaseModel):
    items: list[DocumentStatusItem]


class DocumentStatusUpdate(BaseModel):
    status: str


@router.get("", response_model=DocumentStatusResponse)
async def get_documents(request: Request) -> DocumentStatusResponse:
    principal = require_principal(request)
    db = request.app.state.db
    if not db.enabled:
        raise HTTPException(status_code=503, detail="Postgres persistence is not configured.")

    profile = await repositories.get_or_create_profile_from_claims(db, principal.claims)
    rows = await repositories.list_user_documents(db, user_id=str(profile["id"]))
    return DocumentStatusResponse(items=[_document_item(row) for row in rows])


@router.put("/{doc_type}", response_model=DocumentStatusItem)
async def update_document(doc_type: str, payload: DocumentStatusUpdate, request: Request) -> DocumentStatusItem:
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid document status.")

    principal = require_principal(request)
    db = request.app.state.db
    if not db.enabled:
        raise HTTPException(status_code=503, detail="Postgres persistence is not configured.")

    profile = await repositories.get_or_create_profile_from_claims(db, principal.claims)
    row = await repositories.set_user_document_status(
        db,
        user_id=str(profile["id"]),
        doc_type=doc_type,
        status=payload.status,
    )
    return _document_item(row)


def _document_item(row: dict) -> DocumentStatusItem:
    return DocumentStatusItem(
        doc_type=str(row["doc_type"]),
        status=str(row["status"]),
        updated_at=row["updated_at"].isoformat(),
    )
