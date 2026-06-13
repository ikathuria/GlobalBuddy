"""Social layer (M11): connection and mentor-intro requests backed by Neon.

Requests target Markdown graph entities (seed mentors/peers) and are recorded
against the authenticated requester. Mentor intro emails are sent server-side
via Resend so the mentor's address is never exposed to the client.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.auth import require_principal
from app.config import get_settings
from app.db import repositories
from app.services import email_service

router = APIRouter(prefix="/v1/social", tags=["social"])


class ConnectRequest(BaseModel):
    target_node_id: str = Field(min_length=1)
    target_name: str = ""
    target_role: str = ""
    message: str = ""


class IntroRequest(BaseModel):
    mentor_node_id: str = Field(min_length=1)
    message: str = ""


class SocialRequestItem(BaseModel):
    id: str
    kind: str
    target_node_id: str
    target_name: str
    target_role: str
    status: str
    email_sent: bool
    created_at: str


class SocialRequestList(BaseModel):
    items: list[SocialRequestItem]


class IntroResult(BaseModel):
    id: str
    kind: str
    target_name: str
    status: str
    email_sent: bool
    created_at: str


def _require_db(request: Request):
    db = getattr(request.app.state, "db", None)
    if db is None or not db.enabled:
        raise HTTPException(status_code=503, detail="Postgres persistence is not configured.")
    return db


def _graph_node(request: Request, node_id: str):
    graph_service = getattr(request.app.state, "graph_service", None)
    nodes = getattr(graph_service, "nodes", None)
    if not isinstance(nodes, dict):
        return None
    return nodes.get(node_id)


def _item(row: dict) -> SocialRequestItem:
    return SocialRequestItem(
        id=str(row["id"]),
        kind=str(row["kind"]),
        target_node_id=str(row["target_node_id"]),
        target_name=str(row.get("target_name") or ""),
        target_role=str(row.get("target_role") or ""),
        status=str(row["status"]),
        email_sent=bool(row.get("email_sent")),
        created_at=row["created_at"].isoformat(),
    )


@router.post("/connect", response_model=SocialRequestItem)
async def connect(payload: ConnectRequest, request: Request) -> SocialRequestItem:
    principal = require_principal(request)
    db = _require_db(request)

    profile = await repositories.get_or_create_profile_from_claims(db, principal.claims)
    node = _graph_node(request, payload.target_node_id)
    target_name = payload.target_name or (node.title if node else "")
    target_role = payload.target_role or (node.type if node else "")

    row, _created = await repositories.create_social_request(
        db,
        requester_id=str(profile["id"]),
        kind="connection",
        target_node_id=payload.target_node_id,
        target_name=target_name,
        target_role=target_role,
        message=payload.message,
    )
    return _item(row)


@router.post("/intro-request", response_model=IntroResult)
async def intro_request(payload: IntroRequest, request: Request) -> IntroResult:
    principal = require_principal(request)
    db = _require_db(request)
    settings = get_settings()

    profile = await repositories.get_or_create_profile_from_claims(db, principal.claims)
    node = _graph_node(request, payload.mentor_node_id)
    if node is None:
        raise HTTPException(status_code=404, detail="Mentor not found in graph.")

    mentor_name = node.title or "your mentor"
    row, created = await repositories.create_social_request(
        db,
        requester_id=str(profile["id"]),
        kind="intro",
        target_node_id=payload.mentor_node_id,
        target_name=mentor_name,
        target_role=node.type or "Mentor",
        message=payload.message,
    )

    # Send the templated email at most once per request.
    email_sent = bool(row.get("email_sent"))
    mentor_email = str(node.data.get("email") or "").strip()
    if created and not email_sent and mentor_email:
        requester_name = str(profile.get("full_name") or "").strip() or "A Globalदोस्त student"
        requester_email = str(profile.get("email") or "").strip()
        note = payload.message.strip() or "They'd love a few minutes of your time as they settle in."
        html = (
            f"<p>Hi {mentor_name},</p>"
            f"<p><strong>{requester_name}</strong> asked for an introduction through Globalदोस्त.</p>"
            f"<blockquote>{note}</blockquote>"
            "<p>If you're open to it, just reply to this email to connect directly.</p>"
            "<p>— The Globalदोस्त team</p>"
        )
        email_sent = await email_service.send_email(
            settings,
            to=mentor_email,
            subject=f"{requester_name} would like an introduction",
            html=html,
            reply_to=requester_email or None,
        )
        if email_sent:
            await repositories.mark_social_request_email_sent(db, request_id=str(row["id"]))

    return IntroResult(
        id=str(row["id"]),
        kind="intro",
        target_name=mentor_name,
        status=str(row["status"]),
        email_sent=email_sent,
        created_at=row["created_at"].isoformat(),
    )


@router.get("/requests", response_model=SocialRequestList)
async def list_requests(request: Request) -> SocialRequestList:
    principal = require_principal(request)
    db = _require_db(request)
    profile = await repositories.get_or_create_profile_from_claims(db, principal.claims)
    rows = await repositories.list_social_requests(db, requester_id=str(profile["id"]))
    return SocialRequestList(items=[_item(row) for row in rows])
