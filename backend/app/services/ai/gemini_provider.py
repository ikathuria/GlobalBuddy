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

    async def _generate(self, prompt: str, *, temperature: float, json_output: bool) -> str:
        from google import genai

        client = genai.Client(api_key=self._settings.gemini_api_key)
        config: dict[str, Any] = {"temperature": temperature}
        if json_output:
            config["response_mime_type"] = "application/json"

        def _call() -> str:
            response = client.models.generate_content(
                model=self._settings.gemini_model,
                contents=prompt,
                config=config,
            )
            return response.text or ""

        return await asyncio.to_thread(_call)

    async def generate_plan(
        self,
        evidence_bundle: dict[str, Any],
        student_profile: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        user_blob = json.dumps(
            {"student_profile": student_profile, "evidence_bundle": evidence_bundle},
            ensure_ascii=False,
        )
        prompt = f"{_JUDGE_PROMPT}\n\nDATA:\n{user_blob}"
        text = await self._generate(prompt, temperature=0.35, json_output=True)
        parsed = extract_json_object(text) or {}
        return parsed, {"provider": self.name, "model": self._settings.gemini_model}

    @staticmethod
    def _chat_prompt(history: list[dict], message: str) -> str:
        lines = [_CHAT_SYSTEM, ""]
        for msg in history:
            role = "Student" if msg["role"] == "user" else "Assistant"
            lines.append(f"{role}: {msg['content']}")
        lines.append(f"Student: {message}")
        lines.append("Assistant:")
        return "\n".join(lines)

    async def chat_reply(self, history: list[dict], message: str) -> str:
        """Free-text conversational reply given chat history + new message."""
        return await self._generate(self._chat_prompt(history, message), temperature=0.6, json_output=False)

    async def chat_reply_stream(self, history: list[dict], message: str):
        """Yield the conversational reply incrementally as text chunks."""
        from google import genai

        client = genai.Client(api_key=self._settings.gemini_api_key)
        stream = await client.aio.models.generate_content_stream(
            model=self._settings.gemini_model,
            contents=self._chat_prompt(history, message),
            config={"temperature": 0.6},
        )
        async for chunk in stream:
            if chunk.text:
                yield chunk.text

    async def explain_term(
        self,
        term: str,
        home_country: str,
        context: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        prompt = (
            f"{_BRIDGE_PROMPT}\n\n"
            f"term: {term}\nhome_country: {home_country}\ncontext: {context}\n"
            "No legal guarantees. Plain language."
        )
        text = await self._generate(prompt, temperature=0.3, json_output=True)
        parsed = extract_json_object(text) or {}
        return parsed, {"provider": self.name, "model": self._settings.gemini_model}
