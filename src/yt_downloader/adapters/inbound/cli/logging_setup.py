"""Route stdlib logging (pytubefix logs too) through the same Rich Console."""

import logging

from rich.console import Console
from rich.logging import RichHandler


def setup_logging(console: Console, *, debug: bool) -> None:
    """Idempotent basicConfig with a RichHandler bound to `console`."""
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.WARNING,
        format="%(message)s",
        handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=False)],
        force=True,
    )
