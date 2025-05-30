from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import TaskManager


def export_tasks_json(tasks_root: str = ".tasks", output: str = "tasks.json") -> Path:
    """Export all tasks to a JSON file."""
    tm = TaskManager(tasks_root)
    tasks = tm.task_list()
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(tasks, indent=2), encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Export tasks to JSON")
    parser.add_argument("--tasks-root", default=".tasks", help="Tasks directory")
    parser.add_argument("--output", default="tasks.json", help="Output file path")
    args = parser.parse_args()
    path = export_tasks_json(args.tasks_root, args.output)
    print(path)


if __name__ == "__main__":
    main()
