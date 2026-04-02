"""Judge Agent: ordered survival plan via provider abstraction (Gemini / RocketRide HTTP / Anthropic)."""

from __future__ import annotations

import logging
from typing import Any

from app.config import Settings
from app.models.schemas import PlanGenerateResponse, PlanStep
from app.services.ai.factory import get_ai_provider
from app.utils.citations import validate_entity_citations

logger = logging.getLogger(__name__)


def _fallback_plan(evidence_bundle: dict[str, Any]) -> PlanGenerateResponse:
    """Deterministic checklist from tasks + resources when AI is unavailable."""
    tasks = evidence_bundle.get("tasks_ordered") or []
    resources = evidence_bundle.get("resources") or []
    mentors = evidence_bundle.get("mentors") or []
    res_names = [r.get("name", "") for r in resources if isinstance(r, dict)]
    mentor_name = mentors[0].get("name", "a matched mentor") if mentors else "International Student Services"
    steps: list[PlanStep] = []
    for i, t in enumerate(tasks):
        if not isinstance(t, dict):
            continue
        tid = str(t.get("id", f"task_{i}"))
        tname = str(t.get("name", "Task"))
        window = str(t.get("estimated_day_window", f"Day {i * 2 + 1}-{i * 2 + 3}"))
        primary_res = res_names[0] if res_names else "listed campus resources"
        steps.append(
            PlanStep(
                day_range=window,
                action=(
                    f"Progress on '{tname}'. Confirm prerequisites are met, then use '{primary_res}' "
                    f"and coordinate with {mentor_name} if you are blocked."
                ),
                entities=[tname, primary_res, mentor_name],
                dependency_reason="Follows Neo4j Task-[:PRECEDES]->Task ordering from the graph.",
                source_node_ids=[tid],
            )
        )
    best = ""
    if steps:
        best = steps[0].action
    return PlanGenerateResponse(
        plan_title="Deterministic checklist from Neo4j task graph (AI unavailable)",
        best_next_action=best,
        steps=steps,
        priority_contacts=[mentor_name] if mentor_name else [],
        warnings=["AI inference unavailable; showing graph-derived checklist only."],
        confidence=0.55,
        fallback_used=True,
        llm_provider="deterministic",
    )


async def generate_survival_plan(
    settings: Settings,
    evidence_bundle: dict[str, Any],
    student_profile: dict[str, Any],
) -> PlanGenerateResponse:
    try:
        provider = get_ai_provider(settings)
    except ValueError as exc:
        logger.warning("No AI provider: %s", exc)
        return _fallback_plan(evidence_bundle)

    try:
        parsed, meta = await provider.generate_plan(evidence_bundle, student_profile)
    except Exception as exc:
        logger.warning("Judge agent AI call failed: %s", exc, exc_info=True)
        return _fallback_plan(evidence_bundle)

    steps_raw = parsed.get("steps") or []
    citation_warnings = validate_entity_citations(
        [s if isinstance(s, dict) else {} for s in steps_raw],
        evidence_bundle,
    )
    steps: list[PlanStep] = []
    for s in steps_raw:
        if not isinstance(s, dict):
            continue
        steps.append(
            PlanStep(
                day_range=str(s.get("day_range", "")),
                action=str(s.get("action", "")),
                entities=list(s.get("entities") or []),
                dependency_reason=str(s.get("dependency_reason", "")),
                source_node_ids=list(s.get("source_node_ids") or []),
            )
        )
    warnings = list(parsed.get("warnings") or []) + citation_warnings
    best_next = parsed.get("best_next_action")
    if isinstance(best_next, str) and best_next.strip():
        best_next_str = best_next.strip()
    elif steps:
        best_next_str = steps[0].action
    else:
        best_next_str = ""

    return PlanGenerateResponse(
        plan_title=str(parsed.get("plan_title") or "Your First 30 Days"),
        best_next_action=best_next_str or None,
        steps=steps,
        priority_contacts=list(parsed.get("priority_contacts") or []),
        warnings=warnings,
        confidence=float(parsed.get("confidence") or 0.75),
        fallback_used=False,
        llm_provider=str(meta.get("provider", provider.name)),
    )
