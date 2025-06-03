import unittest
import tempfile
import shutil
from pathlib import Path

from task_manager import TaskManager

class TestEpicPersistence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.tasks_root = Path(self.tmp) / "tasks"
        self.epics_root = Path(self.tmp) / "epics"
        self.tm = TaskManager(str(self.tasks_root), epics_root=str(self.epics_root))
        # create queue and task for relation tests
        self.tm.queue_add("q", "Queue", "desc")
        self.task_id = self.tm.task_add("Task", "Desc", "q")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_epic_add_and_show(self):
        epic_id = self.tm.epic_add("Epic", "Desc")
        epic_file = self.epics_root / f"{epic_id}.json"
        self.assertTrue(epic_file.exists())
        data = self.tm.epic_show(epic_id)
        self.assertEqual(data["title"], "Epic")
        self.assertEqual(data["status"], "open")

    def test_epic_relationships(self):
        parent = self.tm.epic_add("Parent", "Desc")
        child = self.tm.epic_add("Child", "Desc")
        self.tm.epic_add_task(parent, self.task_id)
        self.tm.epic_add_epic(parent, child)

        p = self.tm.epic_show(parent)
        c = self.tm.epic_show(child)

        self.assertIn(self.task_id, p["child_tasks"])
        self.assertIn(child, p["child_epics"])
        self.assertEqual(c["parent_epic"], parent)

    def test_epic_update(self):
        epic_id = self.tm.epic_add("Title", "Desc")
        self.tm.epic_update(epic_id, "title", "New")
        data = self.tm.epic_show(epic_id)
        self.assertEqual(data["title"], "New")

if __name__ == "__main__":
    unittest.main()
