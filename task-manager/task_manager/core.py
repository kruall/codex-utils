from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Union

from .models import Queue, Task, TaskStatus, Epic, EpicStatus
from .utils import log_error
from .storage import load_json, save_json
from .exceptions import (
    QueueExistsError,
    QueueNotFoundError,
    TaskNotFoundError,
    InvalidFieldError,
    CommentNotFoundError,
    LinkNotFoundError,
    LinkAlreadyExistsError,
    StorageError,
)

logger = logging.getLogger(__name__)


class TaskManager:
    def __init__(self, tasks_root: str = ".tasks", epics_root: str = ".epics"):
        self.tasks_root = Path(tasks_root)
        self.tasks_root.mkdir(exist_ok=True)
        self.epics_root = Path(epics_root)
        self.epics_root.mkdir(exist_ok=True)
        self._queue_list_cache: List[Dict[str, str]] | None = None
        self._task_list_cache: dict[tuple[Optional[str], Optional[str]], List[Dict]] = {}
        self._epic_list_cache: Optional[List[Dict]] = None

    def _invalidate_queue_cache(self) -> None:
        self._queue_list_cache = None

    def _invalidate_task_cache(self) -> None:
        self._task_list_cache.clear()

    def _invalidate_epic_cache(self) -> None:
        self._epic_list_cache = None

    def queue_list(self) -> List[Dict[str, str]]:
        """List all queues."""
        if self._queue_list_cache is not None:
            return self._queue_list_cache

        queues: List[Dict[str, str]] = []
        for queue_dir in self.tasks_root.iterdir():
            if queue_dir.is_dir():
                meta_file = queue_dir / "meta.json"
                if meta_file.exists():
                    meta = load_json(meta_file)
                    if meta is None:
                        continue
                    queue = Queue.from_meta(queue_dir.name, meta)
                    queues.append(queue.to_dict())

        self._queue_list_cache = queues
        return queues

    def queue_add(self, name: str, title: str, description: str) -> None:
        """Add a new queue."""
        if not name or not name.strip():
            raise ValueError("Queue name cannot be empty")
        
        queue_dir = self.tasks_root / name

        # Check write permissions on tasks root by inspecting mode bits
        try:
            import stat
            mode = os.stat(self.tasks_root).st_mode
            write_bits = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
            if not (mode & write_bits):
                raise StorageError(f"Error creating queue '{name}': Permission denied")
        except OSError as e:
            raise StorageError(f"Error creating queue '{name}': {e}")

        try:
            if queue_dir.exists():
                raise QueueExistsError(f"Queue '{name}' already exists")
        except (OSError, PermissionError):
            # If we can't check if it exists due to permissions, try to create anyway
            pass
        
        try:
            queue_dir.mkdir(parents=True)
            meta_file = queue_dir / "meta.json"

            queue_obj = Queue(name=name, title=title, description=description)
            meta_data = {
                "title": queue_obj.title,
                "description": queue_obj.description,
            }

            if not save_json(meta_file, meta_data):
                raise StorageError(f"Error saving metadata for queue '{name}'")

            logger.info(f"Queue '{name}' created successfully")
            self._invalidate_queue_cache()
            self._invalidate_task_cache()

        except (OSError, IOError) as e:
            raise StorageError(f"Error creating queue '{name}': {e}")

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

    def _get_next_epic_number(self) -> int:
        """Get the next available epic number."""
        if not self.epics_root.exists():
            return 1

        max_num = 0
        for epic_file in self.epics_root.glob("epic-*.json"):
            try:
                num_str = epic_file.stem.split("-", 1)[1]
                num = int(num_str)
                max_num = max(max_num, num)
            except (IndexError, ValueError):
                continue
        return max_num + 1

    def task_add(self, title: str, description: str, queue: str) -> str:
        """Add a new task to a queue."""
        queue_dir = self.tasks_root / queue

        if not queue_dir.exists():
            raise QueueNotFoundError(f"Queue '{queue}' does not exist")

        try:
            task_num = self._get_next_task_number(queue)
            task_id = f"{queue}-{task_num}"
            task_file = queue_dir / f"{task_id}.json"

            task_obj = Task(id=task_id, title=title, description=description)

            if not save_json(task_file, task_obj.to_dict()):
                raise StorageError(f"Failed to save task '{task_id}' to file")

            logger.info(f"Task '{task_id}' created successfully")
            self._invalidate_task_cache()
            return task_id

        except (OSError, IOError) as e:
            raise StorageError(f"Error creating task: {e}")

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

    def _find_epic_file(self, epic_id: str) -> Optional[Path]:
        """Find the epic file for a given epic ID."""
        if not epic_id.startswith("epic-"):
            return None

        epic_file = self.epics_root / f"{epic_id}.json"
        if epic_file.exists():
            return epic_file
        return None

    def _load_epic(self, epic_id: str) -> Epic:
        epic_file = self._find_epic_file(epic_id)
        if not epic_file:
            raise TaskNotFoundError(f"Epic '{epic_id}' not found")

        data = load_json(epic_file)
        if data is None:
            raise StorageError(f"Failed to read epic '{epic_id}'")
        return Epic.from_dict(data)

    def _save_epic(self, epic_data: Epic) -> None:
        epic_id = epic_data.id
        epic_file = self._find_epic_file(epic_id)
        if not epic_file:
            raise TaskNotFoundError(f"Epic '{epic_id}' not found")

        epic_data.updated_at = time.time()
        if not save_json(epic_file, epic_data.to_dict()):
            raise StorageError(f"Failed to save epic '{epic_id}'")
        self._invalidate_epic_cache()

    def _get_all_epics(self) -> List[Epic]:
        """Return all epics as objects."""
        epics: list[Epic] = []
        for epic_file in self.epics_root.glob("epic-*.json"):
            data = load_json(epic_file)
            if data is None:
                continue
            try:
                epics.append(Epic.from_dict(data))
            except Exception as e:  # pragma: no cover - shouldn't happen
                log_error(f"Error loading epic '{epic_file}': {e}")
        return epics

    def _get_parent_epics(self, item_id: str) -> List[Epic]:
        """Return epics that reference the given task or epic."""
        parents = []
        for epic in self._get_all_epics():
            if item_id in epic.child_tasks or item_id in epic.child_epics:
                parents.append(epic)
        return parents

    def _can_close_epic(self, epic: Epic) -> bool:
        """Return True if all children of epic are complete."""
        for task_id in epic.child_tasks:
            try:
                task = self._load_task(task_id)
            except TaskNotFoundError:
                return False
            if task.status != TaskStatus.DONE:
                return False

        for child_id in epic.child_epics:
            try:
                child = self._load_epic(child_id)
            except TaskNotFoundError:
                return False
            if child.status != EpicStatus.CLOSED:
                return False

        return True

    def _auto_close_parent_epics(self, item_id: str) -> None:
        """Automatically close parent epics if they are now complete."""
        for parent in self._get_parent_epics(item_id):
            if self._can_close_epic(parent) and parent.status != EpicStatus.CLOSED:
                parent.status = EpicStatus.CLOSED
                self._save_epic(parent)
                if parent.parent_epic:
                    self._auto_close_parent_epics(parent.id)

    def task_parent_epics(self, task_id: str) -> List[Dict]:
        """Return epics containing the given task."""
        epics = [e.to_dict() for e in self._get_parent_epics(task_id)]
        return epics

    def invalid_closed_epics(self) -> List[str]:
        """Return IDs of epics marked closed with incomplete children."""
        invalid = []
        for epic in self._get_all_epics():
            if epic.status == EpicStatus.CLOSED and not self._can_close_epic(epic):
                invalid.append(epic.id)
        return invalid

    def repair_links(self) -> None:
        """Ensure all task links are bidirectional."""
        for task in self.task_list():
            task_obj = self._load_task(task["id"])
            changed = False
            for link_type, targets in list(task_obj.links.items()):
                unique_targets = list(dict.fromkeys(targets))
                if unique_targets != targets:
                    task_obj.links[link_type] = unique_targets
                    changed = True
                for target_id in unique_targets:
                    try:
                        target_obj = self._load_task(target_id)
                    except TaskNotFoundError:
                        continue
                    reciprocal = target_obj.links.setdefault(link_type, [])
                    if task_obj.id not in reciprocal:
                        reciprocal.append(task_obj.id)
                        self._save_task(target_obj)
            if changed:
                self._save_task(task_obj)

    def _load_task(self, task_id: str) -> Task:
        """Load task data from file."""
        task_file = self._find_task_file(task_id)
        if not task_file:
            raise TaskNotFoundError(f"Task '{task_id}' not found")

        data = load_json(task_file)
        if data is None:
            raise StorageError(f"Failed to read task '{task_id}'")
        return Task.from_dict(data)

    def _save_task(self, task_data: Task) -> None:
        """Save task data to file."""
        task_id = task_data.id
        task_file = self._find_task_file(task_id)
        if not task_file:
            raise TaskNotFoundError(f"Task '{task_id}' not found")

        task_data.updated_at = time.time()
        if not save_json(task_file, task_data.to_dict()):
            raise StorageError(f"Failed to save task '{task_id}'")
        self._invalidate_task_cache()

    def task_list(self, status: Optional[str] = None, queue: Optional[str] = None) -> List[Dict]:
        """List tasks with optional filtering."""
        cache_key = (status, queue)
        if cache_key in self._task_list_cache:
            return self._task_list_cache[cache_key]

        tasks: List[Dict] = []
        
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
                    data = load_json(task_file)
                    if data is None:
                        continue
                    task_obj = Task.from_dict(data)

                    # Filter by status if specified
                    if status and task_obj.status.value != status:
                        continue

                    tasks.append(task_obj.to_dict())
                except (FileNotFoundError, PermissionError, json.JSONDecodeError) as e:
                    log_error(f"Error processing task file '{task_file}': {e}")
                    continue
        
        # Sort by creation time
        tasks.sort(key=lambda t: t.get("created_at", 0))
        self._task_list_cache[cache_key] = tasks
        return tasks

    def task_show(self, task_id: str) -> Dict:
        """Show detailed information about a task."""
        task_data = self._load_task(task_id)
        return task_data.to_dict()

    def task_update(self, task_id: str, field: str, value: str) -> None:
        """Update a specific field of a task."""
        task_data = self._load_task(task_id)
        
        # Validate field
        allowed_fields = ['title', 'description', 'status']
        if field not in allowed_fields:
            raise InvalidFieldError(
                f"Field '{field}' is not allowed. Allowed fields: {', '.join(allowed_fields)}"
            )
        
        # Handle status field specially to convert string to enum
        actual_value: Union[str, TaskStatus] = value
        if field == 'status':
            try:
                actual_value = TaskStatus(value)
            except ValueError:
                valid_statuses = [status.value for status in TaskStatus]
                raise InvalidFieldError(
                    f"Invalid status '{value}'. Valid statuses: {', '.join(valid_statuses)}"
                )
        
        setattr(task_data, field, actual_value)

        self._save_task(task_data)
        logger.info(f"Task '{task_id}' updated successfully")

        if field == 'status' and actual_value == TaskStatus.DONE:
            self._auto_close_parent_epics(task_id)

    def task_start(self, task_id: str) -> None:
        """Start a task (set status to 'in_progress' and record time)."""
        task_data = self._load_task(task_id)

        task_data.status = TaskStatus.IN_PROGRESS
        if task_data.started_at is None:
            task_data.started_at = time.time()

        self._save_task(task_data)
        logger.info(f"Task '{task_id}' updated successfully")

    def task_done(self, task_id: str) -> None:
        """Mark a task as done (set status to 'done' and record time)."""
        task_data = self._load_task(task_id)

        task_data.status = TaskStatus.DONE
        if task_data.closed_at is None:
            task_data.closed_at = time.time()

        self._save_task(task_data)
        logger.info(f"Task '{task_id}' updated successfully")
        self._auto_close_parent_epics(task_id)

    def task_comment_add(self, task_id: str, comment: str) -> int:
        """Add a comment to a task."""
        task_data = self._load_task(task_id)
        
        # Generate comment ID
        existing_ids = [c.get("id", 0) for c in task_data.comments]
        comment_id = max(existing_ids, default=0) + 1
        
        comment_data = {
            "id": comment_id,
            "text": comment,
            "created_at": time.time(),
        }

        task_data.comments.append(comment_data)
        
        self._save_task(task_data)
        logger.info(f"Comment added to task '{task_id}' with ID {comment_id}")
        return comment_id

    def task_comment_edit(self, task_id: str, comment_id: int, text: str) -> None:
        """Edit a comment on a task."""
        task_data = self._load_task(task_id)

        for comment in task_data.comments:
            if comment.get("id") == comment_id:
                comment["text"] = text
                comment["updated_at"] = time.time()
                break
        else:
            raise CommentNotFoundError(
                f"Comment with ID {comment_id} not found in task '{task_id}'"
            )

        self._save_task(task_data)
        logger.info(f"Comment {comment_id} edited in task '{task_id}'")

    def task_comment_remove(self, task_id: str, comment_id: int) -> None:
        """Remove a comment from a task."""
        task_data = self._load_task(task_id)

        comments = task_data.comments
        original_count = len(comments)
        
        # Remove comment with matching ID
        task_data.comments = [c for c in comments if c.get("id") != comment_id]
        
        if len(task_data.comments) == original_count:
            raise CommentNotFoundError(
                f"Comment with ID {comment_id} not found in task '{task_id}'"
            )
        
        self._save_task(task_data)
        logger.info(f"Comment {comment_id} removed from task '{task_id}'")

    def task_comment_list(self, task_id: str) -> List[Dict]:
        """List all comments for a task."""
        task_data = self._load_task(task_id)
        return task_data.comments

    def task_link_add(
        self, task_id: str, target_id: str, link_type: str = "related"
    ) -> None:
        """Add a link between two tasks."""
        task_data = self._load_task(task_id)
        target_data = self._load_task(target_id)

        links = task_data.links.setdefault(link_type, [])
        target_links = target_data.links.setdefault(link_type, [])

        if target_id in links and task_id in target_links:
            raise LinkAlreadyExistsError(
                f"Link between {task_id} and {target_id} already exists"
            )

        if target_id not in links:
            links.append(target_id)

        if task_id not in target_links:
            target_links.append(task_id)

        self._save_task(task_data)
        self._save_task(target_data)
        logger.info(
            f"Link added between {task_id} and {target_id} (type: {link_type})"
        )

    def task_link_remove(
        self, task_id: str, target_id: str, link_type: str = "related"
    ) -> None:
        """Remove a link between two tasks."""
        task_data = self._load_task(task_id)
        target_data = self._load_task(target_id)

        removed = False

        if target_id in task_data.links.get(link_type, []):
            task_data.links[link_type].remove(target_id)
            if not task_data.links[link_type]:
                del task_data.links[link_type]
            removed = True

        if task_id in target_data.links.get(link_type, []):
            target_data.links[link_type].remove(task_id)
            if not target_data.links[link_type]:
                del target_data.links[link_type]
            removed = True

        if not removed:
            raise LinkNotFoundError(
                f"Link between {task_id} and {target_id} not found"
            )

        self._save_task(task_data)
        self._save_task(target_data)
        logger.info(
            f"Link removed between {task_id} and {target_id} (type: {link_type})"
        )

    def task_link_list(self, task_id: str) -> Dict[str, List[str]]:
        """List links for a task."""
        task_data = self._load_task(task_id)
        return task_data.links

    def queue_delete(self, name: str) -> None:
        """Delete an entire queue and all its tasks."""
        queue_dir = self.tasks_root / name
        if not queue_dir.exists() or not queue_dir.is_dir():
            raise QueueNotFoundError(f"Queue '{name}' not found")

        try:
            import shutil

            shutil.rmtree(queue_dir)
            logger.info(f"Queue '{name}' deleted successfully")
            self._invalidate_queue_cache()
            self._invalidate_task_cache()
        except (OSError, IOError) as e:
            raise StorageError(f"Error deleting queue '{name}': {e}")

    def task_delete(self, task_id: str) -> None:
        """Delete a task file from its queue."""
        task_file = self._find_task_file(task_id)
        if not task_file or not task_file.exists():
            raise TaskNotFoundError(f"Task '{task_id}' not found")

        try:
            task_file.unlink()
            logger.info(f"Task '{task_id}' deleted successfully")
            self._invalidate_task_cache()
        except (OSError, IOError) as e:
            raise StorageError(f"Error deleting task '{task_id}': {e}")

    # ------------------------------------------------------------------
    # Epic persistence methods
    # ------------------------------------------------------------------

    def epic_add(self, title: str, description: str) -> str:
        """Create a new epic."""
        try:
            epic_num = self._get_next_epic_number()
            epic_id = f"epic-{epic_num}"
            epic_file = self.epics_root / f"{epic_id}.json"

            epic_obj = Epic(id=epic_id, title=title, description=description)

            if not save_json(epic_file, epic_obj.to_dict()):
                raise StorageError(f"Failed to save epic '{epic_id}' to file")

            logger.info(f"Epic '{epic_id}' created successfully")
            self._invalidate_epic_cache()
            return epic_id

        except (OSError, IOError) as e:
            raise StorageError(f"Error creating epic: {e}")

    def epic_list(self) -> List[Dict]:
        """List all epics."""
        if self._epic_list_cache is not None:
            return self._epic_list_cache

        epics: List[Dict] = []
        for epic_file in self.epics_root.glob("epic-*.json"):
            try:
                data = load_json(epic_file)
                if data is None:
                    continue
                epics.append(Epic.from_dict(data).to_dict())
            except (FileNotFoundError, PermissionError, json.JSONDecodeError) as e:
                log_error(f"Error processing epic file '{epic_file}': {e}")
                continue

        epics.sort(key=lambda e: e.get("created_at", 0))
        self._epic_list_cache = epics
        return epics

    def epic_show(self, epic_id: str) -> Dict:
        """Show details of an epic."""
        epic_data = self._load_epic(epic_id)
        return epic_data.to_dict()

    def epic_update(self, epic_id: str, field: str, value: str) -> None:
        """Update an epic field."""
        epic_data = self._load_epic(epic_id)

        allowed_fields = ["title", "description", "status"]
        if field not in allowed_fields:
            raise InvalidFieldError(
                f"Field '{field}' is not allowed. Allowed fields: {', '.join(allowed_fields)}"
            )

        actual_value: Union[str, EpicStatus] = value
        if field == "status":
            try:
                actual_value = EpicStatus(value)
            except ValueError:
                valid = [s.value for s in EpicStatus]
                raise InvalidFieldError(
                    f"Invalid status '{value}'. Valid statuses: {', '.join(valid)}"
                )
            if actual_value == EpicStatus.CLOSED and not self._can_close_epic(epic_data):
                raise InvalidFieldError(
                    f"Cannot close epic '{epic_id}' because child tasks or epics are incomplete"
                )

        setattr(epic_data, field, actual_value)
        self._save_epic(epic_data)
        logger.info(f"Epic '{epic_id}' updated successfully")

        if field == "status" and actual_value == EpicStatus.CLOSED:
            if epic_data.parent_epic:
                self._auto_close_parent_epics(epic_id)

    def epic_add_task(self, epic_id: str, task_id: str) -> None:
        """Add a task to an epic."""
        epic_data = self._load_epic(epic_id)
        if task_id not in epic_data.child_tasks:
            epic_data.child_tasks.append(task_id)
        self._save_epic(epic_data)

    def epic_add_epic(self, epic_id: str, child_epic_id: str) -> None:
        """Add a child epic to an epic."""
        parent_epic = self._load_epic(epic_id)
        child_epic = self._load_epic(child_epic_id)

        if child_epic_id not in parent_epic.child_epics:
            parent_epic.child_epics.append(child_epic_id)
        child_epic.parent_epic = epic_id

        self._save_epic(parent_epic)
        self._save_epic(child_epic)

    def epic_delete(self, epic_id: str) -> None:
        """Delete an epic."""
        epic_file = self._find_epic_file(epic_id)
        if not epic_file or not epic_file.exists():
            raise TaskNotFoundError(f"Epic '{epic_id}' not found")

        try:
            epic_file.unlink()
            logger.info(f"Epic '{epic_id}' deleted successfully")
            self._invalidate_epic_cache()
        except (OSError, IOError) as e:
            raise StorageError(f"Error deleting epic '{epic_id}': {e}")

    def epic_remove_task(self, epic_id: str, task_id: str) -> None:
        """Remove a task from an epic."""
        epic_data = self._load_epic(epic_id)
        try:
            epic_data.child_tasks.remove(task_id)
        except ValueError:
            raise TaskNotFoundError(
                f"Task '{task_id}' not found in epic '{epic_id}'"
            )
        self._save_epic(epic_data)

    def epic_remove_epic(self, epic_id: str, child_epic_id: str) -> None:
        """Remove a child epic from an epic."""
        parent_epic = self._load_epic(epic_id)
        child_epic = self._load_epic(child_epic_id)

        try:
            parent_epic.child_epics.remove(child_epic_id)
        except ValueError:
            raise TaskNotFoundError(
                f"Epic '{child_epic_id}' not found in epic '{epic_id}'"
            )

        if child_epic.parent_epic == epic_id:
            child_epic.parent_epic = None

        self._save_epic(parent_epic)
        self._save_epic(child_epic)

    def epic_done(self, epic_id: str) -> None:
        """Mark an epic as closed if all children are complete."""
        epic_data = self._load_epic(epic_id)

        if not self._can_close_epic(epic_data):
            raise InvalidFieldError(
                f"Cannot close epic '{epic_id}' because child tasks or epics are incomplete"
            )

        epic_data.status = EpicStatus.CLOSED
        self._save_epic(epic_data)
        logger.info(f"Epic '{epic_id}' updated successfully")

        if epic_data.parent_epic:
            self._auto_close_parent_epics(epic_id)

