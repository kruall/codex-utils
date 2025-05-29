"""
Tests for internal TaskManager class functionality.
"""

import json
import tempfile
import unittest
from pathlib import Path
import sys
import os

# Add the parent directory to the path to import task_manager
sys.path.insert(0, str(Path(__file__).parent.parent))
from task_manager import (
    TaskManager,
    QueueExistsError,
    QueueNotFoundError,
    TaskNotFoundError,
    InvalidFieldError,
    CommentNotFoundError,
    LinkNotFoundError,
    StorageError,
)


class TestTaskManagerInternal(unittest.TestCase):
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.tasks_root = Path(self.test_dir) / "test_tasks"
        self.tm = TaskManager(str(self.tasks_root))

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)

    def test_task_manager_initialization(self):
        """Test TaskManager initialization."""
        # Test that tasks_root directory is created
        self.assertTrue(self.tasks_root.exists())
        self.assertTrue(self.tasks_root.is_dir())

    def test_queue_list_empty_internal(self):
        """Test queue_list method when no queues exist."""
        queues = self.tm.queue_list()
        self.assertEqual(queues, [])

    def test_queue_add_internal(self):
        """Test queue_add method directly."""
        self.tm.queue_add("test-queue", "Test Queue", "A test queue")
        
        # Verify directory structure
        queue_dir = self.tasks_root / "test-queue"
        self.assertTrue(queue_dir.exists())
        self.assertTrue(queue_dir.is_dir())
        
        # Verify meta file
        meta_file = queue_dir / "meta.json"
        self.assertTrue(meta_file.exists())
        
        with open(meta_file, 'r') as f:
            meta = json.load(f)
        
        self.assertEqual(meta['title'], "Test Queue")
        self.assertEqual(meta['description'], "A test queue")

    def test_queue_add_duplicate_internal(self):
        """Test queue_add method with duplicate name."""
        # Create first queue
        self.tm.queue_add("duplicate", "First", "First description")

        # Try to create duplicate
        with self.assertRaises(QueueExistsError):
            self.tm.queue_add("duplicate", "Second", "Second description")
        
        # Verify original queue is unchanged
        meta_file = self.tasks_root / "duplicate" / "meta.json"
        with open(meta_file, 'r') as f:
            meta = json.load(f)
        
        self.assertEqual(meta['title'], "First")
        self.assertEqual(meta['description'], "First description")

    def test_queue_list_with_queues_internal(self):
        """Test queue_list method with existing queues."""
        # Create multiple queues
        queues_data = [
            ("queue1", "First Queue", "First description"),
            ("queue2", "Second Queue", "Second description"),
            ("queue3", "Third Queue", "Third description")
        ]
        
        for name, title, description in queues_data:
            self.tm.queue_add(name, title, description)
        
        # Get queue list
        queues = self.tm.queue_list()
        
        # Should have 3 queues
        self.assertEqual(len(queues), 3)
        
        # Convert to dict for easier checking
        queue_dict = {q['name']: q for q in queues}
        
        for name, title, description in queues_data:
            self.assertIn(name, queue_dict)
            self.assertEqual(queue_dict[name]['title'], title)
            self.assertEqual(queue_dict[name]['description'], description)

    def test_queue_list_with_corrupted_meta(self):
        """Test queue_list method with corrupted meta.json files."""
        # Create a queue directory with corrupted meta.json
        queue_dir = self.tasks_root / "corrupted-queue"
        queue_dir.mkdir(parents=True)
        
        meta_file = queue_dir / "meta.json"
        with open(meta_file, 'w') as f:
            f.write("invalid json content")
        
        # Create a valid queue
        self.tm.queue_add("valid-queue", "Valid Queue", "Valid description")
        
        # Get queue list - should only return valid queue
        queues = self.tm.queue_list()
        self.assertEqual(len(queues), 1)
        self.assertEqual(queues[0]['name'], "valid-queue")

    def test_queue_list_with_missing_meta(self):
        """Test queue_list method with directories missing meta.json."""
        # Create a queue directory without meta.json
        queue_dir = self.tasks_root / "no-meta-queue"
        queue_dir.mkdir(parents=True)
        
        # Create a valid queue
        self.tm.queue_add("valid-queue", "Valid Queue", "Valid description")
        
        # Get queue list - should only return valid queue
        queues = self.tm.queue_list()
        self.assertEqual(len(queues), 1)
        self.assertEqual(queues[0]['name'], "valid-queue")

    def test_queue_list_with_files_in_tasks_root(self):
        """Test queue_list method ignores files in tasks root."""
        # Create a file in tasks root
        file_path = self.tasks_root / "not-a-queue.txt"
        with open(file_path, 'w') as f:
            f.write("This is not a queue")
        
        # Create a valid queue
        self.tm.queue_add("valid-queue", "Valid Queue", "Valid description")
        
        # Get queue list - should only return valid queue
        queues = self.tm.queue_list()
        self.assertEqual(len(queues), 1)
        self.assertEqual(queues[0]['name'], "valid-queue")

    def test_queue_add_with_unicode(self):
        """Test queue_add method with unicode characters."""
        self.tm.queue_add(
            "unicode-queue",
            "Тест Queue with émojis 🚀",
            "Description with unicode: ñáéíóú and 中文",
        )
        
        # Verify unicode was stored correctly
        meta_file = self.tasks_root / "unicode-queue" / "meta.json"
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        self.assertEqual(meta['title'], "Тест Queue with émojis 🚀")
        self.assertEqual(meta['description'], "Description with unicode: ñáéíóú and 中文")

    def test_queue_add_io_error_simulation(self):
        """Test queue_add method behavior when IO operations fail."""
        # Create a read-only tasks root to simulate permission error
        readonly_root = Path(self.test_dir) / "readonly"
        readonly_root.mkdir()
        
        # Create TaskManager first (this will create the directory structure)
        tm_readonly = TaskManager(str(readonly_root))
        
        # Now make it read-only to simulate permission error
        readonly_root.chmod(0o444)  # Read-only
        
        try:
            # This should fail due to permission error
            with self.assertRaises(StorageError):
                tm_readonly.queue_add("test-queue", "Test", "Test description")
        finally:
            # Restore permissions for cleanup
            readonly_root.chmod(0o755)

    def test_task_manager_with_relative_path(self):
        """Test TaskManager with relative path."""
        # Change to test directory
        original_cwd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            tm = TaskManager("relative_tasks")
            
            tm.queue_add("rel-queue", "Relative Queue", "Relative path test")
            
            # Verify queue was created in relative path
            rel_path = Path(self.test_dir) / "relative_tasks" / "rel-queue"
            self.assertTrue(rel_path.exists())

        finally:
            os.chdir(original_cwd)

    def test_task_add_and_show_internal(self):
        """Test adding a task and showing its details."""
        self.tm.queue_add("q", "Queue", "desc")
        task_id = self.tm.task_add("Task", "Desc", "q")
        self.assertEqual(task_id, "q-1")

        task = self.tm.task_show(task_id)
        self.assertIsNotNone(task)
        self.assertEqual(task["title"], "Task")
        self.assertEqual(task["description"], "Desc")
        self.assertEqual(task["status"], "todo")

    def test_task_update_and_status_changes(self):
        """Test task update, start and done status changes."""
        self.tm.queue_add("q", "Queue", "desc")
        task_id = self.tm.task_add("Task", "Desc", "q")
        self.tm.task_update(task_id, "title", "New Title")
        self.tm.task_start(task_id)
        self.tm.task_done(task_id)

        task = self.tm.task_show(task_id)
        self.assertEqual(task["title"], "New Title")
        self.assertEqual(task["status"], "done")

    def test_task_comments_internal(self):
        """Test adding, listing and removing task comments."""
        self.tm.queue_add("q", "Queue", "desc")
        task_id = self.tm.task_add("Task", "Desc", "q")

        self.tm.task_comment_add(task_id, "c1")
        self.tm.task_comment_add(task_id, "c2")
        comments = self.tm.task_comment_list(task_id)
        self.assertEqual(len(comments), 2)

        self.tm.task_comment_remove(task_id, 1)
        comments = self.tm.task_comment_list(task_id)
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0]["text"], "c2")

    def test_task_comment_edit_internal(self):
        """Test editing task comments."""
        self.tm.queue_add("q", "Queue", "desc")
        task_id = self.tm.task_add("Task", "Desc", "q")

        self.tm.task_comment_add(task_id, "old")
        self.tm.task_comment_edit(task_id, 1, "new")
        comments = self.tm.task_comment_list(task_id)
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0]["text"], "new")
        self.assertIn("updated_at", comments[0])

    def test_queue_delete_internal(self):
        """Test deleting a queue via TaskManager."""
        self.tm.queue_add("del", "Del", "desc")
        self.tm.queue_delete("del")
        self.assertEqual(self.tm.queue_list(), [])

    def test_task_delete_internal(self):
        """Test deleting a task via TaskManager."""
        self.tm.queue_add("q", "Queue", "desc")
        task_id = self.tm.task_add("Task", "Desc", "q")
        self.tm.task_delete(task_id)
        self.assertEqual(self.tm.task_list(), [])

    def test_get_next_task_number_internal(self):
        """Test internal task numbering logic."""
        self.tm.queue_add("q", "Queue", "desc")
        self.assertEqual(self.tm._get_next_task_number("q"), 1)
        self.tm.task_add("A", "B", "q")
        self.assertEqual(self.tm._get_next_task_number("q"), 2)

    def test_queue_add_empty_name_internal(self):
        """Queue name cannot be empty."""
        with self.assertRaises(ValueError):
            self.tm.queue_add("", "T", "D")

    def test_queue_delete_nonexistent_internal(self):
        """Deleting a missing queue raises QueueNotFoundError."""
        with self.assertRaises(QueueNotFoundError):
            self.tm.queue_delete("missing")

    def test_task_add_nonexistent_queue_internal(self):
        """Adding a task to a missing queue raises QueueNotFoundError."""
        with self.assertRaises(QueueNotFoundError):
            self.tm.task_add("T", "D", "missing")

    def test_task_show_nonexistent_internal(self):
        """Showing a non-existent task raises TaskNotFoundError."""
        with self.assertRaises(TaskNotFoundError):
            self.tm.task_show("missing-1")

    def test_task_show_invalid_json_internal(self):
        """Invalid task file content triggers StorageError."""
        self.tm.queue_add("q", "Queue", "desc")
        bad_file = Path(self.tasks_root) / "q" / "q-1.json"
        bad_file.write_text("not json", encoding="utf-8")
        with self.assertRaises(StorageError):
            self.tm.task_show("q-1")

    def test_task_update_invalid_field_internal(self):
        """Invalid field update raises InvalidFieldError."""
        self.tm.queue_add("q", "Queue", "desc")
        task_id = self.tm.task_add("T", "D", "q")
        with self.assertRaises(InvalidFieldError):
            self.tm.task_update(task_id, "bogus", "v")

    def test_task_comment_remove_not_found_internal(self):
        """Removing missing comment raises CommentNotFoundError."""
        self.tm.queue_add("q", "Queue", "desc")
        task_id = self.tm.task_add("T", "D", "q")
        with self.assertRaises(CommentNotFoundError):
            self.tm.task_comment_remove(task_id, 1)

    def test_task_link_remove_not_found_internal(self):
        """Removing absent link raises LinkNotFoundError."""
        self.tm.queue_add("q", "Queue", "desc")
        self.tm.task_add("A", "B", "q")
        self.tm.task_add("C", "D", "q")
        with self.assertRaises(LinkNotFoundError):
            self.tm.task_link_remove("q-1", "q-2")

    def test_task_delete_nonexistent_internal(self):
        """Deleting a missing task raises TaskNotFoundError."""
        with self.assertRaises(TaskNotFoundError):
            self.tm.task_delete("q-99")


if __name__ == '__main__':
    unittest.main() 