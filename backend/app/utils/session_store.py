"""Local fallback session cache.

Production persistence is handled by Neon Postgres via app_sessions; this cache
keeps local/no-DB demos fast and rehydrates from Neon after process restarts.
"""

from __future__ import annotations

import threading
import time
from typing import Any


class SessionStore:
    def __init__(self, ttl_seconds: int = 24 * 60 * 60) -> None:
        self._data: dict[str, tuple[float, dict[str, Any]]] = {}
        self._lock = threading.RLock()
        self._ttl_seconds = ttl_seconds

    def set(self, session_id: str, payload: dict[str, Any]) -> None:
        expires_at = time.time() + self._ttl_seconds
        with self._lock:
            self._data[session_id] = (expires_at, payload)

    def get(self, session_id: str) -> dict[str, Any] | None:
        with self._lock:
            entry = self._data.get(session_id)
            if entry is None:
                return None
            expires_at, payload = entry
            if expires_at <= time.time():
                self._data.pop(session_id, None)
                return None
            return payload

    def update(self, session_id: str, **fields: Any) -> None:
        with self._lock:
            current = self.get(session_id) or {}
            current.update(fields)
            self._data[session_id] = (time.time() + self._ttl_seconds, current)


session_store = SessionStore()
