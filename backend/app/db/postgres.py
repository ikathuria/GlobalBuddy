"""Async Postgres helper for Neon-backed persistence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.config import Settings


class PostgresDatabase:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._pool: Any | None = None

    @property
    def enabled(self) -> bool:
        return bool(self._settings.database_url.strip())

    @property
    def is_connected(self) -> bool:
        return self._pool is not None

    async def connect(self) -> None:
        if not self.enabled or self._pool is not None:
            return
        import asyncpg

        self._pool = await asyncpg.create_pool(
            self._settings.database_url,
            min_size=1,
            max_size=5,
            command_timeout=20,
        )

    async def close(self) -> None:
        if self._pool is None:
            return
        await self._pool.close()
        self._pool = None

    async def execute(self, sql: str, *args: Any) -> str:
        pool = self._require_pool()
        async with pool.acquire() as conn:
            return await conn.execute(sql, *args)

    async def fetch(self, sql: str, *args: Any) -> list[dict[str, Any]]:
        pool = self._require_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, *args)
        return [dict(row) for row in rows]

    async def fetchrow(self, sql: str, *args: Any) -> dict[str, Any] | None:
        pool = self._require_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(sql, *args)
        return dict(row) if row else None

    async def ping(self) -> bool:
        if not self.enabled:
            return False
        row = await self.fetchrow("select 1 as ok")
        return row == {"ok": 1}

    def _require_pool(self) -> Any:
        if self._pool is None:
            raise RuntimeError("Postgres is not connected. Set DATABASE_URL and start the app.")
        return self._pool


def migrations_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "migrations"
