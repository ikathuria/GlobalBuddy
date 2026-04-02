"""Cultural Bridge Agent — provider abstraction (Gemini default)."""

from __future__ import annotations

import logging

from app.config import Settings
from app.models.schemas import BridgeExplainResponse
from app.services.ai.factory import get_ai_provider

logger = logging.getLogger(__name__)


def _fallback_bridge(term: str, home_country: str, context: str) -> BridgeExplainResponse:
    return BridgeExplainResponse(
        term=term,
        plain_explanation=(
            f"Baseline US-student explanation for '{term}' in context: {context}. "
            "Orientation-only when AI is unavailable — not legal advice."
        ),
        home_context_analogy=(
            f"Relate '{term}' to something familiar in {home_country}, then compare to your US paperwork."
        ),
        common_mistakes=[
            "Mixing US lease terms with assumptions from another country's rental market.",
            "Relying on verbal promises instead of the written lease.",
        ],
        what_to_do_next=[
            "Verify definitions in your lease and addenda.",
            "Ask ISS or a mentor to sanity-check confusing clauses.",
        ],
        fallback_used=True,
        llm_provider="deterministic",
    )


async def explain_term(
    settings: Settings,
    *,
    term: str,
    home_country: str,
    context: str,
) -> BridgeExplainResponse:
    try:
        provider = get_ai_provider(settings)
    except ValueError:
        return _fallback_bridge(term, home_country, context)

    try:
        parsed, meta = await provider.explain_term(term, home_country, context)
    except Exception as exc:
        logger.warning("Cultural bridge AI failed: %s", exc, exc_info=True)
        return _fallback_bridge(term, home_country, context)

    return BridgeExplainResponse(
        term=term,
        plain_explanation=str(parsed.get("plain_explanation") or ""),
        home_context_analogy=str(parsed.get("home_context_analogy") or ""),
        common_mistakes=list(parsed.get("common_mistakes") or []),
        what_to_do_next=list(parsed.get("what_to_do_next") or []),
        fallback_used=False,
        llm_provider=str(meta.get("provider", provider.name)),
    )
