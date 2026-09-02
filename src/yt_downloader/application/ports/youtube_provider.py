"""Port for YouTube libraries (pytubefix today; any other lib tomorrow)."""

from collections.abc import Callable
from pathlib import Path
from typing import Protocol

from yt_downloader.domain.models import (
    DownloadedFile,
    PlaylistInfo,
    PlaylistRef,
    Resolution,
    VideoRef,
)

ProgressCallback = Callable[[int, int], None]
"""Called from the download thread with (bytes_done, bytes_total)."""


class YouTubeProviderPort(Protocol):
    """Resolve playlists and download streams. Implementations raise only DomainError."""

    def fetch_playlist(self, ref: PlaylistRef) -> PlaylistInfo:
        """Resolve title and video refs; raise ProviderError on vendor failure."""
        ...

    def download_audio(
        self, ref: VideoRef, dest_dir: Path, on_progress: ProgressCallback
    ) -> DownloadedFile:
        """Download the audio-only stream into dest_dir; raise StreamUnavailableError if none."""
        ...

    def download_video(
        self, ref: VideoRef, resolution: Resolution, dest_dir: Path, on_progress: ProgressCallback
    ) -> DownloadedFile:
        """Download the progressive stream at `resolution`; raise StreamUnavailableError if none."""
        ...
