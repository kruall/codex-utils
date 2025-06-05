import json
import shutil
import tempfile
import unittest
from pathlib import Path

from task_manager import TaskManager

class TestEpicStatusValidation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.mkdtemp()
        self.tasks_root = Path(self.temp) / "tasks"
        self.epics_root = Path(self.temp) / "epics"
        self.tm = TaskManager(str(self.tasks_root), epics_root=str(self.epics_root))
        self.tm.queue_add("q", "Q", "d")
        self.task_id = self.tm.task_add("T", "D", "q")

    def tearDown(self):
        shutil.rmtree(self.temp)

    def test_invalid_closed_epics(self):
        epic_id = self.tm.epic_add("E", "D")
        self.tm.epic_add_task(epic_id, self.task_id)
        path = self.epics_root / f"{epic_id}.json"
        data = json.loads(path.read_text())
        data["status"] = "closed"
        path.write_text(json.dumps(data))
        invalid = self.tm.invalid_closed_epics()
        self.assertIn(epic_id, invalid)

if __name__ == "__main__":
    unittest.main()
