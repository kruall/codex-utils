#!/usr/bin/env python3
"""
Task Manager CLI tool for managing queues and tasks.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, TYPE_CHECKING


class TaskManager:
    def __init__(self, tasks_root: str = ".tasks"):
        self.tasks_root = Path(tasks_root)
        self.tasks_root.mkdir(exist_ok=True)

    def queue_list(self) -> List[Dict[str, str]]:
        """List all queues."""
        queues = []
        for queue_dir in self.tasks_root.iterdir():
            if queue_dir.is_dir():
                meta_file = queue_dir / "meta.json"
                if meta_file.exists():
                    try:
                        with open(meta_file, 'r') as f:
                            meta = json.load(f)
                            queues.append({
                                'name': queue_dir.name,
                                'title': meta.get('title', ''),
                                'description': meta.get('description', '')
                            })
                    except (json.JSONDecodeError, IOError):
                        # Skip corrupted meta files
                        continue
        return queues

    def queue_add(self, name: str, title: str, description: str) -> bool:
        """Add a new queue."""
        # Validate queue name
        if not name or not name.strip():
            print("Error: Queue name cannot be empty", file=sys.stderr)
            return False
        
        queue_dir = self.tasks_root / name

        # Check write permissions on tasks root by inspecting mode bits
        try:
            import stat
            mode = os.stat(self.tasks_root).st_mode
            write_bits = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
            if not (mode & write_bits):
                print(
                    f"Error creating queue '{name}': Permission denied",
                    file=sys.stderr,
                )
                return False
        except OSError as e:
            print(f"Error creating queue '{name}': {e}", file=sys.stderr)
            return False

        try:
            if queue_dir.exists():
                print(f"Error: Queue '{name}' already exists", file=sys.stderr)
                return False
        except (OSError, PermissionError):
            # If we can't check if it exists due to permissions, try to create anyway
            pass
        
        try:
            queue_dir.mkdir(parents=True)
            meta_file = queue_dir / "meta.json"
            
            meta_data = {
                'title': title,
                'description': description
            }
            
            with open(meta_file, 'w') as f:
                json.dump(meta_data, f, indent=2)
            
            print(f"Queue '{name}' created successfully")
            return True
            
        except (OSError, IOError) as e:
            print(f"Error creating queue '{name}': {e}", file=sys.stderr)
            return False

    def _get_next_task_number(self, queue_name: str) -> int:
        """Get the next available task number for a queue."""
        queue_dir = self.tasks_root / queue_name
        if not queue_dir.exists():
            return 1
        
        max_num = 0
        for task_file in queue_dir.glob(f"{queue_name}-*.json"):
            try:
                # Extract number from filename like "queue-name-123.json"
                filename = task_file.stem
                if filename.startswith(f"{queue_name}-"):
                    num_str = filename[len(queue_name) + 1:]
                    num = int(num_str)
                    max_num = max(max_num, num)
            except ValueError:
                continue
        
        return max_num + 1

    def task_add(self, title: str, description: str, queue: str) -> Optional[str]:
        """Add a new task to a queue."""
        queue_dir = self.tasks_root / queue
        
        if not queue_dir.exists():
            print(f"Error: Queue '{queue}' does not exist", file=sys.stderr)
            return None
        
        try:
            task_num = self._get_next_task_number(queue)
            task_id = f"{queue}-{task_num}"
            task_file = queue_dir / f"{task_id}.json"
            
            task_data = {
                'id': task_id,
                'title': title,
                'description': description,
                'status': 'todo',
                'comments': [],
                'created_at': time.time(),
                'updated_at': time.time()
            }
            
            with open(task_file, 'w') as f:
                json.dump(task_data, f, indent=2)
            
            print(f"Task '{task_id}' created successfully")
            return task_id
            
        except (OSError, IOError) as e:
            print(f"Error creating task: {e}", file=sys.stderr)
            return None

    def _find_task_file(self, task_id: str) -> Optional[Path]:
        """Find the task file for a given task ID."""
        if '-' not in task_id:
            return None
        
        queue_name = task_id.rsplit('-', 1)[0]
        queue_dir = self.tasks_root / queue_name
        task_file = queue_dir / f"{task_id}.json"
        
        if task_file.exists():
            return task_file
        return None

    def _load_task(self, task_id: str) -> Optional[Dict]:
        """Load task data from file."""
        task_file = self._find_task_file(task_id)
        if not task_file:
            return None
        
        try:
            with open(task_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def _save_task(self, task_data: Dict) -> bool:
        """Save task data to file."""
        task_id = task_data['id']
        task_file = self._find_task_file(task_id)
        if not task_file:
            return False
        
        try:
            task_data['updated_at'] = time.time()
            with open(task_file, 'w') as f:
                json.dump(task_data, f, indent=2)
            return True
        except (OSError, IOError):
            return False

    def task_list(self, status: Optional[str] = None, queue: Optional[str] = None) -> List[Dict]:
        """List tasks with optional filtering."""
        tasks = []
        
        # Determine which queues to search
        if queue:
            queue_dirs = [self.tasks_root / queue] if (self.tasks_root / queue).exists() else []
        else:
            queue_dirs = [d for d in self.tasks_root.iterdir() if d.is_dir()]
        
        for queue_dir in queue_dirs:
            for task_file in queue_dir.glob("*.json"):
                if task_file.name == "meta.json":
                    continue
                
                try:
                    with open(task_file, 'r') as f:
                        task_data = json.load(f)
                    
                    # Filter by status if specified
                    if status and task_data.get('status') != status:
                        continue
                    
                    tasks.append(task_data)
                except (json.JSONDecodeError, IOError):
                    continue
        
        # Sort by creation time
        tasks.sort(key=lambda t: t.get('created_at', 0))
        return tasks

    def task_show(self, task_id: str) -> Optional[Dict]:
        """Show detailed information about a task."""
        task_data = self._load_task(task_id)
        if not task_data:
            print(f"Error: Task '{task_id}' not found", file=sys.stderr)
            return None
        
        return task_data

    def task_update(self, task_id: str, field: str, value: str) -> bool:
        """Update a specific field of a task."""
        task_data = self._load_task(task_id)
        if not task_data:
            print(f"Error: Task '{task_id}' not found", file=sys.stderr)
            return False
        
        # Validate field
        allowed_fields = ['title', 'description', 'status']
        if field not in allowed_fields:
            print(f"Error: Field '{field}' is not allowed. Allowed fields: {', '.join(allowed_fields)}", file=sys.stderr)
            return False
        
        task_data[field] = value
        
        if self._save_task(task_data):
            print(f"Task '{task_id}' updated successfully")
            return True
        else:
            print(f"Error: Failed to update task '{task_id}'", file=sys.stderr)
            return False

    def task_start(self, task_id: str) -> bool:
        """Start a task (set status to 'in_progress')."""
        return self.task_update(task_id, 'status', 'in_progress')

    def task_done(self, task_id: str) -> bool:
        """Mark a task as done (set status to 'done')."""
        return self.task_update(task_id, 'status', 'done')

    def task_comment_add(self, task_id: str, comment: str) -> bool:
        """Add a comment to a task."""
        task_data = self._load_task(task_id)
        if not task_data:
            print(f"Error: Task '{task_id}' not found", file=sys.stderr)
            return False
        
        # Generate comment ID
        existing_ids = [c.get('id', 0) for c in task_data.get('comments', [])]
        comment_id = max(existing_ids, default=0) + 1
        
        comment_data = {
            'id': comment_id,
            'text': comment,
            'created_at': time.time()
        }
        
        if 'comments' not in task_data:
            task_data['comments'] = []
        
        task_data['comments'].append(comment_data)
        
        if self._save_task(task_data):
            print(f"Comment added to task '{task_id}' with ID {comment_id}")
            return True
        else:
            print(f"Error: Failed to add comment to task '{task_id}'", file=sys.stderr)
            return False

    def task_comment_remove(self, task_id: str, comment_id: int) -> bool:
        """Remove a comment from a task."""
        task_data = self._load_task(task_id)
        if not task_data:
            print(f"Error: Task '{task_id}' not found", file=sys.stderr)
            return False
        
        comments = task_data.get('comments', [])
        original_count = len(comments)
        
        # Remove comment with matching ID
        task_data['comments'] = [c for c in comments if c.get('id') != comment_id]
        
        if len(task_data['comments']) == original_count:
            print(f"Error: Comment with ID {comment_id} not found in task '{task_id}'", file=sys.stderr)
            return False
        
        if self._save_task(task_data):
            print(f"Comment {comment_id} removed from task '{task_id}'")
            return True
        else:
            print(f"Error: Failed to remove comment from task '{task_id}'", file=sys.stderr)
            return False

    def task_comment_list(self, task_id: str) -> Optional[List[Dict]]:
        """List all comments for a task."""
        task_data = self._load_task(task_id)
        if not task_data:
            print(f"Error: Task '{task_id}' not found", file=sys.stderr)
            return None
        
        return task_data.get('comments', [])


def format_timestamp(timestamp: float) -> str:
    """Format timestamp for display."""
    import datetime
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def launch_tui(tm: "TaskManager") -> None:
    """Launch the Textual TUI for the task manager."""
    if TYPE_CHECKING:  # pragma: no cover - type hints only
        from textual.app import App, ComposeResult  # type: ignore
        from textual.widgets import Header, Footer, Button, Static, Input, DataTable  # type: ignore
        from textual.containers import Vertical  # type: ignore

    try:
        from textual.app import App, ComposeResult  # type: ignore
        from textual.widgets import Header, Footer, Button, Static, Input, DataTable  # type: ignore
        from textual.containers import Vertical  # type: ignore
    except Exception:  # pragma: no cover - optional dependency
        print(
            "Textual is required for the UI. Install with 'pip install textual'",
            file=sys.stderr,
        )
        return

    class TMApp(App):
        TITLE = "Task Manager"
        BINDINGS = [("q", "quit", "Quit")]

        def __init__(self, manager: "TaskManager") -> None:
            super().__init__()
            self.manager = manager
            self.body: Vertical | None = None

        def compose(self) -> ComposeResult:
            yield Header(show_clock=True)
            yield Footer()
            self.body = Vertical()
            yield self.body
            self.show_main()

        def show_main(self) -> None:
            assert self.body
            self.body.clear()
            self.body.mount(Static("Task Manager", classes="title"))
            self.body.mount(Button("Queues", id="queues"))
            self.body.mount(Button("Tasks", id="tasks"))
            self.body.mount(Button("Quit", id="quit"))

        def show_queues(self) -> None:
            assert self.body
            self.body.clear()
            table = DataTable()
            table.add_columns("Name", "Title", "Description")
            for q in self.manager.queue_list():
                table.add_row(q["name"], q["title"], q["description"])
            self.body.mount(table)
            self.body.mount(Button("Add Queue", id="queue_add"))
            self.body.mount(Button("Back", id="main"))

        def show_tasks(self) -> None:
            assert self.body
            self.body.clear()
            table = DataTable()
            table.add_columns("ID", "Title", "Status")
            for t in self.manager.task_list():
                table.add_row(t["id"], t["title"], t["status"])
            self.body.mount(table)
            self.body.mount(Button("Back", id="main"))

        def on_button_pressed(self, event: Button.Pressed) -> None:  # pragma: no cover - UI callbacks
            button_id = event.button.id
            if button_id == "quit":
                self.exit()
            elif button_id == "queues":
                self.show_queues()
            elif button_id == "tasks":
                self.show_tasks()
            elif button_id == "main":
                self.show_main()
            elif button_id == "queue_add":
                assert self.body
                self.body.clear()
                name_in = Input(placeholder="Queue name", id="q_name")
                title_in = Input(placeholder="Queue title", id="q_title")
                desc_in = Input(placeholder="Description", id="q_desc")
                self.body.mount(name_in)
                self.body.mount(title_in)
                self.body.mount(desc_in)
                self.body.mount(Button("Create", id="create_queue"))
                self.body.mount(Button("Back", id="queues"))
            elif button_id == "create_queue":
                name = self.query_one("#q_name", Input).value
                title = self.query_one("#q_title", Input).value
                desc = self.query_one("#q_desc", Input).value
                self.manager.queue_add(name, title, desc)
                self.show_queues()

    TMApp(tm).run()


def main():
    parser = argparse.ArgumentParser(description="Task Manager CLI")
    parser.add_argument("--tasks-root", default=".tasks", 
                       help="Root directory for tasks storage (default: .tasks)")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # UI command
    subparsers.add_parser("ui", help="Launch interactive Textual UI")
    
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
    
    # task comment remove
    task_comment_remove_parser = task_comment_subparsers.add_parser("remove", help="Remove a comment from task")
    task_comment_remove_parser.add_argument("--id", required=True, help="Task ID")
    task_comment_remove_parser.add_argument("--comment-id", type=int, required=True, help="Comment ID")
    
    # task comment list
    task_comment_list_parser = task_comment_subparsers.add_parser("list", help="List task comments")
    task_comment_list_parser.add_argument("--id", required=True, help="Task ID")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    tm = TaskManager(args.tasks_root)
    
    if args.command == "queue":
        if args.queue_action == "list":
            queues = tm.queue_list()
            if not queues:
                print("No queues found")
            else:
                print(f"{'Name':<20} {'Title':<30} {'Description'}")
                print("-" * 80)
                for queue in queues:
                    print(f"{queue['name']:<20} {queue['title']:<30} {queue['description']}")
        
        elif args.queue_action == "add":
            success = tm.queue_add(args.name, args.title, args.description)
            return 0 if success else 1
        
        else:
            queue_parser.print_help()
            return 1
    
    elif args.command == "task":
        if args.task_action == "list":
            tasks = tm.task_list(args.status, args.queue)
            if not tasks:
                print("No tasks found")
            else:
                print(f"{'ID':<15} {'Title':<30} {'Status':<12} {'Queue':<15} {'Created'}")
                print("-" * 90)
                for task in tasks:
                    queue_name = task['id'].rsplit('-', 1)[0]
                    created = format_timestamp(task.get('created_at', 0))
                    print(f"{task['id']:<15} {task['title']:<30} {task['status']:<12} {queue_name:<15} {created}")
        
        elif args.task_action == "add":
            task_id = tm.task_add(args.title, args.description, args.queue)
            return 0 if task_id else 1
        
        elif args.task_action == "show":
            task_data = tm.task_show(args.id)
            if task_data:
                print(f"ID: {task_data['id']}")
                print(f"Title: {task_data['title']}")
                print(f"Description: {task_data['description']}")
                print(f"Status: {task_data['status']}")
                print(f"Created: {format_timestamp(task_data.get('created_at', 0))}")
                print(f"Updated: {format_timestamp(task_data.get('updated_at', 0))}")
                
                comments = task_data.get('comments', [])
                if comments:
                    print(f"\nComments ({len(comments)}):")
                    for comment in comments:
                        created = format_timestamp(comment.get('created_at', 0))
                        print(f"  [{comment['id']}] {created}: {comment['text']}")
                else:
                    print("\nNo comments")
                return 0
            else:
                return 1
        
        elif args.task_action == "update":
            success = tm.task_update(args.id, args.field, args.value)
            return 0 if success else 1
        
        elif args.task_action == "start":
            success = tm.task_start(args.id)
            return 0 if success else 1
        
        elif args.task_action == "done":
            success = tm.task_done(args.id)
            return 0 if success else 1
        
        elif args.task_action == "comment":
            if args.comment_action == "add":
                success = tm.task_comment_add(args.id, args.comment)
                return 0 if success else 1
            
            elif args.comment_action == "remove":
                success = tm.task_comment_remove(args.id, getattr(args, 'comment_id'))
                return 0 if success else 1
            
            elif args.comment_action == "list":
                comments = tm.task_comment_list(args.id)
                if comments is not None:
                    if not comments:
                        print("No comments found")
                    else:
                        print(f"Comments for task {args.id}:")
                        for comment in comments:
                            created = format_timestamp(comment.get('created_at', 0))
                            print(f"  [{comment['id']}] {created}: {comment['text']}")
                    return 0
                else:
                    return 1
            
            else:
                task_comment_parser.print_help()
                return 1
        
        else:
            task_parser.print_help()
            return 1
    
    elif args.command == "ui":
        launch_tui(tm)
        return 0
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 