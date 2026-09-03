import io

from rich.console import Console

from yt_downloader.adapters.outbound.progress.rich_reporter import RichProgressReporter
from yt_downloader.application.use_cases.download_media import DownloadMediaUseCase
from yt_downloader.application.use_cases.download_playlist import DownloadPlaylistUseCase
from yt_downloader.bootstrap.container import build_container
from yt_downloader.config.settings import Settings


def test_builds_fully_wired_container() -> None:
    console = Console(file=io.StringIO())
    container = build_container(Settings(), console)
    assert container.console is console
    assert isinstance(container.progress, RichProgressReporter)
    assert isinstance(container.download_media, DownloadMediaUseCase)
    assert isinstance(container.download_playlist, DownloadPlaylistUseCase)
    assert container.settings.youtube.provider == "pytubefix"
