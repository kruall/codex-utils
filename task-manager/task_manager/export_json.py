from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import TaskManager
from .github_api import fetch_github_tasks


def export_tasks_json(
    tasks_root: str = ".tasks",
    output: str = "tasks.json",
    repos: list[str] | None = None,
    token: str | None = None,
) -> Path:
    """Export all tasks to a JSON file.

    If ``repos`` is provided, tasks from the given GitHub repositories are also
    fetched and included in the output.
    """
    tm = TaskManager(tasks_root)
    tasks = tm.task_list()
    if repos:
        tasks.extend(fetch_github_tasks(repos, token))
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(tasks, indent=2), encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Export tasks to JSON")
    parser.add_argument("--tasks-root", default=".tasks", help="Tasks directory")
    parser.add_argument("--output", default="tasks.json", help="Output file path")
    parser.add_argument(
        "--repo",
        action="append",
        help="GitHub repository in owner/repo format (can be used multiple times)",
    )
    parser.add_argument("--token", help="GitHub token for authenticated requests")
    args = parser.parse_args()
    path = export_tasks_json(
        args.tasks_root,
        args.output,
        repos=args.repo,
        token=args.token,
    )
    print(path)


if __name__ == "__main__":
    main()
