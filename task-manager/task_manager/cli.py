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
    tasks = tm.task_list(args.status, args.queue)
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


def handle_sync(args: argparse.Namespace, tm: TaskManager) -> int:
    repos = args.repo or []
    if not repos:
        print("At least one --repo is required")
        return 1

    imported = tm.sync_from_github(repos, args.token)
    print(f"Imported {len(imported)} tasks")
    return 0


COMMAND_HANDLERS: dict[str, Callable[[argparse.Namespace, TaskManager], int]] = {
    "queue": handle_queue,
    "task": handle_task,
    "ui": handle_ui,
    "dashboard": handle_dashboard,
    "sync": handle_sync,
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

    # Sync command
    sync_parser = subparsers.add_parser(
        "sync", help="Sync tasks from GitHub repositories"
    )
    sync_parser.add_argument(
        "--repo",
        action="append",
        required=True,
        help="GitHub repository in owner/repo format (can be used multiple times)",
    )
    sync_parser.add_argument(
        "--token",
        help="GitHub token for authenticated requests",
    )
    
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

    tm = TaskManager(args.tasks_root)

    handler = COMMAND_HANDLERS.get(args.command)
    if not handler:
        parser.print_help()
        return 1
    return handler(args, tm)

