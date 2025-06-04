import argparse
from pathlib import Path
from typing import Callable

from .core import TaskManager
from .dashboard import generate_dashboard
from .tui import launch_tui
from .utils import format_timestamp, setup_logging, log_error
from .exceptions import TaskManagerError
from . import __version__




def queue_list(args: argparse.Namespace, tm: TaskManager) -> int:
    """Handle `queue list` command."""
    queues = tm.queue_list()
    if not queues:
        print("No queues found")
    else:
        print(f"{'Name':<20} {'Title':<30} {'Description'}")
        print("-" * 80)
        for queue in queues:
            print(
                f"{queue['name']:<20} {queue['title']:<30} {queue['description']}"
            )
    return 0


def queue_add(args: argparse.Namespace, tm: TaskManager) -> int:
    """Handle `queue add` command."""
    try:
        tm.queue_add(args.name, args.title, args.description)
        return 0
    except TaskManagerError as e:
        log_error(f"Error: {e}")
        return 1


def queue_delete(args: argparse.Namespace, tm: TaskManager) -> int:
    """Handle `queue delete` command."""
    try:
        tm.queue_delete(args.name)
        return 0
    except TaskManagerError as e:
        log_error(f"Error: {e}")
        return 1


QUEUE_ACTIONS: dict[str, Callable[[argparse.Namespace, TaskManager], int]] = {
    "list": queue_list,
    "add": queue_add,
    "delete": queue_delete,
}


def print_queue_help(args: argparse.Namespace) -> None:
    """Print the help message for the queue command."""
    print(args.parser_queue.format_help())


def handle_queue(args: argparse.Namespace, tm: TaskManager) -> int:
    action = args.queue_action
    if not action:
        print_queue_help(args)
        return 1
    func = QUEUE_ACTIONS.get(action)
    if not func:
        print_queue_help(args)
        return 1
    return func(args, tm)


def task_list_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    tasks = tm.task_list(args.status, args.queue, args.epic)
    if not tasks:
        print("No tasks found")
    else:
        print(
            f"{'ID':<15} {'Title':<30} {'Status':<12} {'Queue':<15} {'Created'}"
        )
        print("-" * 90)
        for task in tasks:
            queue_name = task['id'].rsplit('-', 1)[0]
            created = format_timestamp(task.get('created_at', 0))
            print(
                f"{task['id']:<15} {task['title']:<30} {task['status']:<12} "
                f"{queue_name:<15} {created}"
            )
    return 0


def task_add_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    try:
        tm.task_add(args.title, args.description, args.queue)
        return 0
    except TaskManagerError as e:
        log_error(f"Error: {e}")
        return 1


def task_delete_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    """Handle `task delete` command."""
    try:
        tm.task_delete(args.id)
        return 0
    except TaskManagerError as e:
        log_error(f"Error: {e}")
        return 1


def task_show_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    try:
        task_data = tm.task_show(args.id)
        print(f"ID: {task_data['id']}")
        print(f"Title: {task_data['title']}")
        print(f"Description: {task_data['description']}")

        epics = tm.task_parent_epics(task_data['id'])
        if epics:
            print("Epics:")
            for epic in epics:
                print(
                    f"  {epic['id']}: {epic['title']} ({epic['status']})"
                )
                print(f"    {epic['description']}")

                other_tasks = [
                    t for t in epic.get('child_tasks', []) if t != task_data['id']
                ]
                if other_tasks:
                    print("    Tasks:")
                    for tid in other_tasks:
                        try:
                            tdata = tm.task_show(tid)
                            print(
                                f"      - {tdata['id']}: {tdata['title']} ({tdata['status']})"
                            )
                        except TaskManagerError:
                            print(f"      - {tid} (missing)")

                child_epics = epic.get('child_epics', [])
                if child_epics:
                    print("    Child Epics:")
                    for eid in child_epics:
                        try:
                            edata = tm.epic_show(eid)
                            print(
                                f"      - {edata['id']}: {edata['title']} ({edata['status']})"
                            )
                        except TaskManagerError:
                            print(f"      - {eid} (missing)")

        print(f"Status: {task_data['status']}")
        print(f"Created: {format_timestamp(task_data.get('created_at', 0))}")
        print(f"Updated: {format_timestamp(task_data.get('updated_at', 0))}")
        if task_data.get('started_at'):
            print(f"Started: {format_timestamp(task_data['started_at'])}")
        if task_data.get('closed_at'):
            print(f"Closed: {format_timestamp(task_data['closed_at'])}")

        comments = task_data.get('comments', [])
        if comments:
            print(f"\nComments ({len(comments)}):")
            for comment in comments:
                created = format_timestamp(comment.get('created_at', 0))
                print(f"  [{comment['id']}] {created}: {comment['text']}")
        else:
            print("\nNo comments")
        return 0
    except TaskManagerError as e:
        log_error(f"Error: {e}")
        return 1


