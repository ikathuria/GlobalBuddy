"""Pytest fixtures: env + Neo4j mocks so tests run without Aura."""

from __future__ import annotations

import os
from unittest.mock import MagicMock

import pytest

# Required before Settings / app import
os.environ.setdefault("NEO4J_URI", "bolt://localhost:7687")
os.environ.setdefault("NEO4J_USER", "neo4j")
os.environ.setdefault("NEO4J_PASSWORD", "test-password")
os.environ.setdefault("GEMINI_API_KEY", "test-gemini-key")
os.environ.setdefault("GEMINI_MODEL", "gemini-2.0-flash")
os.environ.setdefault("AI_PROVIDER", "gemini")
os.environ.setdefault("ROCKETRIDE_URI", "")
os.environ.setdefault("ROCKETRIDE_APIKEY", "")
os.environ.setdefault("ANTHROPIC_API_KEY", "")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    from app.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def patch_neo4j_lifecycle(monkeypatch: pytest.MonkeyPatch) -> None:
    """Avoid real Neo4j during FastAPI TestClient runs."""

    async def connect(self: object) -> None:
        setattr(self, "_driver", MagicMock())

    async def query(self: object, cypher: str, params: object | None = None) -> list:
        if "count(n)" in cypher:
            return [{"c": 0}]
        return []

    async def query_write(self: object, cypher: str, params: object | None = None) -> list:
        return []

    async def close(self: object) -> None:
        setattr(self, "_driver", None)

    monkeypatch.setattr("app.db.neo4j_client.Neo4jClient.connect", connect)
    monkeypatch.setattr("app.db.neo4j_client.Neo4jClient.query", query)
    monkeypatch.setattr("app.db.neo4j_client.Neo4jClient.query_write", query_write)
    monkeypatch.setattr("app.db.neo4j_client.Neo4jClient.close", close)


@pytest.fixture
def api_client() -> object:
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as client:
        yield client
