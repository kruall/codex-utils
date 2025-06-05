import json
import glob
import os
import re
import subprocess
from typing import Optional

from task_manager import TaskManager


def get_task_status_from_commit(task_file: str, commit_hash: str) -> Optional[str]:
    """Get task status from a specific commit."""
    try:
        result = subprocess.run(
            ["git", "show", f"{commit_hash}:{task_file}"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        return data.get("status")
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None


def get_epic_status_from_commit(epic_file: str, commit_hash: str) -> Optional[str]:
    """Get epic status from a specific commit."""
    try:
        result = subprocess.run(
            ["git", "show", f"{commit_hash}:{epic_file}"],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(result.stdout)
        return data.get("status")
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None


def get_task_status_before_pr(task_file: str, pr_base_sha: str) -> Optional[str]:
    """Get task status from the base branch before PR changes."""
    return get_task_status_from_commit(task_file, pr_base_sha)


def get_epic_status_before_pr(epic_file: str, pr_base_sha: str) -> Optional[str]:
    """Get epic status from the base branch before PR changes."""
    return get_epic_status_from_commit(epic_file, pr_base_sha)


def main() -> int:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path or not os.path.exists(event_path):
        print("GITHUB_EVENT_PATH not set or file missing")
        return 1

    with open(event_path, "r", encoding="utf-8") as f:
        event = json.load(f)

    if "pull_request" not in event:
        print("Not a pull request event")
        return 0

    pr = event["pull_request"]
    title = pr.get("title", "")

    # Get base branch SHA to check status before PR
    base_sha = pr.get("base", {}).get("sha")
    if not base_sha:
        print("Could not get base branch SHA")
        return 1

    # Extract item ID from PR title
    match = re.search(r"\[([^\]]+)\]", title)
    if not match:
        print(f"PR title '{title}' does not contain [task-id]")
        return 1

    item_id = match.group(1)

    if item_id.startswith("epic-"):
        epic_file = f".epics/{item_id}.json"
        if not os.path.exists(epic_file):
            print(f"Epic '{item_id}' not found")
            return 1

        with open(epic_file, "r", encoding="utf-8") as f:
            epic_data = json.load(f)
        current_status = epic_data.get("status")

        status_before_pr = get_epic_status_before_pr(epic_file, base_sha)

        print(f"Epic {item_id} status before PR: {status_before_pr}")
        print(f"Epic {item_id} status after PR: {current_status}")

        if status_before_pr == "closed":
            print(
                f"Error: Epic {item_id} was already 'closed' before PR. Epics should not be 'closed' before work starts."
            )
            return 1

        if current_status != "closed":
            print(
                f"Error: Epic {item_id} must be 'closed' when PR is merged; current: {current_status}"
            )
            return 1

        tm = TaskManager(tasks_root=".tasks", epics_root=".epics")
        if item_id in tm.invalid_closed_epics():
            print(
                f"Error: Epic {item_id} has incomplete child tasks or epics"
            )
            return 1

        print(
            f"✓ Epic {item_id} workflow is correct: {status_before_pr} → {current_status}"
        )
    else:
        task_files = glob.glob(f".tasks/**/{item_id}.json", recursive=True)
        if not task_files:
            print(f"Task '{item_id}' not found")
            return 1

        task_file = task_files[0]

        with open(task_file, "r", encoding="utf-8") as f:
            task_data = json.load(f)
        current_status = task_data.get("status")

        status_before_pr = get_task_status_before_pr(task_file, base_sha)

        print(f"Task {item_id} status before PR: {status_before_pr}")
        print(f"Task {item_id} status after PR: {current_status}")

        if status_before_pr == "done":
            print(
                f"Error: Task {item_id} was already 'done' before PR. Tasks should not be 'done' before work starts."
            )
            return 1

        if current_status != "done":
            print(
                f"Error: Task {item_id} must be 'done' when PR is merged; current: {current_status}"
            )
            return 1

        print(
            f"✓ Task {item_id} workflow is correct: {status_before_pr} → {current_status}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
