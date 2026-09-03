"""ProgressSessionPort backed by rich.progress.Progress.

Progress.update/log are thread-safe (internal lock), so download threads may
call this directly.
"""

from typing import Self

from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
)

from yt_downloader.application.ports.progress_reporter import LogLevel, TaskId

_STYLES: dict[LogLevel, str] = {"info": "", "warn": "yellow", "error": "bold red"}


class RichProgressReporter:
    """Live task bars + log lines rendered above them on one Console."""

    def __init__(self, console: Console) -> None:
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TimeElapsedColumn(),
            console=console,
        )

    @property
    def console(self) -> Console:
        """The Console shared with logging and presenters."""
        return self._progress.console

    def __enter__(self) -> Self:
        self._progress.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self._progress.stop()

    def add_task(self, description: str, *, total: int | None = None) -> TaskId:
        """Create a bar; total=None renders an indeterminate pulse until known."""
        return TaskId(int(self._progress.add_task(description, total=total)))

    def update(
        self,
        task: TaskId,
        *,
        advance: int = 0,
        completed: int | None = None,
        total: int | None = None,
        description: str | None = None,
    ) -> None:
        """Forward to Progress.update; None means 'leave unchanged'."""
        self._progress.update(
            TaskID(task), advance=advance, completed=completed, total=total, description=description
        )

    def complete(self, task: TaskId) -> None:
        """Fill the bar (or freeze it if total is unknown) and stop its clock."""
        task_id = TaskID(task)
        state = next(t for t in self._progress.tasks if t.id == task_id)
        target = state.total if state.total is not None else state.completed
        self._progress.update(task_id, completed=target)
        self._progress.stop_task(task_id)

    def log(self, message: str, *, level: LogLevel = "info") -> None:
        """Print a line above the bars (works before start() too)."""
        style = _STYLES[level]
        self._progress.log(f"[{style}]{message}[/]" if style else message)
