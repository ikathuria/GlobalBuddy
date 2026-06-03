"""Session lookup helpers with Neon persistence and in-memory fallback."""

from __future__ import annotations

from typing import Any

from fastapi import Request

from app.db import repositories
from app.utils.session_store import session_store


async def get_session_payload(request: Request, session_id: str) -> dict[str, Any] | None:
    payload = session_store.get(session_id)
    if payload is not None:
        return payload

    db = getattr(request.app.state, "db", None)
    if db is None or not db.enabled:
        return None

    payload = await repositories.get_app_session(db, session_id=session_id)
    if payload is not None:
        session_store.set(session_id, payload)
    return payload
