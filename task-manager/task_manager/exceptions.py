class TaskManagerError(Exception):
    """Base exception for Task Manager errors."""


class QueueExistsError(TaskManagerError):
    """Raised when attempting to create a queue that already exists."""


class QueueNotFoundError(TaskManagerError):
    """Raised when a queue does not exist."""


class TaskNotFoundError(TaskManagerError):
    """Raised when a task does not exist."""


class InvalidFieldError(TaskManagerError):
    """Raised when an invalid field is specified for update."""


class CommentNotFoundError(TaskManagerError):
    """Raised when a comment does not exist."""


class LinkNotFoundError(TaskManagerError):
    """Raised when a link between tasks does not exist."""


class StorageError(TaskManagerError):
    """Raised when an underlying storage operation fails."""
