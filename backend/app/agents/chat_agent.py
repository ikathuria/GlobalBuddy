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


async def stream_message(
    settings: Settings,
    *,
    session_id: str | None,
    message: str,
):
    """Process a chat message, yielding event dicts for SSE streaming.

    Event sequence: {"type": "session", ...} once, {"type": "delta", ...} per
    text chunk, then {"type": "done", ...} exactly once (even on fallback).
    """
    sid = session_id or str(uuid.uuid4())
    history = list(_sessions[sid][-_MAX_HISTORY:])
    yield {"type": "session", "session_id": sid}

    try:
        provider = get_ai_provider(settings)
    except ValueError as exc:
        logger.warning("ai_event=chat_no_provider session=%s error=%s", sid, exc)
        _append(sid, message, _FALLBACK_REPLY)
        yield {"type": "delta", "text": _FALLBACK_REPLY}
        yield {"type": "done", "reply": _FALLBACK_REPLY, "session_id": sid, "fallback_used": True}
        return

    timeout = settings.ai_timeout_seconds
    t0 = time.perf_counter()

    if hasattr(provider, "chat_reply_stream"):
        logger.info("ai_event=chat_stream_start provider=%s session=%s timeout_s=%d", provider.name, sid, timeout)
        parts: list[str] = []
        try:
            deadline = asyncio.get_running_loop().time() + timeout
            iterator = provider.chat_reply_stream(history, message).__aiter__()
            while True:
                remaining = deadline - asyncio.get_running_loop().time()
                if remaining <= 0:
                    raise asyncio.TimeoutError
                try:
                    chunk = await asyncio.wait_for(iterator.__anext__(), timeout=remaining)
                except StopAsyncIteration:
                    break
                if chunk:
                    parts.append(chunk)
                    yield {"type": "delta", "text": chunk}
        except (asyncio.TimeoutError, Exception) as exc:  # noqa: BLE001 - any provider failure falls back
            latency_ms = int((time.perf_counter() - t0) * 1000)
            event = "chat_stream_timeout" if isinstance(exc, asyncio.TimeoutError) else "chat_stream_fail"
            logger.warning("ai_event=%s provider=%s latency_ms=%d session=%s error=%s", event, provider.name, latency_ms, sid, exc)
            if not parts:
                yield {"type": "delta", "text": _FALLBACK_REPLY}
            reply = "".join(parts) or _FALLBACK_REPLY
            _append(sid, message, reply)
            yield {"type": "done", "reply": reply, "session_id": sid, "fallback_used": True}
            return

        reply = "".join(parts)
        if not reply:
            reply = _FALLBACK_REPLY
            yield {"type": "delta", "text": reply}
            _append(sid, message, reply)
            yield {"type": "done", "reply": reply, "session_id": sid, "fallback_used": True}
            return

        latency_ms = int((time.perf_counter() - t0) * 1000)
        logger.info("ai_event=chat_stream_ok provider=%s latency_ms=%d session=%s", provider.name, latency_ms, sid)
        _append(sid, message, reply)
        yield {"type": "done", "reply": reply, "session_id": sid, "fallback_used": False}
        return

    # Provider cannot stream — send the full reply as a single delta.
    reply, sid, fallback = await send_message(settings, session_id=sid, message=message)
    yield {"type": "delta", "text": reply}
    yield {"type": "done", "reply": reply, "session_id": sid, "fallback_used": fallback}


def get_history(session_id: str) -> list[dict]:
    return list(_sessions.get(session_id, []))


def _append(sid: str, user_msg: str, assistant_msg: str) -> None:
    _sessions[sid].append({"role": "user", "content": user_msg})
    _sessions[sid].append({"role": "assistant", "content": assistant_msg})
