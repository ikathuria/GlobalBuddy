"""Smoke tests: full 3-step API flow with mocked Neo4j and mocked AI.

These run without any live services — Neo4j is mocked via conftest.py and the
AI provider is monkeypatched. Goal: confirm every endpoint in the critical path
returns the correct shape and status code end-to-end.
"""

from __future__ import annotations

import uuid
from typing import Any

import pytest


# ── Shared fake AI provider ───────────────────────────────────────────────────

class _MockProvider:
    name = "smoke-mock"

    async def generate_plan(
        self, evidence_bundle: dict, student_profile: dict
    ) -> tuple[dict, dict]:
        return {
            "plan_title": "Smoke Test Plan",
            "best_next_action": "Register with ISS office.",
            "steps": [
                {
                    "day_range": "Day 1-3",
                    "action": "Confirm identity documents and visit ISS.",
                    "entities": ["ISS Office"],
                    "dependency_reason": "Required before all other tasks.",
                    "source_node_ids": ["task_identity_docs"],
                }
            ],
            "priority_contacts": ["ISS Office"],
            "warnings": [],
            "confidence": 0.9,
        }, {"provider": "smoke-mock"}

    async def explain_term(
        self, term: str, home_country: str, context: str
    ) -> tuple[dict, dict]:
        return {
            "plain_explanation": f"US meaning of {term}.",
            "home_context_analogy": f"Similar to {home_country} equivalent.",
            "common_mistakes": ["Assuming it works like back home."],
            "what_to_do_next": ["Verify with your university's ISS office."],
        }, {"provider": "smoke-mock"}


_PROFILE_PAYLOAD = {
    "full_name": "Arjun Mehta",
    "email": "arjun@example.com",
    "country_of_origin": "India",
    "home_city": "Mumbai",
    "target_university": "Illinois Institute of Technology",
    "target_city": "Chicago",
    "needs": ["housing", "banking", "social"],
    "new_to_us": True,
}


# ── Step 1: Profile match ─────────────────────────────────────────────────────

def test_step1_profile_match_returns_200(api_client: object) -> None:
    r = api_client.post("/v1/profile/match", json=_PROFILE_PAYLOAD)
    assert r.status_code == 200


def test_step1_profile_match_response_shape(api_client: object) -> None:
    r = api_client.post("/v1/profile/match", json=_PROFILE_PAYLOAD)
    data = r.json()
    required = [
        "session_id", "mentors_top3", "peers_nearby", "evidence_bundle",
        "subgraph", "support_coverage_score", "belonging_score", "cultural_fit_score",
    ]
    for field in required:
        assert field in data, f"Missing field: {field!r}"


def test_step1_session_id_is_valid_uuid(api_client: object) -> None:
    r = api_client.post("/v1/profile/match", json=_PROFILE_PAYLOAD)
    sid = r.json()["session_id"]
    uuid.UUID(sid)  # raises if invalid


# ── Step 2: Plan generate ─────────────────────────────────────────────────────

def test_step2_plan_generate_with_session(
    api_client: object, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("app.agents.judge_agent.get_ai_provider", lambda _: _MockProvider())
    match_r = api_client.post("/v1/profile/match", json=_PROFILE_PAYLOAD)
    session_id = match_r.json()["session_id"]

    plan_r = api_client.post("/v1/plan/generate", json={"session_id": session_id})
    assert plan_r.status_code == 200
    plan = plan_r.json()
    assert plan["plan_title"]
    assert isinstance(plan["steps"], list)
    assert len(plan["steps"]) > 0
    assert "best_next_action" in plan
    assert "fallback_used" in plan


def test_step2_plan_missing_session_returns_400(api_client: object) -> None:
    r = api_client.post("/v1/plan/generate", json={"session_id": str(uuid.uuid4())})
    assert r.status_code == 400


def test_step2_plan_ai_timeout_returns_fallback(
    api_client: object, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When the AI call times out the endpoint must return a deterministic fallback, not 500."""
    import asyncio

    async def _slow_plan(*_a: Any, **_kw: Any) -> None:
        await asyncio.sleep(999)

    class _SlowProvider:
        name = "slow"
        generate_plan = _slow_plan

    monkeypatch.setattr("app.agents.judge_agent.get_ai_provider", lambda _: _SlowProvider())
    # Override timeout to 0.05 s so the test stays fast
    monkeypatch.setenv("AI_TIMEOUT_SECONDS", "0")
    from app.config import get_settings
    get_settings.cache_clear()

    match_r = api_client.post("/v1/profile/match", json=_PROFILE_PAYLOAD)
    session_id = match_r.json()["session_id"]

    plan_r = api_client.post("/v1/plan/generate", json={"session_id": session_id})
    assert plan_r.status_code == 200
    assert plan_r.json()["fallback_used"] is True


# ── Step 3: Bridge explain ────────────────────────────────────────────────────

def test_step3_bridge_explain_returns_200(
    api_client: object, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("app.agents.cultural_bridge_agent.get_ai_provider", lambda _: _MockProvider())
    r = api_client.post(
        "/v1/bridge/explain",
        json={"term": "credit score", "home_country": "India", "context": "opening a bank account"},
    )
    assert r.status_code == 200


def test_step3_bridge_response_shape(
    api_client: object, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("app.agents.cultural_bridge_agent.get_ai_provider", lambda _: _MockProvider())
    r = api_client.post(
        "/v1/bridge/explain",
        json={"term": "security deposit", "home_country": "India", "context": "renting an apartment"},
    )
    data = r.json()
    for field in ("term", "plain_explanation", "home_context_analogy", "common_mistakes", "what_to_do_next"):
        assert field in data, f"Missing field: {field!r}"
    assert data["term"] == "security deposit"


def test_step3_bridge_ai_timeout_returns_fallback(
    api_client: object, monkeypatch: pytest.MonkeyPatch
) -> None:
    import asyncio

    async def _slow_explain(*_a: Any, **_kw: Any) -> None:
        await asyncio.sleep(999)

    class _SlowProvider:
        name = "slow"
        explain_term = _slow_explain

    monkeypatch.setattr("app.agents.cultural_bridge_agent.get_ai_provider", lambda _: _SlowProvider())
    monkeypatch.setenv("AI_TIMEOUT_SECONDS", "0")
    from app.config import get_settings
    get_settings.cache_clear()

    r = api_client.post(
        "/v1/bridge/explain",
        json={"term": "W-2", "home_country": "India", "context": "tax filing"},
    )
    assert r.status_code == 200
    assert r.json()["fallback_used"] is True


# ── Graph subgraph ────────────────────────────────────────────────────────────

def test_graph_subgraph_with_session(api_client: object) -> None:
    match_r = api_client.post("/v1/profile/match", json=_PROFILE_PAYLOAD)
    session_id = match_r.json()["session_id"]

    r = api_client.get(f"/v1/graph/subgraph?session_id={session_id}")
    assert r.status_code == 200
    data = r.json()
    assert "nodes" in data
    assert "edges" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["edges"], list)


# ── Health endpoints ──────────────────────────────────────────────────────────

def test_health_ok(api_client: object) -> None:
    r = api_client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_health_neo4j_returns_node_count(api_client: object) -> None:
    r = api_client.get("/health/neo4j")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "node_count" in data


def test_health_providers_returns_all_keys(api_client: object) -> None:
    r = api_client.get("/health/providers")
    assert r.status_code == 200
    providers = r.json()["providers"]
    for key in ("gemini", "groq", "anthropic"):
        assert key in providers
        assert "status" in providers[key]
