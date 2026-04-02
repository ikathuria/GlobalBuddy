"""Load curated Cypher seeds into Neo4j (MERGE-only files, fixed order)."""

import asyncio
import logging
import re
from pathlib import Path

from app.config import get_neo4j_settings
from app.db.neo4j_client import Neo4jClient

logger = logging.getLogger(__name__)

_SEED_FILES = (
    "nodes.cypher",
    "relationships.cypher",
    "demo_priya.cypher",
    "chicago_belonging.cypher",
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _strip_cypher_line_comments(raw: str) -> str:
    """Remove only full-line // comments. Do not use //.* on the whole file — that breaks https:// inside strings."""
    lines_out: list[str] = []
    for line in raw.splitlines():
        if re.match(r"^\s*//", line):
            continue
        lines_out.append(line)
    return "\n".join(lines_out)


def _split_statements(cypher: str) -> list[str]:
    """Split on semicolons outside of strings (seed files avoid embedded quotes)."""
    cleaned = _strip_cypher_line_comments(cypher)
    parts: list[str] = []
    buf: list[str] = []
    in_single = False
    in_double = False
    i = 0
    while i < len(cleaned):
        ch = cleaned[i]
        if ch == "'" and not in_double:
            in_single = not in_single
            buf.append(ch)
        elif ch == '"' and not in_single:
            in_double = not in_double
            buf.append(ch)
        elif ch == ";" and not in_single and not in_double:
            stmt = "".join(buf).strip()
            if stmt:
                parts.append(stmt)
            buf = []
        else:
            buf.append(ch)
        i += 1
    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    return parts


async def run_seed_async() -> None:
    settings = get_neo4j_settings()
    client = Neo4jClient(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password,
    )
    await client.connect()
    seed_dir = _repo_root() / "data" / "seed"
    try:
        for filename in _SEED_FILES:
            path = seed_dir / filename
            if not path.exists():
                raise FileNotFoundError(f"Missing seed file: {path}")
            text = path.read_text(encoding="utf-8")
            statements = _split_statements(text)
            logger.info("Executing %s (%d statements)", filename, len(statements))
            for stmt in statements:
                await client.query_write(stmt)
        logger.info("Seed completed successfully.")
    finally:
        await client.close()


def run_seed() -> None:
    asyncio.run(run_seed_async())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    run_seed()
