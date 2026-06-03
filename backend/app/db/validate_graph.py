"""Validate Markdown graph data.

Usage:
    python -m app.db.validate_graph
    python -m app.db.validate_graph --root ../data/graph
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from app.services.markdown_graph import MarkdownGraphService


def main() -> int:
    backend_dir = Path(__file__).resolve().parents[2]
    repo_dir = backend_dir.parent
    parser = argparse.ArgumentParser(description="Validate Globalदोस्त Markdown graph data.")
    parser.add_argument(
        "--root",
        default=str(repo_dir / "data" / "graph"),
        help="Path to graph root. Defaults to repo/data/graph.",
    )
    args = parser.parse_args()

    service = MarkdownGraphService(Path(args.root))
    health = service.health()
    print(
        f"Markdown graph: status={health['status']} "
        f"nodes={health['node_count']} edges={health['edge_count']} root={Path(args.root).resolve()}"
    )

    if service.validation.warnings:
        print("\nWarnings:")
        for warning in service.validation.warnings:
            print(f"- {warning}")

    if service.validation.errors:
        print("\nErrors:")
        for error in service.validation.errors:
            print(f"- {error}")
        return 1

    print("Validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
