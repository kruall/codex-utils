import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from task_manager.export_json import export_tasks_json
from task_manager.core import TaskManager


class TestExportJson(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.tasks_root = Path(self.tmpdir) / "tasks"
        self.output = Path(self.tmpdir) / "out.json"
        self.tm = TaskManager(str(self.tasks_root))

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmpdir)

    def test_export_with_remote_tasks(self) -> None:
        self.tm.queue_add("q", "Queue", "Desc")
        local_task_id = self.tm.task_add("Title", "Desc", "q")

        remote_tasks = [{"id": "REMOTE-1", "title": "Remote", "status": "todo"}]
        with patch("task_manager.export_json.fetch_github_tasks", return_value=remote_tasks):
            path = export_tasks_json(str(self.tasks_root), str(self.output), repos=["owner/repo"], token="tkn")

        data = json.loads(Path(path).read_text())
        ids = {t["id"] for t in data}
        self.assertIn(local_task_id, ids)
        self.assertIn("REMOTE-1", ids)


if __name__ == "__main__":
    unittest.main()
