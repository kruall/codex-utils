import json
import glob
import os
import re


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

    match = re.search(r"\[([^\]]+)\]", title)
    if not match:
        print(f"PR title '{title}' does not contain [task-id]")
        return 1

    task_id = match.group(1)
    task_files = glob.glob(f".tasks/**/{task_id}.json", recursive=True)
    if not task_files:
        print(f"Task '{task_id}' not found")
        return 1

    with open(task_files[0], "r", encoding="utf-8") as f:
        data = json.load(f)

    status = data.get("status")
    if action == "closed" and merged:
        if status != "done":
            print(f"Task {task_id} must be 'done' after merge; current: {status}")
            return 1
    else:
        if status not in {"todo", "in_progress"}:
            print(
                f"Task {task_id} must be 'todo' or 'in_progress' before merge; current: {status}"
            )
            return 1

    print("Task status validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
