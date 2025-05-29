"""
Tests for queue management functionality.
"""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestQueueManagement(unittest.TestCase):
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.tasks_root = Path(self.test_dir) / "test_tasks"
        self.task_manager_path = Path(__file__).parent.parent.parent / "task_manager.py"

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)

    def run_task_manager(self, args):
        """Helper method to run task manager with given arguments."""
        cmd = ["python", str(self.task_manager_path), "--tasks-root", str(self.tasks_root)] + args
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result

    def test_queue_list_empty(self):
        """Test listing queues when no queues exist."""
        result = self.run_task_manager(["queue", "list"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("No queues found", result.stdout)

    def test_queue_add_success(self):
        """Test successfully adding a new queue."""
        result = self.run_task_manager([
            "queue", "add", 
            "--name", "test-queue",
            "--title", "Test Queue",
            "--description", "A test queue for testing"
        ])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Queue 'test-queue' created successfully", result.stdout)
        
        # Verify queue directory and meta file were created
        queue_dir = self.tasks_root / "test-queue"
        self.assertTrue(queue_dir.exists())
        self.assertTrue(queue_dir.is_dir())
        
        meta_file = queue_dir / "meta.json"
        self.assertTrue(meta_file.exists())
        
        # Verify meta file content
        with open(meta_file, 'r') as f:
            meta = json.load(f)
        
        self.assertEqual(meta['title'], "Test Queue")
        self.assertEqual(meta['description'], "A test queue for testing")

    def test_queue_add_duplicate(self):
        """Test adding a queue with a name that already exists."""
        # First, create a queue
        result1 = self.run_task_manager([
            "queue", "add",
            "--name", "duplicate-queue",
            "--title", "First Queue",
            "--description", "First description"
        ])
        self.assertEqual(result1.returncode, 0)
        
        # Try to create another queue with the same name
        result2 = self.run_task_manager([
            "queue", "add",
            "--name", "duplicate-queue",
            "--title", "Second Queue",
            "--description", "Second description"
        ])
        self.assertEqual(result2.returncode, 1)
        self.assertIn("Error: Queue 'duplicate-queue' already exists", result2.stderr)

    def test_queue_list_with_queues(self):
        """Test listing queues when queues exist."""
        # Create multiple queues
        queues_data = [
            ("queue1", "First Queue", "Description for first queue"),
            ("queue2", "Second Queue", "Description for second queue"),
            ("queue3", "Third Queue", "Description for third queue")
        ]
        
        for name, title, description in queues_data:
            result = self.run_task_manager([
                "queue", "add",
                "--name", name,
                "--title", title,
                "--description", description
            ])
            self.assertEqual(result.returncode, 0)
        
        # List queues
        result = self.run_task_manager(["queue", "list"])
        self.assertEqual(result.returncode, 0)
        
        # Check that all queues are listed
        for name, title, description in queues_data:
            self.assertIn(name, result.stdout)
            self.assertIn(title, result.stdout)
            self.assertIn(description, result.stdout)

    def test_queue_add_with_special_characters(self):
        """Test adding a queue with special characters in title and description."""
        result = self.run_task_manager([
            "queue", "add",
            "--name", "special-queue",
            "--title", "Queue with 'quotes' and \"double quotes\"",
            "--description", "Description with special chars: !@#$%^&*()"
        ])
        self.assertEqual(result.returncode, 0)
        
        # Verify the content was stored correctly
        meta_file = self.tasks_root / "special-queue" / "meta.json"
        with open(meta_file, 'r') as f:
            meta = json.load(f)
        
        self.assertEqual(meta['title'], "Queue with 'quotes' and \"double quotes\"")
        self.assertEqual(meta['description'], "Description with special chars: !@#$%^&*()")

    def test_queue_add_missing_arguments(self):
        """Test queue add command with missing required arguments."""
        # Missing name
        result = self.run_task_manager([
            "queue", "add",
            "--title", "Test Queue",
            "--description", "Test description"
        ])
        self.assertNotEqual(result.returncode, 0)
        
        # Missing title
        result = self.run_task_manager([
            "queue", "add",
            "--name", "test-queue",
            "--description", "Test description"
        ])
        self.assertNotEqual(result.returncode, 0)
        
        # Missing description
        result = self.run_task_manager([
            "queue", "add",
            "--name", "test-queue",
            "--title", "Test Queue"
        ])
        self.assertNotEqual(result.returncode, 0)

    def test_queue_invalid_command(self):
        """Test invalid queue subcommand."""
        result = self.run_task_manager(["queue", "invalid"])
        self.assertNotEqual(result.returncode, 0)

    def test_tasks_root_creation(self):
        """Test that tasks root directory is created if it doesn't exist."""
        # Use a non-existent directory
        non_existent_root = self.test_dir + "/non_existent"
        
        result = self.run_task_manager([
            "--tasks-root", non_existent_root,
            "queue", "add",
            "--name", "test-queue",
            "--title", "Test Queue",
            "--description", "Test description"
        ])
        self.assertEqual(result.returncode, 0)
        
        # Verify the directory was created
        self.assertTrue(Path(non_existent_root).exists())
        self.assertTrue(Path(non_existent_root).is_dir())

    def test_queue_list_formatting(self):
        """Test that queue list output is properly formatted."""
        # Create a queue with known data
        result = self.run_task_manager([
            "queue", "add",
            "--name", "format-test",
            "--title", "Format Test Queue",
            "--description", "Testing output formatting"
        ])
        self.assertEqual(result.returncode, 0)
        
        # List queues and check formatting
        result = self.run_task_manager(["queue", "list"])
        self.assertEqual(result.returncode, 0)
        
        lines = result.stdout.strip().split('\n')
        # Should have header, separator, and at least one queue line
        self.assertGreaterEqual(len(lines), 3)
        
        # Check header
        self.assertIn("Name", lines[0])
        self.assertIn("Title", lines[0])
        self.assertIn("Description", lines[0])
        
        # Check separator
        self.assertTrue(all(c in '-' for c in lines[1] if c != ' '))


if __name__ == '__main__':
    unittest.main() 