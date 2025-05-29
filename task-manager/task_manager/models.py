from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any
import time


@dataclass
class Queue:
    """Data representation of a task queue."""

    name: str
    title: str
    description: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)

    @classmethod
    def from_meta(cls, name: str, meta: Dict[str, Any]) -> "Queue":
        return cls(name=name, title=meta.get("title", ""), description=meta.get("description", ""))


@dataclass
class Task:
    """Data representation of a task."""

    id: str
    title: str
    description: str
    status: str = "todo"
    comments: List[Dict[str, Any]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        return cls(**data)
