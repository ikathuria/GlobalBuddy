from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import logging
import time

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.config import get_settings
from app.db.neo4j_client import Neo4jClient
from app.routers import auth, bridge, graph, plan, pre_arrival, profile

_telemetry_logger = logging.getLogger("app.telemetry")
_TELEMETRY_ROUTES = {"/v1/plan/generate", "/v1/bridge/explain"}


class _RequestTelemetryMiddleware(BaseHTTPMiddleware):
    """Log method, path, status, and elapsed_ms for AI-heavy routes."""

    async def dispatch(self, request: Request, call_next: object) -> Response:
        if request.url.path not in _TELEMETRY_ROUTES:
            return await call_next(request)
        t0 = time.perf_counter()
        try:
            response: Response = await call_next(request)
            elapsed_ms = int((time.perf_counter() - t0) * 1000)
            _telemetry_logger.info(
                "request method=%s path=%s status=%d elapsed_ms=%d",
                request.method, request.url.path, response.status_code, elapsed_ms,
            )
            return response
        except Exception as exc:
            elapsed_ms = int((time.perf_counter() - t0) * 1000)
            _telemetry_logger.warning(
                "request method=%s path=%s error=%s elapsed_ms=%d",
                request.method, request.url.path, type(exc).__name__, elapsed_ms,
            )
            raise


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
    app.add_middleware(_RequestTelemetryMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_origin_regex=_local_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(pre_arrival.router)
    app.include_router(profile.router)
    app.include_router(plan.router)
    app.include_router(bridge.router)
    app.include_router(graph.router)

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/providers", tags=["system"])
    async def health_providers() -> dict:
        """Lightweight ping of each configured AI provider — checks reachability, not generation."""
        settings = get_settings()
        results: dict[str, dict] = {}

        async with httpx.AsyncClient(timeout=5.0) as client:
            # Gemini — list models endpoint (fast, no token consumption)
            if settings.gemini_api_key.strip():
                t0 = time.perf_counter()
                try:
                    r = await client.get(
                        "https://generativelanguage.googleapis.com/v1beta/models",
                        params={"key": settings.gemini_api_key},
                    )
                    latency_ms = int((time.perf_counter() - t0) * 1000)
                    results["gemini"] = {"status": "ok" if r.status_code == 200 else "error", "latency_ms": latency_ms, "http_status": r.status_code}
                except Exception as exc:
                    results["gemini"] = {"status": "timeout", "latency_ms": int((time.perf_counter() - t0) * 1000), "error": str(exc)}
            else:
                results["gemini"] = {"status": "not_configured"}

            # Groq — list models endpoint
            if settings.groq_api_key.strip():
                t0 = time.perf_counter()
                try:
                    r = await client.get(
                        "https://api.groq.com/openai/v1/models",
                        headers={"Authorization": f"Bearer {settings.groq_api_key}"},
                    )
                    latency_ms = int((time.perf_counter() - t0) * 1000)
                    results["groq"] = {"status": "ok" if r.status_code == 200 else "error", "latency_ms": latency_ms, "http_status": r.status_code}
                except Exception as exc:
                    results["groq"] = {"status": "timeout", "latency_ms": int((time.perf_counter() - t0) * 1000), "error": str(exc)}
            else:
                results["groq"] = {"status": "not_configured"}

            # Anthropic — simple models endpoint
            if settings.anthropic_api_key.strip():
                t0 = time.perf_counter()
                try:
                    r = await client.get(
                        "https://api.anthropic.com/v1/models",
                        headers={"x-api-key": settings.anthropic_api_key, "anthropic-version": "2023-06-01"},
                    )
                    latency_ms = int((time.perf_counter() - t0) * 1000)
                    results["anthropic"] = {"status": "ok" if r.status_code == 200 else "error", "latency_ms": latency_ms, "http_status": r.status_code}
                except Exception as exc:
                    results["anthropic"] = {"status": "timeout", "latency_ms": int((time.perf_counter() - t0) * 1000), "error": str(exc)}
            else:
                results["anthropic"] = {"status": "not_configured"}

        return {"providers": results}

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
