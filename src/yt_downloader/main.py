"""Main CLI entry point for yt-downloader using Typer."""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.logging import RichHandler

# Configure imports based on execution context
if __name__ == "__main__":
    # Running as script - add src to path
    sys.path.insert(0, str(Path(__file__).parent.parent))

# Use relative imports (works both as package and script)
from .audio import AudioConverter
from .commands import PlaylistCommand, VideoCommand
from .config.settings import settings
from .services.parser import URLParser

# Configure logging (will be updated after settings import)
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logger = logging.getLogger(__name__)

# Create Typer app
app = typer.Typer(
    name="yt-downloader",
    help="YouTube video and audio downloader",
    add_completion=False,
)

# Create console for rich output
console = Console()

# Initialize components
audio_converter = AudioConverter()
video_command = VideoCommand(downloader=None)  # Will be initialized with converter
playlist_command = PlaylistCommand(downloader=None)  # Will be initialized with converter

# Update commands with audio converter (downloader is created internally with None, so we need to set the converter)
if video_command.downloader:
    video_command.downloader.audio_converter = audio_converter  # type: ignore[assignment]
if playlist_command.downloader:
    playlist_command.downloader.audio_converter = audio_converter  # type: ignore[assignment]


@app.callback()
def main_callback(
    debug: Annotated[bool, typer.Option("--debug", help="Enable debug mode")] = False,
):
    """YouTube video and audio downloader CLI."""
    if debug or settings.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")


@app.command()
def download_video(
    url: Annotated[str, typer.Argument(help="YouTube video URL to download")],
    output: Annotated[
        Optional[Path], typer.Option("--output", "-o", help="Output directory")
    ] = None,
    resolution: Annotated[
        str, typer.Option("--resolution", "-r", help="Video resolution (lowest/highest)")
    ] = "lowest",
    audio_only: Annotated[bool, typer.Option("--audio-only", help="Download audio only")] = False,
    convert_to_mp3: Annotated[bool, typer.Option("--mp3", help="Convert audio to MP3")] = True,
    bitrate: Annotated[
        str, typer.Option("--bitrate", "-b", help="Audio bitrate for MP3 conversion")
    ] = "128k",
):
    """Download a single YouTube video."""
    try:
        # Validate URL
        url_type = URLParser.get_url_type(url)
        if url_type != "video":
            console.print(f"[red]Error:[/red] Invalid video URL: {url}")
            raise typer.Exit(1)

        console.print(f"[green]Downloading video:[/green] {url}")

        if audio_only:
            if convert_to_mp3:
                result = asyncio.run(
                    video_command.download_and_convert_audio_event(
                        url=url, output_path=str(output) if output else None, bitrate=bitrate
                    )
                )
                console.print(f"[green]✅ Audio downloaded and converted:[/green] {result}")
            else:
                result = video_command.download_audio(
                    url=url, output_path=str(output) if output else None, convert_to_mp3=False
                )
                console.print(f"[green]✅ Audio downloaded:[/green] {result}")
        else:
            result = video_command.download_video(
                url=url,
                output_path=str(output) if output else None,
                resolution=resolution,  # type: ignore[arg-type]
            )
            console.print(f"[green]✅ Video downloaded:[/green] {result}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from e


@app.command()
def download_playlist(
    url: Annotated[str, typer.Argument(help="YouTube playlist URL to download")],
    output: Annotated[
        Optional[Path], typer.Option("--output", "-o", help="Output directory")
    ] = None,
    resolution: Annotated[
        str, typer.Option("--resolution", "-r", help="Video resolution (lowest/highest)")
    ] = "lowest",
    audio_only: Annotated[bool, typer.Option("--audio-only", help="Download audio only")] = True,
    convert_to_mp3: Annotated[bool, typer.Option("--mp3", help="Convert audio to MP3")] = True,
    bitrate: Annotated[
        str, typer.Option("--bitrate", "-b", help="Audio bitrate for MP3 conversion")
    ] = "128k",
    batch_size: Annotated[
        int, typer.Option("--batch-size", help="Batch size for async downloads")
    ] = 5,
    async_mode: Annotated[
        bool, typer.Option("--async", help="Use asynchronous downloading")
    ] = True,
):
    """Download videos from a YouTube playlist."""
    try:
        # Validate URL
        url_type = URLParser.get_url_type(url)
        if url_type != "playlist":
            console.print(f"[red]Error:[/red] Invalid playlist URL: {url}")
            raise typer.Exit(1)

        console.print(f"[green]Downloading playlist:[/green] {url}")

        if audio_only:
            if async_mode:
                console.print("[yellow]Using asynchronous download mode...[/yellow]")
                results, output_dir = asyncio.run(
                    playlist_command.download_playlist_audio_async(
                        url=url,
                        output_path=str(output) if output else None,
                        bitrate=bitrate,
                        batch_size=batch_size,
                    )
                )
                console.print(
                    f"[green]✅ Downloaded {len(results)} audio files to:[/green] {output_dir}"
                )
            else:
                results = playlist_command.download_playlist_audio(
                    url=url,
                    output_path=str(output) if output else None,
                    convert_to_mp3=convert_to_mp3,
                    bitrate=bitrate,
                )
                console.print(f"[green]✅ Downloaded {len(results)} audio files[/green]")
        else:
            results = playlist_command.download_playlist_video(
                url=url,
                output_path=str(output) if output else None,
                resolution=resolution,  # type: ignore[arg-type]
            )
            console.print(f"[green]✅ Downloaded {len(results)} video files[/green]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from e


@app.command()
def info(
    url: Annotated[str, typer.Argument(help="YouTube URL to analyze")],
):
    """Get information about a YouTube URL."""
    try:
        url_type = URLParser.get_url_type(url)

        if url_type == "invalid":
            console.print(f"[red]Invalid YouTube URL:[/red] {url}")
            raise typer.Exit(1)

        console.print(f"[green]URL Type:[/green] {url_type}")

        if url_type == "video":
            video_id = URLParser.extract_video_id(url)
            if video_id:
                console.print(f"[green]Video ID:[/green] {video_id}")
        elif url_type == "playlist":
            playlist_id = URLParser.extract_playlist_id(url)
            if playlist_id:
                console.print(f"[green]Playlist ID:[/green] {playlist_id}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
