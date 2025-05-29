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
from task_manager import TaskManager


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
        success = self.tm.queue_add("test-queue", "Test Queue", "A test queue")
        self.assertTrue(success)
        
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
        success1 = self.tm.queue_add("duplicate", "First", "First description")
        self.assertTrue(success1)
        
        # Try to create duplicate
        success2 = self.tm.queue_add("duplicate", "Second", "Second description")
        self.assertFalse(success2)
        
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
            success = self.tm.queue_add(name, title, description)
            self.assertTrue(success)
        
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
        success = self.tm.queue_add("valid-queue", "Valid Queue", "Valid description")
        self.assertTrue(success)
        
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
        success = self.tm.queue_add("valid-queue", "Valid Queue", "Valid description")
        self.assertTrue(success)
        
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
        success = self.tm.queue_add("valid-queue", "Valid Queue", "Valid description")
        self.assertTrue(success)
        
        # Get queue list - should only return valid queue
        queues = self.tm.queue_list()
        self.assertEqual(len(queues), 1)
        self.assertEqual(queues[0]['name'], "valid-queue")

    def test_queue_add_with_unicode(self):
        """Test queue_add method with unicode characters."""
        success = self.tm.queue_add(
            "unicode-queue",
            "Тест Queue with émojis 🚀",
            "Description with unicode: ñáéíóú and 中文"
        )
        self.assertTrue(success)
        
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
            success = tm_readonly.queue_add("test-queue", "Test", "Test description")
            self.assertFalse(success)
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
            
            success = tm.queue_add("rel-queue", "Relative Queue", "Relative path test")
            self.assertTrue(success)
            
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
        self.assertTrue(self.tm.task_update(task_id, "title", "New Title"))
        self.assertTrue(self.tm.task_start(task_id))
        self.assertTrue(self.tm.task_done(task_id))

        task = self.tm.task_show(task_id)
        self.assertEqual(task["title"], "New Title")
        self.assertEqual(task["status"], "done")

    def test_task_comments_internal(self):
        """Test adding, listing and removing task comments."""
        self.tm.queue_add("q", "Queue", "desc")
        task_id = self.tm.task_add("Task", "Desc", "q")

        self.assertTrue(self.tm.task_comment_add(task_id, "c1"))
        self.assertTrue(self.tm.task_comment_add(task_id, "c2"))
        comments = self.tm.task_comment_list(task_id)
        self.assertEqual(len(comments), 2)

        self.assertTrue(self.tm.task_comment_remove(task_id, 1))
        comments = self.tm.task_comment_list(task_id)
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0]["text"], "c2")

    def test_get_next_task_number_internal(self):
        """Test internal task numbering logic."""
        self.tm.queue_add("q", "Queue", "desc")
        self.assertEqual(self.tm._get_next_task_number("q"), 1)
        self.tm.task_add("A", "B", "q")
        self.assertEqual(self.tm._get_next_task_number("q"), 2)


if __name__ == '__main__':
    unittest.main() 