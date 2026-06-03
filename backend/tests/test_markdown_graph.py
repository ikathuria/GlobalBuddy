from __future__ import annotations

from pathlib import Path

from app.models.schemas import ProfileMatchRequest
from app.services.markdown_graph import MarkdownGraphService


def _repo_graph_root() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "graph"


def test_repo_markdown_graph_validates() -> None:
    service = MarkdownGraphService(_repo_graph_root())
    assert service.validation.ok, service.validation.errors
    assert service.health()["source"] == "markdown"
    assert service.health()["node_count"] >= 8


def test_markdown_graph_profile_match_returns_chicago_evidence() -> None:
    service = MarkdownGraphService(_repo_graph_root())
    profile = ProfileMatchRequest(
        full_name="Arjun Mehta",
        email="arjun@example.test",
        country_of_origin="India",
        home_city="Mumbai",
        target_university="Illinois Institute of Technology",
        target_city="Chicago",
        needs=["banking", "housing", "community"],
        interests=["south indian food"],
        religion_or_observance="Hindu",
        diet="vegetarian",
    )

    result = service.profile_match(profile)

    assert result.mentors_top3
    assert result.peers_nearby
    assert result.places_of_worship
    assert result.grocery_stores
    assert result.housing_areas
    assert result.community_groups
    assert result.evidence_bundle["graph_source"] == "markdown"
    assert result.subgraph.nodes


def test_markdown_graph_orders_task_dependencies() -> None:
    service = MarkdownGraphService(_repo_graph_root())
    ordered = [task["id"] for task in service.tasks_ordered("Chicago")]
    assert ordered.index("task_carry_documents") < ordered.index("task_retrieve_i94")
    assert ordered.index("task_retrieve_i94") < ordered.index("task_open_bank_account")


def test_markdown_graph_validation_catches_duplicate_ids(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("---\nid: duplicate\ntype: Mentor\ntitle: A\ncity: Chicago\n---\n", encoding="utf-8")
    (tmp_path / "b.md").write_text("---\nid: duplicate\ntype: Peer\ntitle: B\ncity: Chicago\n---\n", encoding="utf-8")

    service = MarkdownGraphService(tmp_path)

    assert any("Duplicate node id" in error for error in service.validation.errors)


def test_markdown_graph_validation_catches_broken_wikilinks(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text(
        "---\nid: guide_a\ntype: Guide\ntitle: Guide A\ncity: Chicago\n---\nSee [[Missing Page]].",
        encoding="utf-8",
    )

    service = MarkdownGraphService(tmp_path)

    assert any("broken wikilink" in error for error in service.validation.errors)


def test_markdown_graph_validation_catches_missing_required_fields(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("---\nid: guide_a\ntype: Guide\ncity: Chicago\n---\n", encoding="utf-8")

    service = MarkdownGraphService(tmp_path)

    assert any("missing title" in error for error in service.validation.errors)


def test_markdown_graph_validation_catches_task_cycles(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text(
        "---\nid: task_a\ntype: Task\ntitle: Task A\ncity: Chicago\ndepends_on:\n  - task_b\n---\n",
        encoding="utf-8",
    )
    (tmp_path / "b.md").write_text(
        "---\nid: task_b\ntype: Task\ntitle: Task B\ncity: Chicago\ndepends_on:\n  - task_a\n---\n",
        encoding="utf-8",
    )

    service = MarkdownGraphService(tmp_path)

    assert any("Task dependency cycle" in error for error in service.validation.errors)
