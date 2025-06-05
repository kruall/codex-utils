from __future__ import annotations

import time
from pathlib import Path
from typing import List, Dict, Optional

from .models import Epic
from .storage import load_json, save_json
from .exceptions import StorageError, TaskNotFoundError
from .utils import log_error

class EpicManager:
    """Service class for managing epics."""

    def __init__(self, epics_root: Path):
        self.epics_root = epics_root

    def find_epic_file(self, epic_id: str) -> Optional[Path]:
        path = self.epics_root / f"{epic_id}.json"
        return path if path.exists() else None

    def load_epic(self, epic_id: str) -> Epic:
        epic_file = self.find_epic_file(epic_id)
        if not epic_file:
            raise TaskNotFoundError(f"Epic '{epic_id}' not found")
        data = load_json(epic_file)
        if data is None:
            raise StorageError(f"Failed to read epic '{epic_id}'")
        return Epic.from_dict(data)

    def save_epic(self, epic: Epic) -> None:
        epic_file = self.find_epic_file(epic.id)
        if not epic_file:
            raise TaskNotFoundError(f"Epic '{epic.id}' not found")
        epic.updated_at = time.time()
        if not save_json(epic_file, epic.to_dict()):
            raise StorageError(f"Failed to save epic '{epic.id}'")

    def list_epics(self) -> List[Dict]:
        epics: List[Dict] = []
        for epic_file in self.epics_root.glob("epic-*.json"):
            data = load_json(epic_file)
            if data is None:
                continue
            try:
                epics.append(Epic.from_dict(data).to_dict())
            except Exception as e:  # pragma: no cover - shouldn't happen
                log_error(f"Error loading epic '{epic_file}': {e}")
        epics.sort(key=lambda e: e.get("created_at", 0))
        return epics

    def load_all_epics(self) -> List[Epic]:
        epics: List[Epic] = []
        for epic_file in self.epics_root.glob("epic-*.json"):
            data = load_json(epic_file)
            if data is None:
                continue
            try:
                epics.append(Epic.from_dict(data))
            except Exception as e:  # pragma: no cover - shouldn't happen
                log_error(f"Error loading epic '{epic_file}': {e}")
        return epics
