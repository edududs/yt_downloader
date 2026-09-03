"""Rich output for CLI results. Policy (what to show) lives here, not in use cases.

ASCII-only text: Windows consoles without UTF-8 (cp1252) raise on emoji.
"""

from pathlib import Path

from rich.console import Console

from yt_downloader.domain.models import BatchDownloadResult, DownloadedFile, PlaylistRef, VideoRef


def show_downloaded(console: Console, result: DownloadedFile) -> None:
    """Single-file success line."""
    console.print(f"[green]Downloaded:[/green] {result.path}")


def show_batch(console: Console, result: BatchDownloadResult, output_dir: Path, total: int) -> None:
    """Playlist summary plus one line per failure."""
    console.print(
        f"[green]Downloaded {len(result.successes)}/{total} files to:[/green] {output_dir}"
    )
    for failure in result.failures:
        console.print(f"[yellow]Failed {failure.target.id}:[/yellow] {failure.reason}")


def show_url_info(console: Console, ref: VideoRef | PlaylistRef) -> None:
    """Output of the `info` command."""
    kind = "video" if isinstance(ref, VideoRef) else "playlist"
    console.print(f"[green]URL Type:[/green] {kind}")
    console.print(f"[green]{kind.capitalize()} ID:[/green] {ref.id}")


def show_error(console: Console, error: Exception) -> None:
    """Uniform error line."""
    console.print(f"[red]Error:[/red] {error}")
