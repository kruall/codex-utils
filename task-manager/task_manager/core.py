import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional


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

