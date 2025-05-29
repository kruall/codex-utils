"""Task manager package exports."""

from .core import TaskManager
from .tui import launch_tui
from .utils import format_timestamp, setup_logging
from .dashboard import generate_dashboard

__version__ = "0.1.0"

from .cli import main

__all__ = [
    "TaskManager",
    "launch_tui",
    "format_timestamp",
    "setup_logging",
    "generate_dashboard",
    "main",
    "__version__",
]

