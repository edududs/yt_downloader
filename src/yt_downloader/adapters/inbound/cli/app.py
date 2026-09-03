"""Typer entry point. Parses args → builds domain requests → calls use cases → presents."""

import asyncio
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from yt_downloader.bootstrap.container import Container, build_container
from yt_downloader.config.settings import Settings
from yt_downloader.domain.errors import DomainError
from yt_downloader.domain.models import (
    AudioDownload,
    Bitrate,
    DownloadRequest,
    MediaSpec,
    PlaylistDownloadRequest,
    Resolution,
    VideoDownload,
)
from yt_downloader.domain.url_parser import parse_playlist_url, parse_video_url, parse_youtube_url

from .logging_setup import setup_logging
from .presenters import show_batch, show_downloaded, show_error, show_url_info

app = typer.Typer(
    name="yt-downloader", help="YouTube video and audio downloader", add_completion=False
)


@app.callback()
def main(
    ctx: typer.Context,
    debug: Annotated[bool, typer.Option("--debug", help="Enable debug logging")] = False,
) -> None:
    """Build the container once per invocation (tests inject one via ctx.obj)."""
    if ctx.obj is None:
        settings = Settings()
        console = Console()
        setup_logging(console, debug=debug or settings.debug)
        ctx.obj = build_container(settings, console)


def _container(ctx: typer.Context) -> Container:
    obj = ctx.obj
    if not isinstance(obj, Container):
        msg = "CLI context has no Container; callback did not run"
        raise TypeError(msg)
    return obj


def _media_spec(
    settings: Settings,
    *,
    audio_only: bool,
    resolution: Resolution | None,
    convert_to_mp3: bool | None,
    bitrate: str | None,
) -> MediaSpec:
    """CLI flags + settings defaults → MediaSpec (value objects validate at the boundary)."""
    if not audio_only:
        return VideoDownload(resolution=resolution or settings.download.video_resolution)
    convert = settings.audio.convert_to_mp3 if convert_to_mp3 is None else convert_to_mp3
    if not convert:
        return AudioDownload(mp3_bitrate=None)
    chosen = settings.audio.default_bitrate if bitrate is None else bitrate
    return AudioDownload(mp3_bitrate=Bitrate(chosen))


def _concurrency(settings: Settings, *, batch_size: int | None, async_mode: bool) -> int:
    """`--no-async` → 1; otherwise the explicit value (even 0, so the domain rejects it)."""
    if not async_mode:
        return 1
    return settings.download.batch_size if batch_size is None else batch_size


@app.command("download-video")
def download_video(
    ctx: typer.Context,
    url: Annotated[str, typer.Argument(help="YouTube video URL")],
    output: Annotated[Path | None, typer.Option("--output", "-o", help="Output directory")] = None,
    resolution: Annotated[
        Resolution | None, typer.Option("--resolution", "-r", help="lowest|highest")
    ] = None,
    audio_only: Annotated[bool, typer.Option("--audio-only", help="Download audio only")] = False,
    convert_to_mp3: Annotated[
        bool | None, typer.Option("--mp3/--no-mp3", help="Convert audio to MP3")
    ] = None,
    bitrate: Annotated[
        str | None, typer.Option("--bitrate", "-b", help="MP3 bitrate, e.g. 128k")
    ] = None,
) -> None:
    """Download a single YouTube video (or its audio)."""
    container = _container(ctx)
    settings = container.settings
    try:
        request = DownloadRequest(
            target=parse_video_url(url),
            media=_media_spec(
                settings,
                audio_only=audio_only,
                resolution=resolution,
                convert_to_mp3=convert_to_mp3,
                bitrate=bitrate,
            ),
            output_dir=output or settings.download.output_dir,
        )
        with container.progress:
            result = container.download_media.execute(request)
    except DomainError as exc:
        show_error(container.console, exc)
        raise typer.Exit(1) from exc
    show_downloaded(container.console, result)


@app.command("download-playlist")
def download_playlist(
    ctx: typer.Context,
    url: Annotated[str, typer.Argument(help="YouTube playlist URL")],
    output: Annotated[Path | None, typer.Option("--output", "-o", help="Output directory")] = None,
    resolution: Annotated[
        Resolution | None, typer.Option("--resolution", "-r", help="lowest|highest")
    ] = None,
    audio_only: Annotated[
        bool, typer.Option("--audio-only/--no-audio-only", help="Download audio only")
    ] = True,
    convert_to_mp3: Annotated[
        bool | None, typer.Option("--mp3/--no-mp3", help="Convert audio to MP3")
    ] = None,
    bitrate: Annotated[
        str | None, typer.Option("--bitrate", "-b", help="MP3 bitrate, e.g. 128k")
    ] = None,
    batch_size: Annotated[
        int | None, typer.Option("--batch-size", help="Concurrent downloads")
    ] = None,
    async_mode: Annotated[
        bool, typer.Option("--async/--no-async", help="Download concurrently")
    ] = True,
) -> None:
    """Download every video of a playlist."""
    container = _container(ctx)
    settings = container.settings
    try:
        request = PlaylistDownloadRequest(
            target=parse_playlist_url(url),
            media=_media_spec(
                settings,
                audio_only=audio_only,
                resolution=resolution,
                convert_to_mp3=convert_to_mp3,
                bitrate=bitrate,
            ),
            output_dir=output or settings.download.output_dir,
            concurrency=_concurrency(settings, batch_size=batch_size, async_mode=async_mode),
        )
        with container.progress:
            result = asyncio.run(container.download_playlist.execute(request))
    except DomainError as exc:
        show_error(container.console, exc)
        raise typer.Exit(1) from exc
    total = len(result.successes) + len(result.failures)
    show_batch(container.console, result, request.output_dir, total)
    if not result.successes:
        raise typer.Exit(1)


@app.command("info")
def info(ctx: typer.Context, url: Annotated[str, typer.Argument(help="YouTube URL")]) -> None:
    """Show what kind of YouTube URL this is and its id."""
    container = _container(ctx)
    try:
        ref = parse_youtube_url(url)
    except DomainError as exc:
        show_error(container.console, exc)
        raise typer.Exit(1) from exc
    show_url_info(container.console, ref)
