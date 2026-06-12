from __future__ import annotations

from datetime import date

from app.utils.stages import highest_stage, infer_user_stage, normalize_stage, parse_arrival_date


def test_infer_user_stage_defaults_to_newcomer_without_arrival_date() -> None:
    assert infer_user_stage("", today=date(2026, 6, 3)) == "newcomer"
    assert infer_user_stage("not-a-date", today=date(2026, 6, 3)) == "newcomer"


def test_infer_user_stage_from_arrival_date_thresholds() -> None:
    today = date(2026, 6, 3)

    assert infer_user_stage("2026-05-01", today=today) == "newcomer"
    assert infer_user_stage("2026-02-15", today=today) == "settler"
    assert infer_user_stage("2025-01-15", today=today) == "local"
    assert infer_user_stage("2026-08-01", today=today) == "newcomer"


def test_stage_helpers_reject_invalid_manual_mentor_upgrade() -> None:
    assert parse_arrival_date("2026-06-03").isoformat() == "2026-06-03"
    assert normalize_stage("mentor", allow_mentor=False) is None
    assert highest_stage("settler", "newcomer") == "settler"
