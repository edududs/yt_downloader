"""Wire settings → adapters → use cases. Nothing else may import adapters/outbound."""

from dataclasses import dataclass

from rich.console import Console

from yt_downloader.adapters.outbound.audio.ffmpeg_converter import FfmpegConverter
from yt_downloader.adapters.outbound.filesystem.local import LocalFilesystem
from yt_downloader.adapters.outbound.progress.rich_reporter import RichProgressReporter
from yt_downloader.adapters.outbound.youtube.registry import build_youtube_provider
from yt_downloader.application.ports.progress_reporter import ProgressSessionPort
from yt_downloader.application.use_cases.download_media import DownloadMediaUseCase
from yt_downloader.application.use_cases.download_playlist import DownloadPlaylistUseCase
from yt_downloader.config.settings import Settings


@dataclass(frozen=True, slots=True)
class Container:
    """Everything the CLI needs."""

    settings: Settings
    console: Console
    progress: ProgressSessionPort
    download_media: DownloadMediaUseCase
    download_playlist: DownloadPlaylistUseCase


def build_container(settings: Settings, console: Console) -> Container:
    """Production wiring."""
    progress = RichProgressReporter(console)
    youtube = build_youtube_provider(settings.youtube)
    converter = FfmpegConverter(settings.audio.ffmpeg_path)
    fs = LocalFilesystem()
    download_media = DownloadMediaUseCase(
        youtube=youtube, converter=converter, fs=fs, progress=progress
    )
    download_playlist = DownloadPlaylistUseCase(
        youtube=youtube, download_media=download_media, progress=progress
    )
    return Container(
        settings=settings,
        console=console,
        progress=progress,
        download_media=download_media,
        download_playlist=download_playlist,
    )
