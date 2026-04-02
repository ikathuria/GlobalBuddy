from __future__ import annotations

import json
from typing import Any

from anyio import to_thread

try:
    from google import genai
except Exception:  # pragma: no cover - handled via runtime fallback
    genai = None  # type: ignore[assignment]

from app.config import Settings
from app.models import (
    BridgeExplainRequest,
    BridgeExplainResponse,
    PlanGenerateRequest,
    PlanGenerateResponse,
    PlanStep,
)


PLAN_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "plan_title": {"type": "string"},
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "day_range": {"type": "string"},
                    "action": {"type": "string"},
                    "entities": {"type": "array", "items": {"type": "string"}},
                    "dependency_reason": {"type": "string"},
                    "source_node_ids": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "day_range",
                    "action",
                    "entities",
                    "dependency_reason",
                    "source_node_ids",
                ],
            },
        },
        "priority_contacts": {"type": "array", "items": {"type": "string"}},
        "warnings": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "number"},
    },
    "required": ["plan_title", "steps", "priority_contacts", "warnings", "confidence"],
}


BRIDGE_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "term": {"type": "string"},
        "plain_explanation": {"type": "string"},
        "home_context_analogy": {"type": "string"},
        "common_mistakes": {"type": "array", "items": {"type": "string"}},
        "what_to_do_next": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "term",
        "plain_explanation",
        "home_context_analogy",
        "common_mistakes",
        "what_to_do_next",
    ],
}


