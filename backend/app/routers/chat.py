"""POST /v1/chat/message - AI chat assistant with optional Neon persistence."""

from __future__ import annotations

from fastapi import APIRouter, Request

from app.agents import chat_agent
from app.auth import get_optional_principal
from app.config import get_settings
from app.db import repositories
from app.models.schemas import (
    ChatHistoryResponse,
    ChatMessageRequest,
    ChatMessageResponse,
)

router = APIRouter(prefix="/v1/chat", tags=["chat"])


@router.post("/message", response_model=ChatMessageResponse)
async def chat_message(payload: ChatMessageRequest, request: Request) -> ChatMessageResponse:
    settings = get_settings()
    message = payload.message.strip()
    reply, sid, fallback = await chat_agent.send_message(
        settings,
        session_id=payload.session_id,
        message=message,
    )

    profile = await _current_profile(request)
    if profile is not None:
        db = request.app.state.db
        user_id = str(profile["id"])
        await repositories.add_chat_message(db, user_id=user_id, session_id=sid, role="user", content=message)
        await repositories.add_chat_message(db, user_id=user_id, session_id=sid, role="assistant", content=reply)

    return ChatMessageResponse(reply=reply, session_id=sid, fallback_used=fallback)


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_history(session_id: str, request: Request) -> ChatHistoryResponse:
    profile = await _current_profile(request)
    if profile is not None:
        rows = await repositories.list_chat_messages(
            request.app.state.db,
            user_id=str(profile["id"]),
            session_id=session_id,
        )
        return ChatHistoryResponse(session_id=session_id, messages=rows)

    messages = chat_agent.get_history(session_id)
    return ChatHistoryResponse(session_id=session_id, messages=messages)


async def _current_profile(request: Request) -> dict | None:
    principal = get_optional_principal(request)
    db = getattr(request.app.state, "db", None)
    if principal is None or db is None or not db.enabled:
        return None
    return await repositories.get_or_create_profile_from_claims(db, principal.claims)
