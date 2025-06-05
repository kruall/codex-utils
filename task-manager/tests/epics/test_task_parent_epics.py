import tempfile
import shutil
from pathlib import Path
from task_manager.core import TaskManager


def test_task_parent_epics():
    tmp = tempfile.mkdtemp()
    try:
        tm = TaskManager(tmp, epics_root=str(Path(tmp)/"epics"))
        tm.queue_add("q", "Q", "d")
        tid = tm.task_add("T", "d", "q")
        e1 = tm.epic_add("E1", "d")
        e2 = tm.epic_add("E2", "d")
        tm.epic_add_task(e1, tid)
        tm.epic_add_epic(e1, e2)
        tm.epic_add_task(e2, tid)
        epics = tm.task_parent_epics(tid)
        ids = {e["id"] for e in epics}
        assert {e1, e2} <= ids
    finally:
        shutil.rmtree(tmp)

