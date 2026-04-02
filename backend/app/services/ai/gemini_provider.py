"""Google Gemini — structured JSON via response_mime_type application/json."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from app.config import Settings
from app.utils.json_tools import extract_json_object

logger = logging.getLogger(__name__)

_JUDGE_PROMPT = """You are GlobalBuddy's Judge Agent.
Output a single JSON object only. Use ONLY entities and tasks present in evidence_bundle JSON.
Rules:
1) Cite actual names from evidence in each step's entities list.
2) Respect tasks_ordered order for dependencies.
3) Include best_next_action: one concrete sentence for the single most important immediate action.
4) confidence between 0 and 1.

Schema:
{
  "plan_title": string,
  "best_next_action": string,
  "steps": [{"day_range": string, "action": string, "entities": string[], "dependency_reason": string, "source_node_ids": string[]}],
  "priority_contacts": string[],
  "warnings": string[],
  "confidence": number
}
"""

_BRIDGE_PROMPT = """You are GlobalBuddy's Cultural Bridge Agent.
Output a single JSON object only.

Schema:
{
  "plain_explanation": string,
  "home_context_analogy": string,
  "common_mistakes": string[],
  "what_to_do_next": string[]
}
"""


class GeminiProvider:
    name = "gemini"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def generate_plan(
        self,
        evidence_bundle: dict[str, Any],
        student_profile: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        import google.generativeai as genai

        genai.configure(api_key=self._settings.gemini_api_key)
        model = genai.GenerativeModel(self._settings.gemini_model)
        user_blob = json.dumps(
            {"student_profile": student_profile, "evidence_bundle": evidence_bundle},
            ensure_ascii=False,
        )
        prompt = f"{_JUDGE_PROMPT}\n\nDATA:\n{user_blob}"

        def _call() -> str:
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.35,
                ),
            )
            return response.text or ""

        text = await asyncio.to_thread(_call)
        parsed = extract_json_object(text) or {}
        return parsed, {"provider": self.name, "model": self._settings.gemini_model}

    async def explain_term(
        self,
        term: str,
        home_country: str,
        context: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        import google.generativeai as genai

        genai.configure(api_key=self._settings.gemini_api_key)
        model = genai.GenerativeModel(self._settings.gemini_model)
        prompt = (
            f"{_BRIDGE_PROMPT}\n\n"
            f"term: {term}\nhome_country: {home_country}\ncontext: {context}\n"
            "No legal guarantees. Plain language."
        )

        def _call() -> str:
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.3,
                ),
            )
            return response.text or ""

        text = await asyncio.to_thread(_call)
        parsed = extract_json_object(text) or {}
        return parsed, {"provider": self.name, "model": self._settings.gemini_model}
