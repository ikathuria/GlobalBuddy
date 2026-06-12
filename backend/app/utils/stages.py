"""Journey stage helpers shared by profile matching and persistence."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

VALID_STAGES = ("newcomer", "settler", "local", "mentor")
STAGE_RANKS = {stage: index for index, stage in enumerate(VALID_STAGES)}


def parse_arrival_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    raw = str(value).strip()
    if not raw:
        return None
    try:
        return date.fromisoformat(raw[:10])
    except ValueError:
        return None


def infer_user_stage(arrival_date: Any, today: date | None = None) -> str:
    arrived = parse_arrival_date(arrival_date)
    if arrived is None:
        return "newcomer"

    today = today or date.today()
    if arrived > today:
        return "newcomer"

    days_since_arrival = (today - arrived).days
    if days_since_arrival < 90:
        return "newcomer"
    if days_since_arrival < 365:
        return "settler"
    return "local"


def normalize_stage(value: Any, *, allow_mentor: bool = True) -> str | None:
    stage = str(value or "").strip().lower()
    if stage not in VALID_STAGES:
        return None
    if stage == "mentor" and not allow_mentor:
        return None
    return stage


def highest_stage(current: str, inferred: str) -> str:
    current_stage = normalize_stage(current) or "newcomer"
    inferred_stage = normalize_stage(inferred) or "newcomer"
    if STAGE_RANKS[current_stage] >= STAGE_RANKS[inferred_stage]:
        return current_stage
    return inferred_stage