def task_update_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    try:
        tm.task_update(args.id, args.field, args.value)
        return 0
    except TaskManagerError as e:
        log_error(f"Error: {e}")
        return 1


def task_start_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    try:
        tm.task_start(args.id)
        return 0
    except TaskManagerError as e:
        log_error(f"Error: {e}")
        return 1


def task_done_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    try:
        tm.task_done(args.id)
        return 0
    except TaskManagerError as e:
        log_error(f"Error: {e}")
        return 1


def comment_add_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    try:
        tm.task_comment_add(args.id, args.comment)
        return 0
    except TaskManagerError as e:
        log_error(f"Error: {e}")
        return 1


def comment_edit_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    try:
        tm.task_comment_edit(args.id, args.comment_id, args.comment)
        return 0
    except TaskManagerError as e:
        log_error(f"Error: {e}")
        return 1


def comment_remove_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    try:
        tm.task_comment_remove(args.id, args.comment_id)
        return 0
    except TaskManagerError as e:
        log_error(f"Error: {e}")
        return 1


def comment_list_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    try:
        comments = tm.task_comment_list(args.id)
        if not comments:
            print("No comments found")
        else:
            print(f"Comments for task {args.id}:")
            for comment in comments:
                created = format_timestamp(comment.get('created_at', 0))
                print(f"  [{comment['id']}] {created}: {comment['text']}")
        return 0
    except TaskManagerError as e:
        log_error(f"Error: {e}")
        return 1


COMMENT_ACTIONS: dict[str, Callable[[argparse.Namespace, TaskManager], int]] = {
    "add": comment_add_cmd,
    "edit": comment_edit_cmd,
    "remove": comment_remove_cmd,
    "list": comment_list_cmd,
}


def link_add_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    try:
        tm.task_link_add(args.id, args.target_id, args.type)
        return 0
    except TaskManagerError as e:
        log_error(f"Error: {e}")
        return 1


def link_remove_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    try:
        tm.task_link_remove(args.id, args.target_id, args.type)
        return 0
    except TaskManagerError as e:
        log_error(f"Error: {e}")
        return 1


def link_list_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    try:
        links = tm.task_link_list(args.id)
        if not links:
            print("No links found")
        else:
            print(f"Links for task {args.id}:")
            for link_type, targets in links.items():
                for target in targets:
                    print(f"  {link_type}: {target}")
        return 0
    except TaskManagerError as e:
        log_error(f"Error: {e}")
        return 1


LINK_ACTIONS: dict[str, Callable[[argparse.Namespace, TaskManager], int]] = {
    "add": link_add_cmd,
    "remove": link_remove_cmd,
    "list": link_list_cmd,
}


def task_add_to_epic_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    try:
        tm.epic_add_task(args.epic_id, args.id)
        return 0
    except TaskManagerError as e:
        log_error(f"Error: {e}")
        return 1


def task_remove_from_epic_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    try:
        tm.epic_remove_task(args.epic_id, args.id)
        return 0
    except TaskManagerError as e:
        log_error(f"Error: {e}")
        return 1


