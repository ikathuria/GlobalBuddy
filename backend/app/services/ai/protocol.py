"""Provider-agnostic AI interface — Gemini today, RocketRide HTTP or other backends later."""

from __future__ import annotations

from typing import Any, Protocol


class AIProvider(Protocol):
    """Structured JSON in / structured dict out. Grounding is enforced via prompts, not here."""

    name: str

    async def generate_plan(
        self,
        evidence_bundle: dict[str, Any],
        student_profile: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Returns (parsed_json, metadata)."""

    async def explain_term(
        self,
        term: str,
        home_country: str,
        context: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Returns (parsed_json, metadata)."""
