import subprocess
import tempfile
import unittest
from pathlib import Path


class TestEpicCLI(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.tasks_root = Path(self.test_dir) / "tasks"
        self.task_manager_path = Path(__file__).resolve().parents[2] / "task_manager.py"

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)

    def run_tm(self, args):
        cmd = [
            "python",
            str(self.task_manager_path),
            "--tasks-root",
            str(self.tasks_root),
        ] + args
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.test_dir)
        return result

    def test_epic_add_and_list(self):
        result = self.run_tm(["epic", "add", "--title", "E1", "--description", "Desc"])
        self.assertEqual(result.returncode, 0)

        result = self.run_tm(["epic", "list"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("epic-1", result.stdout)

    def test_epic_relations_and_done(self):
        # setup queue and task
        self.run_tm(["queue", "add", "--name", "q", "--title", "Q", "--description", "d"])
        self.run_tm(["task", "add", "--title", "T1", "--description", "d", "--queue", "q"])
        # create epics
        self.run_tm(["epic", "add", "--title", "Parent", "--description", "d"])
        self.run_tm(["epic", "add", "--title", "Child", "--description", "d"])
        # add relations
        self.run_tm(["epic", "add-task", "--id", "epic-1", "--task-id", "q-1"])
        self.run_tm(["epic", "add-epic", "--id", "epic-1", "--child-id", "epic-2"])

        # attempt to close epic before child complete
        result = self.run_tm(["epic", "done", "--id", "epic-1"])
        self.assertNotEqual(result.returncode, 0)

        # complete child entities
        self.run_tm(["task", "done", "--id", "q-1"])
        self.run_tm(["epic", "done", "--id", "epic-2"])

        result = self.run_tm(["epic", "done", "--id", "epic-1"])
        self.assertEqual(result.returncode, 0)
        show = self.run_tm(["epic", "show", "--id", "epic-1"])
        self.assertIn("closed", show.stdout)

    def test_epic_update_status_validation(self):
        self.run_tm(["queue", "add", "--name", "q", "--title", "Q", "--description", "d"])
        self.run_tm(["task", "add", "--title", "T", "--description", "d", "--queue", "q"])
        self.run_tm(["epic", "add", "--title", "E", "--description", "d"])
        self.run_tm(["epic", "add-task", "--id", "epic-1", "--task-id", "q-1"])
        result = self.run_tm(["epic", "update", "--id", "epic-1", "--field", "status", "--value", "closed"])
        self.assertNotEqual(result.returncode, 0)

    def test_auto_close_parent_epic(self):
        self.run_tm(["queue", "add", "--name", "q", "--title", "Q", "--description", "d"])
        self.run_tm(["task", "add", "--title", "T", "--description", "d", "--queue", "q"])
        self.run_tm(["epic", "add", "--title", "Parent", "--description", "d"])
        self.run_tm(["epic", "add", "--title", "Child", "--description", "d"])
        self.run_tm(["epic", "add-task", "--id", "epic-1", "--task-id", "q-1"])
        self.run_tm(["epic", "add-epic", "--id", "epic-1", "--child-id", "epic-2"])
        self.run_tm(["task", "done", "--id", "q-1"])
        self.run_tm(["epic", "done", "--id", "epic-2"])
        show = self.run_tm(["epic", "show", "--id", "epic-1"])
        self.assertIn("closed", show.stdout)

    def test_epic_remove_relations(self):
        self.run_tm(["queue", "add", "--name", "q", "--title", "Q", "--description", "d"])
        self.run_tm(["task", "add", "--title", "T", "--description", "d", "--queue", "q"])
        self.run_tm(["epic", "add", "--title", "Parent", "--description", "d"])
        self.run_tm(["epic", "add", "--title", "Child", "--description", "d"])
        self.run_tm(["epic", "add-task", "--id", "epic-1", "--task-id", "q-1"])
        self.run_tm(["epic", "add-epic", "--id", "epic-1", "--child-id", "epic-2"])
        self.run_tm(["epic", "remove-task", "--id", "epic-1", "--task-id", "q-1"])
        self.run_tm(["epic", "remove-epic", "--id", "epic-1", "--child-id", "epic-2"])
        show = self.run_tm(["epic", "show", "--id", "epic-1"])
        self.assertNotIn("q-1", show.stdout)
        self.assertNotIn("epic-2", show.stdout)


if __name__ == "__main__":
    unittest.main()
