"""Seed quality validator — checks required nodes and properties per city.

Usage:
    cd backend
    python -m app.db.validate_seed
    python -m app.db.validate_seed --city chicago
    python -m app.db.validate_seed --city boston
    python -m app.db.validate_seed --city new_york
"""

from __future__ import annotations

import asyncio
import logging
from argparse import ArgumentParser

from app.config import get_neo4j_settings
from app.db.neo4j_client import Neo4jClient

logger = logging.getLogger(__name__)

_CITY_NAMES = {
    "chicago": "Chicago",
    "boston": "Boston",
    "new_york": "New York",
}

_MIN_COUNTS = {
    "Mentor": 2,
    "PlaceOfWorship": 1,
    "GroceryStore": 1,
    "HousingArea": 1,
    "ExplorationSpot": 1,
    "TransitTip": 1,
}


async def _validate(client: Neo4jClient, city_key: str) -> list[str]:
    """Return a list of warning strings (empty = clean)."""
    city_name = _CITY_NAMES.get(city_key.lower())
    if not city_name:
        return [f"Unknown city key '{city_key}'. Known: {list(_CITY_NAMES)}"]

    warnings: list[str] = []

    # 1. Check city node exists
    rows = await client.query("MATCH (c:City {name: $name}) RETURN count(c) AS n", {"name": city_name})
    if not rows or int(rows[0]["n"]) == 0:
        warnings.append(f"MISSING City node with name='{city_name}'")
        return warnings  # nothing else will work without the city

    # 2. Node count minimums
    for label, minimum in _MIN_COUNTS.items():
        rows = await client.query(
            f"MATCH (n:{label}) WHERE n.city_name = $city RETURN count(n) AS cnt",
            {"city": city_name},
        )
        count = int(rows[0]["cnt"]) if rows else 0
        if count < minimum:
            warnings.append(f"LOW {label} count for {city_name}: {count} (expected >= {minimum})")

    # 3. LocalEntity nodes missing maps_link
    for label in ("PlaceOfWorship", "GroceryStore", "HousingArea", "ExplorationSpot"):
        rows = await client.query(
            f"MATCH (n:{label}) WHERE n.city_name = $city AND (n.maps_link IS NULL OR n.maps_link = '') RETURN n.id AS id",
            {"city": city_name},
        )
        for row in rows:
            warnings.append(f"MISSING maps_link on {label} id={row['id']}")

    # 4. Mentor nodes missing email
    rows = await client.query(
        "MATCH (m:Mentor) WHERE m.city_name = $city AND (m.email IS NULL OR m.email = '') RETURN m.id AS id",
        {"city": city_name},
    )
    for row in rows:
        warnings.append(f"MISSING email on Mentor id={row['id']}")

    # 5. Task nodes missing PRECEDES edge
    rows = await client.query(
        "MATCH (t:Task) WHERE NOT (t)-[:PRECEDES]->() AND NOT ()-[:PRECEDES]->(t) RETURN t.id AS id",
        {},
    )
    for row in rows:
        warnings.append(f"Task id={row['id']} has no PRECEDES edges (isolated)")

    # 6. Mentors in this city not connected to a university
    rows = await client.query(
        "MATCH (m:Mentor) WHERE m.city_name = $city AND NOT (m)-[:AFFILIATED_WITH]->(:University) RETURN m.id AS id",
        {"city": city_name},
    )
    for row in rows:
        warnings.append(f"Mentor id={row['id']} missing AFFILIATED_WITH University edge")

    return warnings


async def run(city_keys: list[str]) -> None:
    settings = get_neo4j_settings()
    client = Neo4jClient(uri=settings.neo4j_uri, user=settings.neo4j_user, password=settings.neo4j_password)
    await client.connect()
    try:
        all_clean = True
        for key in city_keys:
            print(f"\n=== Validating city: {key} ===")
            warnings = await _validate(client, key)
            if warnings:
                all_clean = False
                for w in warnings:
                    print(f"  WARN  {w}")
            else:
                print("  OK  All checks passed.")
        print()
        if all_clean:
            print("All cities passed validation.")
        else:
            print("Validation complete — warnings found (see above).")
    finally:
        await client.close()


def main() -> None:
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
    parser = ArgumentParser(description="Validate Neo4j seed data quality per city.")
    parser.add_argument("--city", default=None, help="City key: chicago, boston, new_york (default: all)")
    args = parser.parse_args()
    cities = [args.city] if args.city else list(_CITY_NAMES)
    asyncio.run(run(cities))


if __name__ == "__main__":
    main()
