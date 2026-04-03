"""RocketRide SDK provider using DAP pipelines for plan + bridge generation."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
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
5) Chicago local intelligence: you may weave in worship, grocery, housing areas, exploration spots, and transit tips when those arrays are non-empty - only by naming nodes that appear there. Do not invent routes, schedules, times, or live event dates; if timing is unknown, say so and point to graph notes/maps_query for the student to verify.

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


class RocketRideSdkProvider:
    name = "rocketride_sdk"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def generate_plan(
        self,
        evidence_bundle: dict[str, Any],
        student_profile: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        payload = json.dumps(
            {"student_profile": student_profile, "evidence_bundle": evidence_bundle},
            ensure_ascii=False,
        )
        prompt = f"{_JUDGE_PROMPT}\n\nDATA:\n{payload}"
        parsed = await self._run_pipeline_question(
            pipeline_path=self._settings.rocketride_plan_pipeline,
            prompt=prompt,
        )
        return parsed, {"provider": self.name, "pipeline": self._settings.rocketride_plan_pipeline}

    async def explain_term(
        self,
        term: str,
        home_country: str,
        context: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        prompt = (
            f"{_BRIDGE_PROMPT}\n\n"
            f"term: {term}\n"
            f"home_country: {home_country}\n"
            f"context: {context}\n"
            "No legal guarantees. Plain language."
        )
        parsed = await self._run_pipeline_question(
            pipeline_path=self._settings.rocketride_bridge_pipeline,
            prompt=prompt,
        )
        return parsed, {"provider": self.name, "pipeline": self._settings.rocketride_bridge_pipeline}

    async def _run_pipeline_question(self, *, pipeline_path: str, prompt: str) -> dict[str, Any]:
        RocketRideClient, Question = _load_rocketride_sdk()
        pipeline = self._resolve_pipeline_path(pipeline_path)
        self._prepare_sdk_env()

        token = ""
        async with RocketRideClient(
            uri=self._settings.rocketride_uri.strip(),
            auth=self._settings.rocketride_apikey.strip(),
        ) as client:
            started = await client.use(filepath=str(pipeline))
            token = _extract_token(started)

            question = Question(expectJson=True)
            question.addInstruction("Output", "Return exactly one JSON object. No markdown.")
            question.addQuestion(prompt)
            response = await client.chat(token=token, question=question)

            try:
                return _extract_answer_json(response)
            finally:
                try:
                    await client.terminate(token)
                except Exception as exc:
                    logger.warning("RocketRide terminate failed for token %s: %s", token, exc)

    @staticmethod
    def _resolve_pipeline_path(raw_path: str) -> Path:
        candidate = Path(raw_path).expanduser()
        if not candidate.is_absolute():
            candidate = (Path.cwd() / candidate).resolve()
        if not candidate.exists():
            raise FileNotFoundError(f"RocketRide pipeline file not found: {candidate}")
        return candidate

    def _prepare_sdk_env(self) -> None:
        # RocketRide SDK resolves ${ROCKETRIDE_*} placeholders from env/.env.
        gemini_key = self._settings.rocketride_gemini_key.strip() or self._settings.gemini_api_key.strip()
        if gemini_key:
            os.environ.setdefault("ROCKETRIDE_GEMINI_KEY", gemini_key)


def _load_rocketride_sdk() -> tuple[Any, Any]:
    try:
        from rocketride import RocketRideClient  # type: ignore[import-not-found]
        from rocketride.schema import Question  # type: ignore[import-not-found]
    except Exception as exc:  # pragma: no cover - import availability depends on env
        raise RuntimeError(
            "RocketRide SDK is not installed. Add 'rocketride' to backend dependencies."
        ) from exc
    return RocketRideClient, Question


def _extract_token(started: Any) -> str:
    if not isinstance(started, dict):
        raise RuntimeError("RocketRide use() returned an unexpected payload (expected dict).")
    token = started.get("token")
    if not isinstance(token, str) or not token.strip():
        raise RuntimeError("RocketRide use() did not return a token.")
    return token


def _extract_answer_json(response: Any) -> dict[str, Any]:
    answer_text = _extract_answer_text(response)
    if answer_text:
        parsed = extract_json_object(answer_text)
        if isinstance(parsed, dict):
            return parsed
    raise RuntimeError("RocketRide chat() response did not contain a JSON answer payload.")


def _extract_answer_text(response: Any) -> str:
    if isinstance(response, str):
        return response
    if not isinstance(response, dict):
        return ""

    data = response.get("data")
    if isinstance(data, dict):
        answer = data.get("answer")
        if isinstance(answer, str) and answer.strip():
            return answer

    answers = response.get("answers")
    if isinstance(answers, list):
        for item in answers:
            if isinstance(item, str) and item.strip():
                return item
            if isinstance(item, dict):
                maybe_text = item.get("answer") or item.get("text")
                if isinstance(maybe_text, str) and maybe_text.strip():
                    return maybe_text

    result = response.get("result")
    if isinstance(result, dict):
        nested = _extract_answer_text(result)
        if nested:
            return nested
    return ""
