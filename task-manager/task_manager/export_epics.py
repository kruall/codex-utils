from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import TaskManager


def export_epics_json(
    tasks_root: str = ".tasks",
    epics_root: str = ".epics",
    output: str = "epics.json",
) -> Path:
    """Export all epics to a JSON file."""

    tm = TaskManager(tasks_root, epics_root)
    epics = tm.epic_list()
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(epics, indent=2), encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Export epics to JSON")
    parser.add_argument("--tasks-root", default=".tasks", help="Tasks directory")
    parser.add_argument("--epics-root", default=".epics", help="Epics directory")
    parser.add_argument("--output", default="epics.json", help="Output file path")
    args = parser.parse_args()

    path = export_epics_json(
        tasks_root=args.tasks_root,
        epics_root=args.epics_root,
        output=args.output,
    )
    print(path)


if __name__ == "__main__":
    main()