class AiService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def enabled(self) -> bool:
        return bool(genai and self._settings.gemini_api_key)

    async def generate_plan(self, payload: PlanGenerateRequest) -> PlanGenerateResponse:
        if not self.enabled:
            return self._fallback_plan(payload, warning="Gemini is not configured.")

        prompt = self._build_plan_prompt(payload)
        try:
            parsed = await to_thread.run_sync(
                self._generate_structured_json,
                prompt,
                PLAN_JSON_SCHEMA,
            )
            normalized = self._normalize_plan_payload(parsed, payload)
            return PlanGenerateResponse.model_validate(normalized)
        except Exception as exc:
            return self._fallback_plan(
                payload, warning=f"Gemini request failed, fallback plan used: {exc}"
            )

    async def explain_term(self, payload: BridgeExplainRequest) -> BridgeExplainResponse:
        if not self.enabled:
            return self._fallback_bridge(
                payload, warning="Gemini is not configured; deterministic explanation used."
            )

        prompt = self._build_bridge_prompt(payload)
        try:
            parsed = await to_thread.run_sync(
                self._generate_structured_json,
                prompt,
                BRIDGE_JSON_SCHEMA,
            )
            normalized = self._normalize_bridge_payload(parsed, payload)
            return BridgeExplainResponse.model_validate(normalized)
        except Exception as exc:
            return self._fallback_bridge(
                payload, warning=f"Gemini request failed, fallback explanation used: {exc}"
            )

    def _build_plan_prompt(self, payload: PlanGenerateRequest) -> str:
        profile = json.dumps(payload.student_profile, ensure_ascii=True, sort_keys=True)
        evidence = json.dumps(payload.evidence_bundle, ensure_ascii=True, sort_keys=True)
        return (
            "You are the GlobalBuddy Judge Agent.\n"
            "Return ONLY JSON that matches the given schema.\n"
            "Requirements:\n"
            "- Use only entities present in evidence_bundle.\n"
            "- Build an ordered first-30-days plan for international student onboarding.\n"
            "- Respect dependency logic: documentation readiness before banking and rental commitments.\n"
            "- Keep tone warm and practical.\n"
            f"session_id: {payload.session_id}\n"
            f"student_profile: {profile}\n"
            f"evidence_bundle: {evidence}\n"
        )

    def _build_bridge_prompt(self, payload: BridgeExplainRequest) -> str:
        return (
            "You are the GlobalBuddy Cultural Bridge Agent.\n"
            "Return ONLY JSON that matches the given schema.\n"
            "Requirements:\n"
            "- Explain in plain language for a newly arrived international student.\n"
            "- Include a home-country analogy, common mistakes, and concrete next actions.\n"
            f"term: {payload.term}\n"
            f"home_country: {payload.home_country}\n"
            f"context: {payload.context}\n"
        )

    def _generate_structured_json(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        if not genai:
            raise RuntimeError("google-genai package is not installed.")
        if not self._settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is missing.")

        client = genai.Client(api_key=self._settings.gemini_api_key)
        response = client.models.generate_content(
            model=self._settings.gemini_model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": schema,
            },
        )
        text = getattr(response, "text", None)
        if not text:
            raise RuntimeError("Gemini returned an empty response.")
        parsed = self._try_parse_json(text)
        if not isinstance(parsed, dict):
            raise RuntimeError("Gemini response was not valid JSON object.")
        return parsed

    @staticmethod
    def _try_parse_json(value: str) -> Any:
        try:
            return json.loads(value)
        except Exception:
            return None

    def _normalize_plan_payload(
        self, raw: dict[str, Any], payload: PlanGenerateRequest
    ) -> dict[str, Any]:
        title = raw.get("plan_title")
        if not isinstance(title, str) or not title.strip():
            city = payload.student_profile.get("target_city", "your new city")
            title = f"Your First 30 Days in {city}"

        steps = raw.get("steps")
        if not isinstance(steps, list) or not steps:
            fallback = self._fallback_plan(payload, warning="AI response missing steps.")
            return fallback.model_dump()

        normalized_steps = []
        for item in steps:
            if not isinstance(item, dict):
                continue
            normalized_steps.append(
                {
                    "day_range": str(item.get("day_range", "Day 1-3")),
                    "action": str(item.get("action", "Take the next required setup step.")),
                    "entities": [
                        str(entity)
                        for entity in item.get("entities", [])
                        if entity is not None and str(entity).strip()
                    ],
                    "dependency_reason": str(
                        item.get(
                            "dependency_reason",
                            "This step unlocks later requirements.",
                        )
                    ),
                    "source_node_ids": [
                        str(node_id)
                        for node_id in item.get("source_node_ids", [])
                        if node_id is not None and str(node_id).strip()
                    ],
                }
            )

        if not normalized_steps:
            fallback = self._fallback_plan(payload, warning="AI response had no usable steps.")
            return fallback.model_dump()

        contacts = raw.get("priority_contacts")
        warnings = raw.get("warnings")
        confidence = raw.get("confidence", 0.85)

        if not isinstance(confidence, (int, float)):
            confidence = 0.85
        confidence = max(0.0, min(1.0, float(confidence)))

        return {
            "plan_title": title,
            "steps": normalized_steps,
            "priority_contacts": [str(x) for x in contacts] if isinstance(contacts, list) else [],
            "warnings": [str(x) for x in warnings] if isinstance(warnings, list) else [],
            "confidence": confidence,
        }

    def _normalize_bridge_payload(
        self, raw: dict[str, Any], payload: BridgeExplainRequest
    ) -> dict[str, Any]:
        return {
            "term": str(raw.get("term", payload.term)),
            "plain_explanation": str(
                raw.get(
                    "plain_explanation",
                    f"{payload.term} is an important local concept for {payload.context}.",
                )
            ),
            "home_context_analogy": str(
                raw.get(
                    "home_context_analogy",
                    f"Think of it as a similar concept in {payload.home_country}.",
                )
            ),
            "common_mistakes": [
                str(x) for x in raw.get("common_mistakes", []) if x is not None
            ],
            "what_to_do_next": [
                str(x) for x in raw.get("what_to_do_next", []) if x is not None
            ],
        }

    def _fallback_plan(
        self, payload: PlanGenerateRequest, warning: str
    ) -> PlanGenerateResponse:
        profile = payload.student_profile if isinstance(payload.student_profile, dict) else {}
        evidence = payload.evidence_bundle if isinstance(payload.evidence_bundle, dict) else {}
        needs = self._extract_needs(profile)
        target_city = profile.get("target_city", "Chicago")
        mentor_names = self._extract_names(evidence.get("mentors_top3", []))
        resource_names = self._extract_names(evidence.get("resources", []))

        steps: list[PlanStep] = [
            PlanStep(
                day_range="Day 1-2",
                action="Collect passport, I-20, student ID, and address details in one folder.",
                entities=resource_names[:1],
                dependency_reason="Documentation readiness is required before banking and lease decisions.",
                source_node_ids=self._extract_ids(evidence.get("resources", []), limit=1),
            )
        ]

        if "banking" in needs:
            steps.append(
                PlanStep(
                    day_range="Day 2-5",
                    action="Meet a mentor and open a student checking account using your document folder.",
                    entities=mentor_names[:1] + resource_names[:1],
                    dependency_reason="Bank setup supports rent payments and daily transactions.",
                    source_node_ids=self._extract_ids(evidence.get("mentors_top3", []), limit=1),
                )
            )

        if "housing" in needs:
            steps.append(
                PlanStep(
                    day_range="Day 4-10",
                    action="Tour candidate neighborhoods, confirm lease terms, and prepare deposit payment.",
                    entities=mentor_names[:1] + self._extract_names(evidence.get("community_events", []), 1),
                    dependency_reason="Housing commitment should happen after financial setup and document checks.",
                    source_node_ids=self._extract_ids(evidence.get("community_events", []), limit=1),
                )
            )

        steps.append(
            PlanStep(
                day_range="Day 10-30",
                action="Attend one community event per week and build a reliable support circle.",
                entities=self._extract_names(evidence.get("community_events", []), limit=2),
                dependency_reason="Social support improves confidence and reduces onboarding friction.",
                source_node_ids=self._extract_ids(evidence.get("community_events", []), limit=2),
            )
        )

        contacts = mentor_names[:2] + resource_names[:1]
        return PlanGenerateResponse(
            plan_title=f"Your First 30 Days in {target_city}",
            steps=steps,
            priority_contacts=contacts,
            warnings=[warning],
            confidence=0.72,
        )

    def _fallback_bridge(
        self, payload: BridgeExplainRequest, warning: str
    ) -> BridgeExplainResponse:
        term_lower = payload.term.strip().lower()

        if term_lower == "security deposit":
            plain = (
                "A security deposit is money paid upfront to the landlord before move-in. "
                "It is usually refundable when you move out if there is no major damage or unpaid rent."
            )
            analogy = (
                f"In {payload.home_country}, it is similar to giving a refundable advance to confirm commitment."
            )
            mistakes = [
                "Assuming it is the same as the first month of rent.",
                "Not documenting apartment condition at move-in.",
                "Missing written terms on deposit return timeline.",
            ]
            next_steps = [
                "Ask for the exact deposit amount and return conditions in writing.",
                "Take timestamped photos during move-in inspection.",
                "Keep receipts and the signed lease in one folder.",
            ]
        else:
            plain = (
                f"{payload.term} is a local concept used in {payload.context}. "
                "You should verify definition, payment obligations, and deadlines in writing."
            )
            analogy = f"Think of it as a comparable process in {payload.home_country}, but with local legal rules."
            mistakes = [
                "Relying only on verbal explanations.",
                "Ignoring deadlines and required documents.",
            ]
            next_steps = [
                "Ask the provider for written terms and a checklist.",
                "Confirm deadlines and fees before signing anything.",
            ]

        plain_with_note = f"{plain} ({warning})"

        return BridgeExplainResponse(
            term=payload.term,
            plain_explanation=plain_with_note,
            home_context_analogy=analogy,
            common_mistakes=mistakes,
            what_to_do_next=next_steps,
        )

    @staticmethod
    def _extract_needs(profile: dict[str, Any]) -> list[str]:
        raw = profile.get("needs", [])
        if not isinstance(raw, list):
            return []
        return [str(item).strip().lower() for item in raw if str(item).strip()]

    @staticmethod
    def _extract_names(items: Any, limit: int | None = None) -> list[str]:
        if not isinstance(items, list):
            return []
        names = []
        for item in items:
            if isinstance(item, dict):
                name = item.get("name")
                if name:
                    names.append(str(name))
            elif isinstance(item, str):
                names.append(item)
        return names[:limit] if isinstance(limit, int) else names

    @staticmethod
    def _extract_ids(items: Any, limit: int | None = None) -> list[str]:
        if not isinstance(items, list):
            return []
        ids = []
        for item in items:
            if isinstance(item, dict):
                item_id = item.get("id")
                if item_id:
                    ids.append(str(item_id))
        return ids[:limit] if isinstance(limit, int) else ids
