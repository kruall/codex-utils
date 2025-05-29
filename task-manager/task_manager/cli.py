import argparse
from .core import TaskManager
from .tui import launch_tui
from .utils import format_timestamp

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

