import io

from rich.console import Console

from yt_downloader.adapters.outbound.progress.rich_reporter import RichProgressReporter
from yt_downloader.application.ports.progress_reporter import ProgressSessionPort


def make_reporter() -> tuple[RichProgressReporter, io.StringIO]:
    buffer = io.StringIO()
    console = Console(file=buffer, force_terminal=False, width=120, log_time=False, log_path=False)
    return RichProgressReporter(console), buffer


def test_log_levels_reach_console() -> None:
    reporter, buffer = make_reporter()
    session: ProgressSessionPort = reporter
    with session:
        session.log("plain info")
        session.log("careful", level="warn")
        session.log("broken", level="error")
    out = buffer.getvalue()
    assert "plain info" in out
    assert "careful" in out
    assert "broken" in out


def test_task_lifecycle_updates_rich_task() -> None:
    reporter, _ = make_reporter()
    with reporter:
        task = reporter.add_task("dl", total=10)
        reporter.update(task, completed=4)
        reporter.update(task, advance=2, description="renamed")
        state = reporter._progress.tasks[0]
        assert state.completed == 6
        assert state.description == "renamed"
        reporter.complete(task)
        assert reporter._progress.tasks[0].completed == 10
        assert reporter._progress.tasks[0].finished


def test_total_can_arrive_late() -> None:
    reporter, _ = make_reporter()
    with reporter:
        task = reporter.add_task("unknown size")
        assert reporter._progress.tasks[0].total is None
        reporter.update(task, completed=50, total=100)
        assert reporter._progress.tasks[0].total == 100
        reporter.complete(task)
        assert reporter._progress.tasks[0].completed == 100


def test_log_outside_session_still_prints() -> None:
    reporter, buffer = make_reporter()
    reporter.log("before start")
    assert "before start" in buffer.getvalue()
