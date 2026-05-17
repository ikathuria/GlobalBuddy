"""Chat Agent — multi-turn AI assistant for international students."""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from collections import defaultdict

from app.config import Settings
from app.services.ai.factory import get_ai_provider

logger = logging.getLogger(__name__)

_MAX_HISTORY = 10

# In-memory store: session_id -> list of {role, content}
_sessions: dict[str, list[dict]] = defaultdict(list)

_FALLBACK_REPLY = (
    "I'm having trouble connecting to the AI service right now. "
    "For urgent questions, check your university's International Student Services (ISS) office, "
    "ssa.gov for SSN information, or studentaid.gov for financial aid guidance."
)


async def send_message(
    settings: Settings,
    *,
    session_id: str | None,
    message: str,
) -> tuple[str, str, bool]:
    """Process a chat message and return (reply, session_id, fallback_used)."""
    sid = session_id or str(uuid.uuid4())
    history = list(_sessions[sid][-_MAX_HISTORY:])

    try:
        provider = get_ai_provider(settings)
    except ValueError as exc:
        logger.warning("ai_event=chat_no_provider session=%s error=%s", sid, exc)
        _append(sid, message, _FALLBACK_REPLY)
        return _FALLBACK_REPLY, sid, True

    if not hasattr(provider, "chat_reply"):
        logger.warning("ai_event=chat_no_method provider=%s session=%s", provider.name, sid)
        _append(sid, message, _FALLBACK_REPLY)
        return _FALLBACK_REPLY, sid, True

    timeout = settings.ai_timeout_seconds
    logger.info("ai_event=chat_start provider=%s session=%s timeout_s=%d", provider.name, sid, timeout)
    t0 = time.perf_counter()

    try:
        reply = await asyncio.wait_for(
            provider.chat_reply(history, message),
            timeout=timeout,
        )
        latency_ms = int((time.perf_counter() - t0) * 1000)
        logger.info("ai_event=chat_ok provider=%s latency_ms=%d session=%s", provider.name, latency_ms, sid)
    except asyncio.TimeoutError:
        latency_ms = int((time.perf_counter() - t0) * 1000)
        logger.warning("ai_event=chat_timeout provider=%s latency_ms=%d session=%s", provider.name, latency_ms, sid)
        _append(sid, message, _FALLBACK_REPLY)
        return _FALLBACK_REPLY, sid, True
    except Exception as exc:
        latency_ms = int((time.perf_counter() - t0) * 1000)
        logger.warning("ai_event=chat_fail provider=%s latency_ms=%d session=%s error=%s", provider.name, latency_ms, sid, exc, exc_info=True)
        _append(sid, message, _FALLBACK_REPLY)
        return _FALLBACK_REPLY, sid, True

    _append(sid, message, reply)
    return reply, sid, False


def get_history(session_id: str) -> list[dict]:
    return list(_sessions.get(session_id, []))


def _append(sid: str, user_msg: str, assistant_msg: str) -> None:
    _sessions[sid].append({"role": "user", "content": user_msg})
    _sessions[sid].append({"role": "assistant", "content": assistant_msg})
