"""Citation validation for AI-generated steps against Neo4j evidence bundles."""

from __future__ import annotations

from typing import Any


def validate_entity_citations(
    steps: list[dict[str, Any]],
    evidence_bundle: dict[str, Any],
) -> list[str]:
    """Entity strings in steps should appear in evidence names."""
    known: set[str] = set()
    list_keys = (
        "mentors",
        "mentors_top3",
        "peers",
        "peers_nearby",
        "cultural_restaurants",
        "restaurants",
        "community_events",
        "events",
        "resources",
        "places_of_worship",
        "grocery_stores",
        "housing_areas",
        "exploration_spots",
        "transit_tips",
    )
    for key in list_keys:
        for item in evidence_bundle.get(key, []) or []:
            if isinstance(item, dict) and item.get("name"):
                known.add(str(item["name"]))

    warnings: list[str] = []
    for step in steps:
        for ent in step.get("entities", []) or []:
            if ent and ent not in known:
                warnings.append(f"Step cites entity not present in evidence bundle: {ent}")
    return warnings
