import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from task_manager import TaskManager


class TestGitHubSync(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.tasks_root = Path(self.temp_dir) / "tasks"
        self.tm = TaskManager(str(self.tasks_root))

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_sync_from_github(self) -> None:
        task_data = {"id": "DEV-1", "title": "Remote", "description": "Desc"}
        with patch("task_manager.core.fetch_github_tasks", return_value=[task_data]):
            ids = self.tm.sync_from_github(["owner/repo"])
        self.assertEqual(ids, ["DEV-1"])
        task_file = self.tasks_root / "DEV" / "DEV-1.json"
        self.assertTrue(task_file.exists())
        with open(task_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["title"], "Remote")


if __name__ == "__main__":
    unittest.main()
