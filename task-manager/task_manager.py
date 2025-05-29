#!/usr/bin/env python3
"""
Task Manager CLI tool for managing queues and tasks.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List


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


def main():
    parser = argparse.ArgumentParser(description="Task Manager CLI")
    parser.add_argument("--tasks-root", default=".tasks", 
                       help="Root directory for tasks storage (default: .tasks)")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
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
    
    # Task commands (placeholder for future implementation)
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
    
    # task update
    task_update_parser = task_subparsers.add_parser("update", help="Update a task")
    task_update_parser.add_argument("--id", required=True, help="Task ID")
    task_update_parser.add_argument("--field", help="Field to update")
    
    # task start
    task_start_parser = task_subparsers.add_parser("start", help="Start a task")
    task_start_parser.add_argument("--id", required=True, help="Task ID")
    
    # task done
    task_done_parser = task_subparsers.add_parser("done", help="Mark task as done")
    task_done_parser.add_argument("--id", required=True, help="Task ID")
    
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
        print("Task management not implemented yet", file=sys.stderr)
        return 1
    
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 