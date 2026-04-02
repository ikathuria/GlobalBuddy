"""In-memory session store for MVP demo (replace with Redis/DB in production)."""

from __future__ import annotations

import threading
from typing import Any


class SessionStore:
    def __init__(self) -> None:
        self._data: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    def set(self, session_id: str, payload: dict[str, Any]) -> None:
        with self._lock:
            self._data[session_id] = payload

    def get(self, session_id: str) -> dict[str, Any] | None:
        with self._lock:
            return self._data.get(session_id)

    def update(self, session_id: str, **fields: Any) -> None:
        with self._lock:
            if session_id not in self._data:
                self._data[session_id] = {}
            self._data[session_id].update(fields)


session_store = SessionStore()
