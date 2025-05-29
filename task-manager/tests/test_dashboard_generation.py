import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from task_manager import TaskManager
from task_manager.dashboard import generate_dashboard


class TestDashboardGeneration(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.tasks_root = Path(self.temp_dir) / "tasks"
        self.output = Path(self.temp_dir) / "site" / "index.html"
        self.tm = TaskManager(str(self.tasks_root))

    def tearDown(self) -> None:
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_generate_dashboard(self) -> None:
        self.tm.queue_add("q", "Q", "desc")
        self.tm.task_add("Title", "Desc", "q")
        out_path = generate_dashboard(str(self.tasks_root), str(self.output))
        self.assertTrue(out_path.exists())
        html = out_path.read_text(encoding="utf-8")
        self.assertIn("Title", html)