def epic_list_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    epics = tm.epic_list()
    if not epics:
        print("No epics found")
    else:
        print(f"{'ID':<10} {'Title':<30} {'Status':<10} {'Created'}")
        print("-" * 70)
        for epic in epics:
            created = format_timestamp(epic.get('created_at', 0))
            print(
                f"{epic['id']:<10} {epic['title']:<30} {epic['status']:<10} {created}"
            )
    return 0


def epic_add_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    try:
        tm.epic_add(args.title, args.description)
        return 0
    except TaskManagerError as e:
        log_error(f"Error: {e}")
        return 1


def epic_show_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    try:
        data = tm.epic_show(args.id)
        print(f"ID: {data['id']}")
        print(f"Title: {data['title']}")
        print(f"Description: {data['description']}")
        print(f"Status: {data['status']}")
        print(f"Created: {format_timestamp(data.get('created_at', 0))}")
        print(f"Updated: {format_timestamp(data.get('updated_at', 0))}")
        if data.get('parent_epic'):
            print(f"Parent: {data['parent_epic']}")
        if data.get('child_tasks'):
            print("Tasks:")
            for t in data['child_tasks']:
                print(f"  - {t}")
        if data.get('child_epics'):
            print("Epics:")
            for e in data['child_epics']:
                print(f"  - {e}")
        return 0
    except TaskManagerError as e:
        log_error(f"Error: {e}")
        return 1


def epic_update_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    try:
        tm.epic_update(args.id, args.field, args.value)
        return 0
    except TaskManagerError as e:
        log_error(f"Error: {e}")
        return 1


def epic_done_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    try:
        tm.epic_done(args.id)
        return 0
    except TaskManagerError as e:
        log_error(f"Error: {e}")
        return 1


def epic_add_task_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    try:
        tm.epic_add_task(args.id, args.task_id)
        return 0
    except TaskManagerError as e:
        log_error(f"Error: {e}")
        return 1


def epic_add_epic_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    try:
        tm.epic_add_epic(args.id, args.child_id)
        return 0
    except TaskManagerError as e:
        log_error(f"Error: {e}")
        return 1


def epic_remove_task_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    try:
        tm.epic_remove_task(args.id, args.task_id)
        return 0
    except TaskManagerError as e:
        log_error(f"Error: {e}")
        return 1


def epic_remove_epic_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    try:
        tm.epic_remove_epic(args.id, args.child_id)
        return 0
    except TaskManagerError as e:
        log_error(f"Error: {e}")
        return 1


EPIC_ACTIONS: dict[str, Callable[[argparse.Namespace, TaskManager], int]] = {
    "list": epic_list_cmd,
    "add": epic_add_cmd,
    "show": epic_show_cmd,
    "update": epic_update_cmd,
    "done": epic_done_cmd,
    "add-task": epic_add_task_cmd,
    "add-epic": epic_add_epic_cmd,
    "remove-task": epic_remove_task_cmd,
    "remove-epic": epic_remove_epic_cmd,
}


def handle_epic(args: argparse.Namespace, tm: TaskManager) -> int:
    action = args.epic_action
    if not action:
        print(args.parser_epic.format_help())
        return 1
    func = EPIC_ACTIONS.get(action)
    if not func:
        print(args.parser_epic.format_help())
        return 1
    return func(args, tm)


def handle_comment(args: argparse.Namespace, tm: TaskManager) -> int:
    action = args.comment_action
    if not action:
        print(args.parser_comment.format_help())
        return 1
    func = COMMENT_ACTIONS.get(action)
    if not func:
        print(args.parser_comment.format_help())
        return 1
    return func(args, tm)


def handle_link(args: argparse.Namespace, tm: TaskManager) -> int:
    action = args.link_action
    if not action:
        print(args.parser_link.format_help())
        return 1
    func = LINK_ACTIONS.get(action)
    if not func:
        print(args.parser_link.format_help())
        return 1
    return func(args, tm)


