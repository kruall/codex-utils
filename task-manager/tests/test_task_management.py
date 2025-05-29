"""
Tests for task management functionality.
"""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestTaskManagement(unittest.TestCase):
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.tasks_root = Path(self.test_dir) / "test_tasks"
        self.task_manager_path = Path(__file__).parent.parent / "task_manager.py"
        
        # Create a test queue for tasks
        self.run_task_manager([
            "queue", "add",
            "--name", "test-queue",
            "--title", "Test Queue",
            "--description", "Queue for testing tasks"
        ])

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)

    def run_task_manager(self, args):
        """Helper method to run task manager with given arguments."""
        cmd = ["python", str(self.task_manager_path), "--tasks-root", str(self.tasks_root)] + args
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result

    def test_task_add_success(self):
        """Test successfully adding a new task."""
        result = self.run_task_manager([
            "task", "add",
            "--title", "Test Task",
            "--description", "A test task for testing",
            "--queue", "test-queue"
        ])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Task 'test-queue-1' created successfully", result.stdout)
        
        # Verify task file was created
        task_file = self.tasks_root / "test-queue" / "test-queue-1.json"
        self.assertTrue(task_file.exists())
        
        # Verify task content
        with open(task_file, 'r') as f:
            task_data = json.load(f)
        
        self.assertEqual(task_data['id'], "test-queue-1")
        self.assertEqual(task_data['title'], "Test Task")
        self.assertEqual(task_data['description'], "A test task for testing")
        self.assertEqual(task_data['status'], "todo")
        self.assertEqual(task_data['comments'], [])
        self.assertIn('created_at', task_data)
        self.assertIn('updated_at', task_data)
        self.assertIsNone(task_data.get('started_at'))
        self.assertIsNone(task_data.get('closed_at'))

    def test_task_add_nonexistent_queue(self):
        """Test adding a task to a non-existent queue."""
        result = self.run_task_manager([
            "task", "add",
            "--title", "Test Task",
            "--description", "A test task",
            "--queue", "nonexistent-queue"
        ])
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error: Queue 'nonexistent-queue' does not exist", result.stderr)

    def test_task_list_empty(self):
        """Test listing tasks when no tasks exist."""
        result = self.run_task_manager(["task", "list"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("No tasks found", result.stdout)

    def test_task_list_with_tasks(self):
        """Test listing tasks when tasks exist."""
        # Create multiple tasks
        tasks_data = [
            ("Task 1", "Description 1"),
            ("Task 2", "Description 2"),
            ("Task 3", "Description 3")
        ]
        
        for title, description in tasks_data:
            result = self.run_task_manager([
                "task", "add",
                "--title", title,
                "--description", description,
                "--queue", "test-queue"
            ])
            self.assertEqual(result.returncode, 0)
        
        # List tasks
        result = self.run_task_manager(["task", "list"])
        self.assertEqual(result.returncode, 0)
        
        # Check that all tasks are listed
        for title, _ in tasks_data:
            self.assertIn(title, result.stdout)
        
        # Check header
        self.assertIn("ID", result.stdout)
        self.assertIn("Title", result.stdout)
        self.assertIn("Status", result.stdout)

    def test_task_list_filter_by_status(self):
        """Test filtering tasks by status."""
        # Create tasks and change their status
        self.run_task_manager([
            "task", "add",
            "--title", "Todo Task",
            "--description", "A todo task",
            "--queue", "test-queue"
        ])
        
        self.run_task_manager([
            "task", "add",
            "--title", "In Progress Task",
            "--description", "An in progress task",
            "--queue", "test-queue"
        ])
        
        # Start the second task
        self.run_task_manager(["task", "start", "--id", "test-queue-2"])
        
        # Filter by todo status
        result = self.run_task_manager(["task", "list", "--status", "todo"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Todo Task", result.stdout)
        self.assertNotIn("In Progress Task", result.stdout)
        
        # Filter by in_progress status
        result = self.run_task_manager(["task", "list", "--status", "in_progress"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("In Progress Task", result.stdout)
        self.assertNotIn("Todo Task", result.stdout)

    def test_task_list_filter_by_queue(self):
        """Test filtering tasks by queue."""
        # Create another queue
        self.run_task_manager([
            "queue", "add",
            "--name", "other-queue",
            "--title", "Other Queue",
            "--description", "Another queue"
        ])
        
        # Create tasks in different queues
        self.run_task_manager([
            "task", "add",
            "--title", "Task in test queue",
            "--description", "Description",
            "--queue", "test-queue"
        ])
        
        self.run_task_manager([
            "task", "add",
            "--title", "Task in other queue",
            "--description", "Description",
            "--queue", "other-queue"
        ])
        
        # Filter by test-queue
        result = self.run_task_manager(["task", "list", "--queue", "test-queue"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Task in test queue", result.stdout)
        self.assertNotIn("Task in other queue", result.stdout)
        
        # Filter by other-queue
        result = self.run_task_manager(["task", "list", "--queue", "other-queue"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Task in other queue", result.stdout)
        self.assertNotIn("Task in test queue", result.stdout)

    def test_task_show_success(self):
        """Test showing task details."""
        # Create a task
        self.run_task_manager([
            "task", "add",
            "--title", "Detailed Task",
            "--description", "A task with details",
            "--queue", "test-queue"
        ])
        
        # Show task details
        result = self.run_task_manager(["task", "show", "--id", "test-queue-1"])
        self.assertEqual(result.returncode, 0)
        
        self.assertIn("ID: test-queue-1", result.stdout)
        self.assertIn("Title: Detailed Task", result.stdout)
        self.assertIn("Description: A task with details", result.stdout)
        self.assertIn("Status: todo", result.stdout)
        self.assertIn("Created:", result.stdout)
        self.assertIn("Updated:", result.stdout)
        self.assertIn("No comments", result.stdout)
        self.assertNotIn("Started:", result.stdout)
        self.assertNotIn("Closed:", result.stdout)

    def test_task_show_nonexistent(self):
        """Test showing details of non-existent task."""
        result = self.run_task_manager(["task", "show", "--id", "nonexistent-1"])
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error: Task 'nonexistent-1' not found", result.stderr)

    def test_task_update_success(self):
        """Test updating task fields."""
        # Create a task
        self.run_task_manager([
            "task", "add",
            "--title", "Original Title",
            "--description", "Original Description",
            "--queue", "test-queue"
        ])
        
        # Update title
        result = self.run_task_manager([
            "task", "update",
            "--id", "test-queue-1",
            "--field", "title",
            "--value", "Updated Title"
        ])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Task 'test-queue-1' updated successfully", result.stdout)
        
        # Update description
        result = self.run_task_manager([
            "task", "update",
            "--id", "test-queue-1",
            "--field", "description",
            "--value", "Updated Description"
        ])
        self.assertEqual(result.returncode, 0)
        
        # Update status
        result = self.run_task_manager([
            "task", "update",
            "--id", "test-queue-1",
            "--field", "status",
            "--value", "in_progress"
        ])
        self.assertEqual(result.returncode, 0)
        
        # Verify updates
        result = self.run_task_manager(["task", "show", "--id", "test-queue-1"])
        self.assertIn("Title: Updated Title", result.stdout)
        self.assertIn("Description: Updated Description", result.stdout)
        self.assertIn("Status: in_progress", result.stdout)

    def test_task_update_invalid_field(self):
        """Test updating task with invalid field."""
        # Create a task
        self.run_task_manager([
            "task", "add",
            "--title", "Test Task",
            "--description", "Description",
            "--queue", "test-queue"
        ])
        
        # Try to update invalid field
        result = self.run_task_manager([
            "task", "update",
            "--id", "test-queue-1",
            "--field", "invalid_field",
            "--value", "some value"
        ])
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error: Field 'invalid_field' is not allowed", result.stderr)

    def test_task_start(self):
        """Test starting a task."""
        # Create a task
        self.run_task_manager([
            "task", "add",
            "--title", "Task to Start",
            "--description", "Description",
            "--queue", "test-queue"
        ])
        
        # Start the task
        result = self.run_task_manager(["task", "start", "--id", "test-queue-1"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Task 'test-queue-1' updated successfully", result.stdout)
        
        # Verify status changed
        result = self.run_task_manager(["task", "show", "--id", "test-queue-1"])
        self.assertIn("Status: in_progress", result.stdout)

        # Verify started_at timestamp was recorded
        task_file = self.tasks_root / "test-queue" / "test-queue-1.json"
        with open(task_file) as f:
            data = json.load(f)
        self.assertIsNotNone(data.get("started_at"))
        self.assertIsNone(data.get("closed_at"))

    def test_task_done(self):
        """Test marking a task as done."""
        # Create a task
        self.run_task_manager([
            "task", "add",
            "--title", "Task to Complete",
            "--description", "Description",
            "--queue", "test-queue"
        ])
        
        # Mark task as done
        result = self.run_task_manager(["task", "done", "--id", "test-queue-1"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Task 'test-queue-1' updated successfully", result.stdout)
        
        # Verify status changed
        result = self.run_task_manager(["task", "show", "--id", "test-queue-1"])
        self.assertIn("Status: done", result.stdout)

        # Verify closed_at timestamp was recorded
        task_file = self.tasks_root / "test-queue" / "test-queue-1.json"
        with open(task_file) as f:
            data = json.load(f)
        self.assertIsNotNone(data.get("closed_at"))

    def test_task_comment_add(self):
        """Test adding comments to a task."""
        # Create a task
        self.run_task_manager([
            "task", "add",
            "--title", "Task with Comments",
            "--description", "Description",
            "--queue", "test-queue"
        ])
        
        # Add a comment
        result = self.run_task_manager([
            "task", "comment", "add",
            "--id", "test-queue-1",
            "--comment", "This is a test comment"
        ])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Comment added to task 'test-queue-1' with ID 1", result.stdout)
        
        # Add another comment
        result = self.run_task_manager([
            "task", "comment", "add",
            "--id", "test-queue-1",
            "--comment", "This is another comment"
        ])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Comment added to task 'test-queue-1' with ID 2", result.stdout)
        
        # Verify comments in task show
        result = self.run_task_manager(["task", "show", "--id", "test-queue-1"])
        self.assertIn("Comments (2):", result.stdout)
        self.assertIn("[1]", result.stdout)
        self.assertIn("This is a test comment", result.stdout)
        self.assertIn("[2]", result.stdout)
        self.assertIn("This is another comment", result.stdout)

    def test_task_comment_list(self):
        """Test listing task comments."""
        # Create a task
        self.run_task_manager([
            "task", "add",
            "--title", "Task with Comments",
            "--description", "Description",
            "--queue", "test-queue"
        ])
        
        # Add comments
        self.run_task_manager([
            "task", "comment", "add",
            "--id", "test-queue-1",
            "--comment", "First comment"
        ])
        self.run_task_manager([
            "task", "comment", "add",
            "--id", "test-queue-1",
            "--comment", "Second comment"
        ])
        
        # List comments
        result = self.run_task_manager(["task", "comment", "list", "--id", "test-queue-1"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Comments for task test-queue-1:", result.stdout)
        self.assertIn("[1]", result.stdout)
        self.assertIn("First comment", result.stdout)
        self.assertIn("[2]", result.stdout)
        self.assertIn("Second comment", result.stdout)

    def test_task_comment_remove(self):
        """Test removing task comments."""
        # Create a task
        self.run_task_manager([
            "task", "add",
            "--title", "Task with Comments",
            "--description", "Description",
            "--queue", "test-queue"
        ])
        
        # Add comments
        self.run_task_manager([
            "task", "comment", "add",
            "--id", "test-queue-1",
            "--comment", "Comment to keep"
        ])
        self.run_task_manager([
            "task", "comment", "add",
            "--id", "test-queue-1",
            "--comment", "Comment to remove"
        ])
        
        # Remove second comment
        result = self.run_task_manager([
            "task", "comment", "remove",
            "--id", "test-queue-1",
            "--comment-id", "2"
        ])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Comment 2 removed from task 'test-queue-1'", result.stdout)
        
        # Verify comment was removed
        result = self.run_task_manager(["task", "comment", "list", "--id", "test-queue-1"])
        self.assertIn("Comment to keep", result.stdout)
        self.assertNotIn("Comment to remove", result.stdout)

    def test_task_comment_remove_nonexistent(self):
        """Test removing non-existent comment."""
        # Create a task
        self.run_task_manager([
            "task", "add",
            "--title", "Task with Comments",
            "--description", "Description",
            "--queue", "test-queue"
        ])
        
        # Try to remove non-existent comment
        result = self.run_task_manager([
            "task", "comment", "remove",
            "--id", "test-queue-1",
            "--comment-id", "999"
        ])
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error: Comment with ID 999 not found", result.stderr)

    def test_task_comment_operations_nonexistent_task(self):
        """Test comment operations on non-existent task."""
        # Try to add comment to non-existent task
        result = self.run_task_manager([
            "task", "comment", "add",
            "--id", "nonexistent-1",
            "--comment", "Test comment"
        ])
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error: Task 'nonexistent-1' not found", result.stderr)
        
        # Try to list comments for non-existent task
        result = self.run_task_manager([
            "task", "comment", "list",
            "--id", "nonexistent-1"
        ])
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error: Task 'nonexistent-1' not found", result.stderr)
        
        # Try to remove comment from non-existent task
        result = self.run_task_manager([
            "task", "comment", "remove",
            "--id", "nonexistent-1",
            "--comment-id", "1"
        ])
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error: Task 'nonexistent-1' not found", result.stderr)

    def test_task_numbering(self):
        """Test that task numbers increment correctly."""
        # Create multiple tasks
        for i in range(1, 4):
            result = self.run_task_manager([
                "task", "add",
                "--title", f"Task {i}",
                "--description", f"Description {i}",
                "--queue", "test-queue"
            ])
            self.assertEqual(result.returncode, 0)
            self.assertIn(f"Task 'test-queue-{i}' created successfully", result.stdout)
        
        # Verify all tasks exist
        result = self.run_task_manager(["task", "list"])
        self.assertIn("test-queue-1", result.stdout)
        self.assertIn("test-queue-2", result.stdout)
        self.assertIn("test-queue-3", result.stdout)

    def test_task_link_add_list_remove(self):
        """Test adding, listing, and removing task links."""
        # Create two tasks
        self.run_task_manager([
            "task",
            "add",
            "--title",
            "Task 1",
            "--description",
            "Desc",
            "--queue",
            "test-queue",
        ])
        self.run_task_manager([
            "task",
            "add",
            "--title",
            "Task 2",
            "--description",
            "Desc",
            "--queue",
            "test-queue",
        ])

        # Add link
        result = self.run_task_manager([
            "task",
            "link",
            "add",
            "--id",
            "test-queue-1",
            "--target-id",
            "test-queue-2",
        ])
        self.assertEqual(result.returncode, 0)
        self.assertIn(
            "Link added between test-queue-1 and test-queue-2",
            result.stdout,
        )

        # List links
        result = self.run_task_manager([
            "task",
            "link",
            "list",
            "--id",
            "test-queue-1",
        ])
        self.assertEqual(result.returncode, 0)
        self.assertIn("related: test-queue-2", result.stdout)

        # Remove link
        result = self.run_task_manager([
            "task",
            "link",
            "remove",
            "--id",
            "test-queue-1",
            "--target-id",
            "test-queue-2",
        ])
        self.assertEqual(result.returncode, 0)
        self.assertIn(
            "Link removed between test-queue-1 and test-queue-2",
            result.stdout,
        )

        # Verify link removed
        result = self.run_task_manager([
            "task",
            "link",
            "list",
            "--id",
            "test-queue-1",
        ])
        self.assertEqual(result.returncode, 0)
        self.assertIn("No links found", result.stdout)

    def test_task_link_nonexistent(self):
        """Test link operations with non-existent tasks."""
        self.run_task_manager([
            "task",
            "add",
            "--title",
            "Task",
            "--description",
            "Desc",
            "--queue",
            "test-queue",
        ])

        result = self.run_task_manager([
            "task",
            "link",
            "add",
            "--id",
            "test-queue-1",
            "--target-id",
            "nonexistent-1",
        ])
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error: Task 'nonexistent-1' not found", result.stderr)


if __name__ == '__main__':
    unittest.main() 
