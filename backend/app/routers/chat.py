"""POST /v1/chat/message — Persistent AI chat assistant."""

from fastapi import APIRouter

from app.agents import chat_agent
from app.config import get_settings
from app.models.schemas import (
    ChatHistoryResponse,
    ChatMessageRequest,
    ChatMessageResponse,
)

router = APIRouter(prefix="/v1/chat", tags=["chat"])


@router.post("/message", response_model=ChatMessageResponse)
async def chat_message(payload: ChatMessageRequest) -> ChatMessageResponse:
    settings = get_settings()
    reply, sid, fallback = await chat_agent.send_message(
        settings,
        session_id=payload.session_id,
        message=payload.message.strip(),
    )
    return ChatMessageResponse(reply=reply, session_id=sid, fallback_used=fallback)


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_history(session_id: str) -> ChatHistoryResponse:
    messages = chat_agent.get_history(session_id)
    return ChatHistoryResponse(session_id=session_id, messages=messages)