TASK_ACTIONS: dict[str, Callable[[argparse.Namespace, TaskManager], int]] = {
    "list": task_list_cmd,
    "add": task_add_cmd,
    "delete": task_delete_cmd,
    "show": task_show_cmd,
    "update": task_update_cmd,
    "start": task_start_cmd,
    "done": task_done_cmd,
    "comment": handle_comment,
    "link": handle_link,
    "add-to-epic": task_add_to_epic_cmd,
    "remove-from-epic": task_remove_from_epic_cmd,
}


def handle_task(args: argparse.Namespace, tm: TaskManager) -> int:
    action = args.task_action
    if not action:
        print(args.parser_task.format_help())
        return 1
    func = TASK_ACTIONS.get(action)
    if not func:
        print(args.parser_task.format_help())
        return 1
    return func(args, tm)


def handle_ui(args: argparse.Namespace, tm: TaskManager) -> int:
    launch_tui(tm)
    return 0


def handle_dashboard(args: argparse.Namespace, tm: TaskManager) -> int:
    path = generate_dashboard(
        args.tasks_root,
        args.output,
        repos=args.repo,
        token=args.token,
    )
    print(f"Dashboard generated at {path}")
    return 0


def verify_cmd(args: argparse.Namespace, tm: TaskManager) -> int:
    """Check for common issues before finishing work."""
    tm.repair_links()
    tasks = tm.task_list(status="in_progress")
    invalid_epics = tm.invalid_closed_epics()

    if not tasks and not invalid_epics:
        print("\u2705 No tasks in progress and all epics valid")
        return 0

    if tasks:
        task_ids = ", ".join(t["id"] for t in tasks)
        count = len(tasks)
        plural = "task" if count == 1 else "tasks"
        print(f"\u274C Found {count} {plural} in progress: {task_ids}")
        print("Run: ./tm task done --id <task-id> to close them.")

    if invalid_epics:
        epic_ids = ", ".join(invalid_epics)
        count = len(invalid_epics)
        plural = "epic" if count == 1 else "epics"
        print(f"\u274C Found {count} {plural} with invalid status: {epic_ids}")
        print("Ensure all child tasks and epics are done, then run: ./tm epic done --id <epic-id>")

    return 1


COMMAND_HANDLERS: dict[str, Callable[[argparse.Namespace, TaskManager], int]] = {
    "queue": handle_queue,
    "task": handle_task,
    "epic": handle_epic,
    "ui": handle_ui,
    "dashboard": handle_dashboard,
    "verify": verify_cmd,
}

