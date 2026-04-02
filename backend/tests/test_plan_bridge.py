"""Plan + bridge response shapes with mocked AI provider."""

from __future__ import annotations

from typing import Any

import pytest

from app.agents.cultural_bridge_agent import explain_term
from app.agents.judge_agent import generate_survival_plan
from app.config import Settings


class _FakeProvider:
    name = "mock"

    async def generate_plan(
        self,
        evidence_bundle: dict[str, Any],
        student_profile: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return {
            "plan_title": "First 30 Days",
            "best_next_action": "Confirm documents and book ISS advising.",
            "steps": [
                {
                    "day_range": "Day 1-3",
                    "action": "Meet mentor and open bank account.",
                    "entities": ["Ananya Sharma", "Chase Bank - South Loop / Grant Park"],
                    "dependency_reason": "Documentation before banking.",
                    "source_node_ids": ["task_identity_docs"],
                }
            ],
            "priority_contacts": ["Ananya Sharma"],
            "warnings": [],
            "confidence": 0.88,
        }, {"provider": "mock"}

    async def explain_term(
        self,
        term: str,
        home_country: str,
        context: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return {
            "plain_explanation": f"Explanation of {term}",
            "home_context_analogy": f"Compared to {home_country}",
            "common_mistakes": ["m1"],
            "what_to_do_next": ["n1"],
        }, {"provider": "mock"}


@pytest.mark.asyncio
async def test_plan_generate_response_shape(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.agents.judge_agent.get_ai_provider",
        lambda _s: _FakeProvider(),
    )
    settings = Settings(
        neo4j_uri="bolt://x",
        neo4j_user="u",
        neo4j_password="p",
        gemini_api_key="k",
    )
    ev = {
        "mentors": [{"name": "Ananya Sharma"}],
        "tasks_ordered": [],
        "resources": [],
    }
    out = await generate_survival_plan(settings, ev, {"country_of_origin": "India"})
    assert out.plan_title
    assert out.best_next_action
    assert out.steps
    assert out.confidence > 0
    assert out.llm_provider == "mock"


@pytest.mark.asyncio
async def test_bridge_response_shape(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.agents.cultural_bridge_agent.get_ai_provider",
        lambda _s: _FakeProvider(),
    )
    settings = Settings(
        neo4j_uri="bolt://x",
        neo4j_user="u",
        neo4j_password="p",
        gemini_api_key="k",
    )
    out = await explain_term(settings, term="credit score", home_country="India", context="banking")
    assert out.term == "credit score"
    assert out.plain_explanation
    assert out.home_context_analogy
    assert out.common_mistakes
    assert out.what_to_do_next
