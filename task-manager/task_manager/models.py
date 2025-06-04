from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any
from enum import Enum
import time


class TaskStatus(Enum):
    """Status values for tasks."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class EpicStatus(Enum):
    """Status values for epics."""
    OPEN = "open"
    CLOSED = "closed"


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
    status: TaskStatus = TaskStatus.TODO
    comments: List[Dict[str, Any]] = field(default_factory=list)
    links: Dict[str, List[str]] = field(default_factory=dict)
    epics: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    started_at: float | None = None
    closed_at: float | None = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['status'] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = TaskStatus(data['status'])
        if 'epics' not in data:
            data['epics'] = []
        return cls(**data)

@dataclass
class Epic:
    """Data representation of an epic grouping tasks and sub-epics."""

    id: str
    title: str
    description: str
    status: EpicStatus = EpicStatus.OPEN
    child_tasks: List[str] = field(default_factory=list)
    child_epics: List[str] = field(default_factory=list)
    parent_epic: str | None = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['status'] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Epic":
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = EpicStatus(data['status'])
        return cls(**data)