def main():
    setup_logging()

    parser = argparse.ArgumentParser(description="Task Manager CLI")
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information and exit",
    )
    parser.add_argument(
        "--tasks-root",
        default=".tasks",
        help="Root directory for tasks storage (default: .tasks)",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # UI command
    subparsers.add_parser("ui", help="Launch interactive Textual UI")

    # Dashboard command
    dashboard_parser = subparsers.add_parser(
        "dashboard", help="Generate static HTML dashboard"
    )
    dashboard_parser.add_argument(
        "--output",
        default="docs/index.html",
        help="Output HTML file (default: docs/index.html)",
    )
    dashboard_parser.add_argument(
        "--repo",
        action="append",
        help="GitHub repository in owner/repo format (can be used multiple times)",
    )
    dashboard_parser.add_argument(
        "--token",
        help="GitHub token for authenticated requests",
    )

    # Verify command
    subparsers.add_parser("verify", help="Verify no tasks are left in progress")
    
    # Queue commands
    queue_parser = subparsers.add_parser("queue", help="Queue management")
    queue_subparsers = queue_parser.add_subparsers(dest="queue_action", help="Queue actions")
    
    # queue list
    queue_subparsers.add_parser("list", help="List all queues")
    
    # queue add
    queue_add_parser = queue_subparsers.add_parser("add", help="Add a new queue")
    queue_add_parser.add_argument("--name", required=True, help="Queue name")
    queue_add_parser.add_argument("--title", required=True, help="Queue title")
    queue_add_parser.add_argument("--description", required=True, help="Queue description")

    # queue delete
    queue_delete_parser = queue_subparsers.add_parser("delete", help="Delete a queue")
    queue_delete_parser.add_argument("--name", required=True, help="Queue name")
    
    # Task commands
    task_parser = subparsers.add_parser("task", help="Task management")
    task_subparsers = task_parser.add_subparsers(dest="task_action", help="Task actions")
    
    # task list
    task_list_parser = task_subparsers.add_parser("list", help="List tasks")
    task_list_parser.add_argument("--status", help="Filter by status")
    task_list_parser.add_argument("--queue", help="Filter by queue")
    task_list_parser.add_argument("--epic", help="Filter by epic")
    
    # task add
    task_add_parser = task_subparsers.add_parser("add", help="Add a new task")
    task_add_parser.add_argument("--title", required=True, help="Task title")
    task_add_parser.add_argument("--description", required=True, help="Task description")
    task_add_parser.add_argument("--queue", required=True, help="Queue name")

    # task delete
    task_delete_parser = task_subparsers.add_parser("delete", help="Delete a task")
    task_delete_parser.add_argument("--id", required=True, help="Task ID")
    
    # task show
    task_show_parser = task_subparsers.add_parser("show", help="Show task details")
    task_show_parser.add_argument("--id", required=True, help="Task ID")
    
    # task update
    task_update_parser = task_subparsers.add_parser("update", help="Update a task")
    task_update_parser.add_argument("--id", required=True, help="Task ID")
    task_update_parser.add_argument("--field", required=True, help="Field to update")
    task_update_parser.add_argument("--value", required=True, help="New value")
    
    # task start
    task_start_parser = task_subparsers.add_parser("start", help="Start a task")
    task_start_parser.add_argument("--id", required=True, help="Task ID")
    
    # task done
    task_done_parser = task_subparsers.add_parser("done", help="Mark task as done")
    task_done_parser.add_argument("--id", required=True, help="Task ID")
    
    # task comment commands
    task_comment_parser = task_subparsers.add_parser("comment", help="Task comment management")
    task_comment_subparsers = task_comment_parser.add_subparsers(dest="comment_action", help="Comment actions")
    
    # task comment add
    task_comment_add_parser = task_comment_subparsers.add_parser("add", help="Add a comment to task")
    task_comment_add_parser.add_argument("--id", required=True, help="Task ID")
    task_comment_add_parser.add_argument("--comment", required=True, help="Comment text")

    # task comment edit
    task_comment_edit_parser = task_comment_subparsers.add_parser("edit", help="Edit a comment on task")
    task_comment_edit_parser.add_argument("--id", required=True, help="Task ID")
    task_comment_edit_parser.add_argument("--comment-id", type=int, required=True, help="Comment ID")
    task_comment_edit_parser.add_argument("--comment", required=True, help="New comment text")
    
    # task comment remove
    task_comment_remove_parser = task_comment_subparsers.add_parser("remove", help="Remove a comment from task")
    task_comment_remove_parser.add_argument("--id", required=True, help="Task ID")
    task_comment_remove_parser.add_argument("--comment-id", type=int, required=True, help="Comment ID")
    
    # task comment list
    task_comment_list_parser = task_comment_subparsers.add_parser("list", help="List task comments")
    task_comment_list_parser.add_argument("--id", required=True, help="Task ID")

    # task link commands
    task_link_parser = task_subparsers.add_parser("link", help="Task link management")
    task_link_subparsers = task_link_parser.add_subparsers(dest="link_action", help="Link actions")

    # task link add
    task_link_add_parser = task_link_subparsers.add_parser("add", help="Add a link between tasks")
    task_link_add_parser.add_argument("--id", required=True, help="Task ID")
    task_link_add_parser.add_argument("--target-id", required=True, help="Target task ID")
    task_link_add_parser.add_argument("--type", default="related", help="Link type")

    # task link remove
    task_link_remove_parser = task_link_subparsers.add_parser("remove", help="Remove a link between tasks")
    task_link_remove_parser.add_argument("--id", required=True, help="Task ID")
    task_link_remove_parser.add_argument("--target-id", required=True, help="Target task ID")
    task_link_remove_parser.add_argument("--type", default="related", help="Link type")

    # task link list
    task_link_list_parser = task_link_subparsers.add_parser("list", help="List task links")
    task_link_list_parser.add_argument("--id", required=True, help="Task ID")

    # task add-to-epic
    task_add_epic_parser = task_subparsers.add_parser("add-to-epic", help="Add task to epic")
    task_add_epic_parser.add_argument("--id", required=True, help="Task ID")
    task_add_epic_parser.add_argument("--epic-id", required=True, help="Epic ID")

    # task remove-from-epic
    task_remove_epic_parser = task_subparsers.add_parser("remove-from-epic", help="Remove task from epic")
    task_remove_epic_parser.add_argument("--id", required=True, help="Task ID")
    task_remove_epic_parser.add_argument("--epic-id", required=True, help="Epic ID")

    # Epic commands
    epic_parser = subparsers.add_parser("epic", help="Epic management")
    epic_subparsers = epic_parser.add_subparsers(dest="epic_action", help="Epic actions")

    # epic list
    epic_subparsers.add_parser("list", help="List epics")

    # epic add
    epic_add_parser = epic_subparsers.add_parser("add", help="Add a new epic")
    epic_add_parser.add_argument("--title", required=True, help="Epic title")
    epic_add_parser.add_argument("--description", required=True, help="Epic description")

    # epic show
    epic_show_parser = epic_subparsers.add_parser("show", help="Show epic details")
    epic_show_parser.add_argument("--id", required=True, help="Epic ID")

    # epic update
    epic_update_parser = epic_subparsers.add_parser("update", help="Update an epic")
    epic_update_parser.add_argument("--id", required=True, help="Epic ID")
    epic_update_parser.add_argument("--field", required=True, help="Field to update")
    epic_update_parser.add_argument("--value", required=True, help="New value")

    # epic done
    epic_done_parser = epic_subparsers.add_parser("done", help="Mark epic as done")
    epic_done_parser.add_argument("--id", required=True, help="Epic ID")

    # epic add-task
    epic_add_task_parser = epic_subparsers.add_parser("add-task", help="Add task to epic")
    epic_add_task_parser.add_argument("--id", required=True, help="Epic ID")
    epic_add_task_parser.add_argument("--task-id", required=True, help="Task ID")

    # epic add-epic
    epic_add_epic_parser = epic_subparsers.add_parser("add-epic", help="Add child epic")
    epic_add_epic_parser.add_argument("--id", required=True, help="Epic ID")
    epic_add_epic_parser.add_argument("--child-id", required=True, help="Child epic ID")

    # epic remove-task
    epic_remove_task_parser = epic_subparsers.add_parser("remove-task", help="Remove task from epic")
    epic_remove_task_parser.add_argument("--id", required=True, help="Epic ID")
    epic_remove_task_parser.add_argument("--task-id", required=True, help="Task ID")

    # epic remove-epic
    epic_remove_epic_parser = epic_subparsers.add_parser("remove-epic", help="Remove child epic")
    epic_remove_epic_parser.add_argument("--id", required=True, help="Epic ID")
    epic_remove_epic_parser.add_argument("--child-id", required=True, help="Child epic ID")
    
    args = parser.parse_args()

    if args.version:
        print(f"Task Manager CLI version {__version__}")
        print(f"Tasks directory: {Path(args.tasks_root).resolve()}")
        return 0

    if not args.command:
        parser.print_help()
        return 1

    args.parser_queue = queue_parser
    args.parser_task = task_parser
    args.parser_comment = task_comment_parser
    args.parser_link = task_link_parser
    args.parser_epic = epic_parser

    tm = TaskManager(args.tasks_root)

    handler = COMMAND_HANDLERS.get(args.command)
    if not handler:
        parser.print_help()
        return 1
    return handler(args, tm)

