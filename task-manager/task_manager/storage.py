import json
from pathlib import Path
from typing import Any, Optional


def load_json(path: Path) -> Optional[dict[str, Any]]:
    """Load JSON data from a file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def save_json(path: Path, data: dict[str, Any]) -> bool:
    """Save JSON data to a file."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except (OSError, IOError):
        return False

