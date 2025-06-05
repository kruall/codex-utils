from pathlib import Path
from task_manager.epic_manager import EpicManager
from task_manager.models import Epic
from task_manager.storage import save_json


def test_list_epics(tmp_path: Path):
    epics_root = tmp_path / "epics"
    epics_root.mkdir()
    efile = epics_root / "epic-1.json"
    save_json(efile, Epic(id="epic-1", title="T", description="D").to_dict())
    manager = EpicManager(epics_root)
    epics = manager.list_epics()
    assert epics[0]["id"] == "epic-1"
