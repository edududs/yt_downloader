"""Ports for progress display. Use cases get the reporter; only bootstrap/CLI get the session."""

from typing import Literal, NewType, Protocol, Self

LogLevel = Literal["info", "warn", "error"]
TaskId = NewType("TaskId", int)


class ProgressReporterPort(Protocol):
    """Task bars plus a log line channel. Must be safe to call from worker threads."""

    def add_task(self, description: str, *, total: int | None = None) -> TaskId:
        """Create a task bar; total=None means unknown until `update(total=...)`."""
        ...

    def update(
        self,
        task: TaskId,
        *,
        advance: int = 0,
        completed: int | None = None,
        total: int | None = None,
        description: str | None = None,
    ) -> None:
        """Change a task; None keyword means 'leave unchanged'; `completed` wins over `advance`."""
        ...

    def complete(self, task: TaskId) -> None:
        """Mark a task finished (fill to total when known)."""
        ...

    def log(self, message: str, *, level: LogLevel = "info") -> None:
        """Emit a line that survives above the task bars."""
        ...


class ProgressSessionPort(ProgressReporterPort, Protocol):
    """A reporter whose display has a lifecycle (context manager)."""

    def __enter__(self) -> Self: ...

    def __exit__(self, *exc: object) -> None: ...
