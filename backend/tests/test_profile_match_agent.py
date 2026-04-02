"""Profile match agent returns expected top-level keys (mocked Neo4j)."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.agents.profile_match_agent import run_profile_match
from app.db.neo4j_client import Neo4jClient
from app.models.schemas import ProfileMatchRequest


def _mentor_rows() -> list[dict]:
    return [
        {
            "id": "mentor_ananya_sharma",
            "name": "Ananya Sharma",
            "trust_score": 0.92,
            "languages": ["English", "Hindi"],
            "email": "ananya@example.test",
            "linkedin_url": "",
            "connect_hint": "Say GlobalBuddy in the subject.",
            "covered": ["banking", "housing"],
        }
    ]


def _peer_rows() -> list[dict]:
    return [
        {
            "id": "peer_alex_kim",
            "name": "Alex Kim",
            "university": "Illinois Institute of Technology",
            "neighborhood": "South Loop",
            "email": "peer@example.test",
            "connect_hint": "Coffee near campus.",
        }
    ]


def _rest_rows() -> list[dict]:
    return [
        {"id": "rest_devon_kitchen", "name": "Devon Kitchen", "price_level": 2, "distance_km": 2.4}
    ]


def _event_rows() -> list[dict]:
    return [
        {
            "id": "event_hackwithchicago_3",
            "name": "HackWithChicago 3.0",
            "start_time": "2026-04-12T09:00:00Z",
            "location": "Chicago Loop",
            "category": "hackathon",
        }
    ]


def _resource_rows() -> list[dict]:
    return [
        {"id": "resource_chase_south_loop", "name": "Chase Bank - South Loop / Grant Park", "resource_type": "banking"}
    ]


def _task_rows() -> list[dict]:
    return [
        {
            "tid": "task_identity_docs",
            "name": "Identity docs",
            "priority": 1,
            "estimated_day_window": "Day 1-3",
            "next_id": "task_open_bank_account",
        },
        {
            "tid": "task_open_bank_account",
            "name": "Bank account",
            "priority": 2,
            "estimated_day_window": "Day 3-7",
            "next_id": "task_housing_commitment",
        },
        {
            "tid": "task_housing_commitment",
            "name": "Housing",
            "priority": 3,
            "estimated_day_window": "Day 7-14",
            "next_id": None,
        },
    ]


@pytest.mark.asyncio
async def test_profile_match_result_shape(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_query(self: object, cypher: str, params: object | None = None) -> list:
        if "Mentor" in cypher and "FROM_COUNTRY" in cypher:
            return _mentor_rows()
        if "Peer" in cypher:
            return _peer_rows()
        if "Restaurant" in cypher:
            return _rest_rows()
        if "Event" in cypher and "RELEVANT_TO" in cypher:
            return _event_rows()
        if "Resource" in cypher and "HELPS_WITH" in cypher:
            return _resource_rows()
        if "Task" in cypher and "PRECEDES" in cypher:
            return _task_rows()
        return []

    monkeypatch.setattr(Neo4jClient, "query", fake_query)

    neo4j = Neo4jClient(uri="bolt://x", user="u", password="p")
    profile = ProfileMatchRequest(
        country_of_origin="India",
        home_city="Bengaluru",
        target_university="Illinois Institute of Technology",
        target_city="Chicago",
        needs=["banking", "housing"],
        interests=["south indian food"],
    )
    result = await run_profile_match(neo4j, profile)
    assert result.session_id
    assert isinstance(result.mentors_top3, list)
    assert result.mentors_top3[0].email == "ananya@example.test"
    assert result.peers_nearby[0].email == "peer@example.test"
    eb = result.evidence_bundle
    assert "mentors" in eb
    assert "tasks_ordered" in eb
    assert isinstance(result.subgraph.nodes, list)
