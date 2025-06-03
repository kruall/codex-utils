import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestVerifyCommand(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.tasks_root = Path(self.temp_dir) / "tasks"
        self.task_manager_path = Path(__file__).parent.parent / "task_manager.py"
        # create a queue for tasks
        self.run_task_manager([
            "queue",
            "add",
            "--name",
            "q",
            "--title",
            "Q",
            "--description",
            "Desc",
        ])

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def run_task_manager(self, args):
        cmd = [
            sys.executable,
            str(self.task_manager_path),
            "--tasks-root",
            str(self.tasks_root),
        ] + args
        return subprocess.run(cmd, capture_output=True, text=True)

    def test_verify_no_tasks_in_progress(self):
        result = self.run_task_manager(["verify"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("No tasks in progress", result.stdout)

    def test_verify_with_in_progress_tasks(self):
        self.run_task_manager([
            "task",
            "add",
            "--title",
            "Task",
            "--description",
            "Desc",
            "--queue",
            "q",
        ])
        self.run_task_manager(["task", "start", "--id", "q-1"])
        result = self.run_task_manager(["verify"])
        self.assertEqual(result.returncode, 1)
        self.assertIn("Found 1 task in progress", result.stdout)
        self.assertIn("q-1", result.stdout)


if __name__ == "__main__":
    unittest.main()
