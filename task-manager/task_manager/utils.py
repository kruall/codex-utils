"""Utility helpers for the task manager."""

from __future__ import annotations

import datetime
import logging
import sys


def format_timestamp(timestamp: float) -> str:
    """Format timestamp for display."""
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


class _LessThanFilter(logging.Filter):
    """Filter allowing only records below a given level."""

    def __init__(self, max_level: int) -> None:
        super().__init__()
        self.max_level = max_level

    def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover - trivial
        return record.levelno < self.max_level


def setup_logging(level: int = logging.INFO) -> None:
    """Configure basic logging for the CLI."""

    logger = logging.getLogger()
    if logger.handlers:
        # Logger already configured
        return

    logger.setLevel(level)
    fmt = logging.Formatter("%(message)s")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.addFilter(_LessThanFilter(logging.ERROR))
    stdout_handler.setFormatter(fmt)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.setFormatter(fmt)

    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)




