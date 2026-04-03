from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db.neo4j_client import Neo4jClient
from app.routers import bridge, graph, plan, profile


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    neo4j = Neo4jClient(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password,
    )
    await neo4j.connect()
    app.state.neo4j_client = neo4j
    yield
    await neo4j.close()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Globalदोस्त API", version="0.1.0", lifespan=lifespan)

    # Regex covers localhost / 127.0.0.1 / [::1] with any port (browser Origin must match for CORS).
    _local_origin_regex = r"https?://(localhost|127\.0\.0\.1|\[::1\])(:\d+)?"
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_origin_regex=_local_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(profile.router)
    app.include_router(plan.router)
    app.include_router(bridge.router)
    app.include_router(graph.router)

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/neo4j", tags=["system"])
    async def health_neo4j(request: Request) -> dict[str, str | int | None]:
        """Quick DB probe: graph data only exists after you run the seed script (API does not auto-seed)."""
        neo4j = request.app.state.neo4j_client
        rows = await neo4j.query("MATCH (n) RETURN count(n) AS c", {})
        count = int(rows[0]["c"]) if rows else 0
        return {
            "status": "ok",
            "node_count": count,
            "seed_command": (
                "cd backend && source .venv/bin/activate && python -m app.db.seed_data"
                if count == 0
                else None
            ),
        }

    return app


app = create_app()
