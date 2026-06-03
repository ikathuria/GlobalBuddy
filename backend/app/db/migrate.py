"""Run SQL migrations against Neon Postgres.

Usage:
    python -m app.db.migrate
"""

from __future__ import annotations

import asyncio
from pathlib import Path
import sys

from app.config import get_settings
from app.db.postgres import migrations_dir


async def _run() -> int:
    settings = get_settings()
    database_url = settings.database_url_unpooled.strip() or settings.database_url.strip()
    if not database_url:
        print("DATABASE_URL or DATABASE_URL_UNPOOLED is not configured.")
        return 1

    import asyncpg

    conn = await asyncpg.connect(database_url)
    try:
        await conn.execute(
            """
            create table if not exists schema_migrations (
              version text primary key,
              applied_at timestamptz not null default now()
            )
            """
        )
        root = migrations_dir()
        files = sorted(Path(root).glob("*.sql"))
        if not files:
            print(f"No migrations found in {root}")
            return 0

        for file in files:
            version = file.stem
            exists = await conn.fetchval("select 1 from schema_migrations where version = $1", version)
            if exists:
                print(f"skip {version}")
                continue

            sql = file.read_text(encoding="utf-8")
            async with conn.transaction():
                await conn.execute(sql)
                await conn.execute("insert into schema_migrations (version) values ($1)", version)
            print(f"applied {version}")
    finally:
        await conn.close()

    return 0


def main() -> int:
    return asyncio.run(_run())


if __name__ == "__main__":
    sys.exit(main())
