"""Google Gemini — structured JSON via response_mime_type application/json."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from app.config import Settings
from app.utils.json_tools import extract_json_object

logger = logging.getLogger(__name__)

_JUDGE_PROMPT = """You are Globalदोस्त's Judge Agent.
Output a single JSON object only. Use ONLY entities and tasks present in evidence_bundle JSON.
Rules:
1) Cite actual names from evidence in each step's entities list (mentors, peers, restaurants, events, resources, places_of_worship, grocery_stores, housing_areas, exploration_spots, transit_tips).
2) Respect tasks_ordered order for dependencies.
3) Include best_next_action: one concrete sentence for the single most important immediate action.
4) confidence between 0 and 1.
5) Chicago local intelligence: you may weave in worship, grocery, housing areas, exploration spots, and transit tips when those arrays are non-empty — only by naming nodes that appear there. Do not invent routes, schedules, times, or live event dates; if timing is unknown, say so and point to graph notes/maps_query for the student to verify.

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

_BRIDGE_PROMPT = """You are Globalदोस्त's Cultural Bridge Agent.
Output a single JSON object only.

Schema:
{
  "plain_explanation": string,
  "home_context_analogy": string,
  "common_mistakes": string[],
  "what_to_do_next": string[]
}
"""

_CHAT_SYSTEM = """You are Globalदोस्त's AI assistant for international students arriving in the US.
Help with: F-1/J-1 visa paperwork, banking, SSN, housing leases, health insurance, cultural adjustment, campus life, city navigation, and anything a new student might need.
Be concise, friendly, and practical. Use plain language. Do not give legal advice — recommend official sources (ssa.gov, uscis.gov, studentaid.gov) for legal or immigration questions.
Keep replies under 200 words unless the student explicitly asks for more detail."""


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

    async def chat_reply(self, history: list[dict], message: str) -> str:
        """Free-text conversational reply given chat history + new message."""
        import google.generativeai as genai

        genai.configure(api_key=self._settings.gemini_api_key)
        model = genai.GenerativeModel(self._settings.gemini_model)

        lines = [_CHAT_SYSTEM, ""]
        for msg in history:
            role = "Student" if msg["role"] == "user" else "Assistant"
            lines.append(f"{role}: {msg['content']}")
        lines.append(f"Student: {message}")
        lines.append("Assistant:")
        prompt = "\n".join(lines)

        def _call() -> str:
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(temperature=0.6),
            )
            return response.text or ""

        return await asyncio.to_thread(_call)

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
