from __future__ import annotations


def normalize_text_list(values: list[str]) -> list[str]:
    return [value.strip().lower() for value in values if value and value.strip()]


def mentor_score(
    *,
    shared_country: bool,
    shared_university: bool,
    need_overlap_count: int,
    requested_need_count: int,
    trust_score: float,
) -> float:
    need_fit = 0.0
    if requested_need_count > 0:
        need_fit = float(need_overlap_count) / float(requested_need_count)

    score = (
        (0.30 * (1.0 if shared_country else 0.0))
        + (0.25 * (1.0 if shared_university else 0.0))
        + (0.25 * need_fit)
        + (0.20 * trust_score)
    )
    return round(score, 4)
