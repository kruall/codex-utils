import json
import glob
import os
import re
import subprocess
from typing import Optional


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


def get_task_status_before_pr(task_file: str, pr_base_sha: str) -> Optional[str]:
    """Get task status from the base branch before PR changes."""
    return get_task_status_from_commit(task_file, pr_base_sha)


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
    action = event.get("action")
    title = pr.get("title", "")
    merged = pr.get("merged", False)
    
    # Get base branch SHA to check status before PR
    base_sha = pr.get("base", {}).get("sha")
    if not base_sha:
        print("Could not get base branch SHA")
        return 1

    # Extract task ID from PR title
    match = re.search(r"\[([^\]]+)\]", title)
    if not match:
        print(f"PR title '{title}' does not contain [task-id]")
        return 1

    task_id = match.group(1)
    task_files = glob.glob(f".tasks/**/{task_id}.json", recursive=True)
    if not task_files:
        print(f"Task '{task_id}' not found")
        return 1

    task_file = task_files[0]
    
    # Get current task status (after PR changes)
    with open(task_file, "r", encoding="utf-8") as f:
        task_data = json.load(f)
    current_status = task_data.get("status")
    
    # Get task status before PR
    status_before_pr = get_task_status_before_pr(task_file, base_sha)
    
    print(f"Task {task_id} status before PR: {status_before_pr}")
    print(f"Task {task_id} status after PR: {current_status}")

    if status_before_pr == "done":
        print(f"Error: Task {task_id} was already 'done' before PR. Tasks should not be 'done' before work starts.")
        return 1
    
    if current_status != "done":
        print(f"Error: Task {task_id} must be 'done' when PR is merged; current: {current_status}")
        return 1
        
    print(f"✓ Task {task_id} workflow is correct: {status_before_pr} → {current_status}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
