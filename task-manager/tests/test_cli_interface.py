"""
Tests for CLI interface and general functionality.
"""

import subprocess
import tempfile
import unittest
from pathlib import Path


class TestCLIInterface(unittest.TestCase):
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.tasks_root = Path(self.test_dir) / "test_tasks"
        self.task_manager_path = Path(__file__).parent.parent / "task_manager.py"

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)

    def run_task_manager(self, args):
        """Helper method to run task manager with given arguments."""
        cmd = ["python", str(self.task_manager_path), "--tasks-root", str(self.tasks_root)] + args
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result

    def test_help_message(self):
        """Test that help message is displayed correctly."""
        result = self.run_task_manager(["--help"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Task Manager CLI", result.stdout)
        self.assertIn("--tasks-root", result.stdout)

    def test_no_command(self):
        """Test behavior when no command is provided."""
        result = self.run_task_manager([])
        self.assertEqual(result.returncode, 1)
        self.assertIn("usage:", result.stdout)

    def test_invalid_command(self):
        """Test behavior with invalid top-level command."""
        result = self.run_task_manager(["invalid"])
        self.assertNotEqual(result.returncode, 0)

    def test_queue_help(self):
        """Test queue command help."""
        result = self.run_task_manager(["queue", "--help"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Queue actions", result.stdout)
        self.assertIn("list", result.stdout)
        self.assertIn("add", result.stdout)

    def test_queue_add_help(self):
        """Test queue add command help."""
        result = self.run_task_manager(["queue", "add", "--help"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("--name", result.stdout)
        self.assertIn("--title", result.stdout)
        self.assertIn("--description", result.stdout)

    def test_task_command_implemented(self):
        """Test that task commands are now implemented."""
        result = self.run_task_manager(["task", "list"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("No tasks found", result.stdout)

    def test_custom_tasks_root(self):
        """Test using custom tasks root directory."""
        custom_root = Path(self.test_dir) / "custom_tasks"
        
        result = self.run_task_manager([
            "--tasks-root", str(custom_root),
            "queue", "add",
            "--name", "custom-queue",
            "--title", "Custom Queue",
            "--description", "Queue in custom directory"
        ])
        self.assertEqual(result.returncode, 0)
        
        # Verify queue was created in custom directory
        queue_dir = custom_root / "custom-queue"
        self.assertTrue(queue_dir.exists())
        
        meta_file = queue_dir / "meta.json"
        self.assertTrue(meta_file.exists())

    def test_tasks_root_with_spaces(self):
        """Test tasks root directory with spaces in path."""
        custom_root = Path(self.test_dir) / "path with spaces"
        
        result = self.run_task_manager([
            "--tasks-root", str(custom_root),
            "queue", "add",
            "--name", "space-queue",
            "--title", "Space Queue",
            "--description", "Queue in path with spaces"
        ])
        self.assertEqual(result.returncode, 0)
        
        # Verify queue was created
        queue_dir = custom_root / "space-queue"
        self.assertTrue(queue_dir.exists())

    def test_queue_name_validation(self):
        """Test queue name with various characters."""
        # Test valid queue names
        valid_names = ["test-queue", "test_queue", "testqueue", "test123", "123test"]
        
        for name in valid_names:
            result = self.run_task_manager([
                "queue", "add",
                "--name", name,
                "--title", f"Title for {name}",
                "--description", f"Description for {name}"
            ])
            self.assertEqual(result.returncode, 0, f"Failed for queue name: {name}")

    def test_empty_arguments(self):
        """Test behavior with empty string arguments."""
        result = self.run_task_manager([
            "queue", "add",
            "--name", "",
            "--title", "Empty Name Test",
            "--description", "Testing empty name"
        ])
        # Empty name should fail because it creates an invalid directory path
        self.assertEqual(result.returncode, 1)

    def test_very_long_arguments(self):
        """Test behavior with very long arguments."""
        long_string = "x" * 1000
        
        result = self.run_task_manager([
            "queue", "add",
            "--name", "long-test",
            "--title", long_string,
            "--description", long_string
        ])
        self.assertEqual(result.returncode, 0)
        
        # Verify the long strings were stored correctly
        import json
        meta_file = self.tasks_root / "long-test" / "meta.json"
        with open(meta_file, 'r') as f:
            meta = json.load(f)
        
        self.assertEqual(meta['title'], long_string)
        self.assertEqual(meta['description'], long_string)


if __name__ == '__main__':
    unittest.main() 