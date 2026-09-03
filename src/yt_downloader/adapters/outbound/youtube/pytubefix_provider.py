"""YouTubeProviderPort backed by pytubefix. The only module allowed to import pytubefix."""

# pyright: reportMissingTypeStubs=false
# pytubefix ships no py.typed/stubs; pyright reads its inline annotations from source.

from collections.abc import Callable
from pathlib import Path

from pytubefix import YouTube
from pytubefix.contrib.playlist import Playlist
from pytubefix.streams import Stream

from yt_downloader.application.ports.youtube_provider import ProgressCallback
from yt_downloader.domain.errors import ProviderError, StreamUnavailableError
from yt_downloader.domain.models import (
    DownloadedFile,
    PlaylistInfo,
    PlaylistRef,
    Resolution,
    VideoRef,
)
from yt_downloader.domain.url_parser import parse_video_url


def _guard[T](action: Callable[[], T], ref: VideoRef | PlaylistRef) -> T:
    """Run a vendor call; translate any failure into ProviderError."""
    try:
        return action()
    except Exception as exc:
        raise ProviderError(f"pytubefix failed for {ref.id}: {exc}") from exc


def _pick_audio(yt: YouTube) -> Stream | None:
    return yt.streams.get_audio_only()


def _pick_lowest(yt: YouTube) -> Stream | None:
    return yt.streams.get_lowest_resolution()


def _pick_highest(yt: YouTube) -> Stream | None:
    # pytubefix leaves `mime_type` unannotated on this getter; the call itself is typed.
    return yt.streams.get_highest_resolution()  # pyright: ignore[reportUnknownMemberType]


class PytubefixProvider:
    """pytubefix adapter. One YouTube object per download so each has its own hook."""

    provider_name = "pytubefix"

    def fetch_playlist(self, ref: PlaylistRef) -> PlaylistInfo:
        """Resolve title and video URLs of a playlist."""
        playlist = _guard(lambda: Playlist(ref.url), ref)
        title: str | None = _guard(lambda: playlist.title, ref)
        urls: list[str] = _guard(lambda: list(playlist.video_urls), ref)
        return PlaylistInfo(
            ref=ref,
            title=title or ref.id,
            videos=tuple(parse_video_url(u) for u in urls),
        )

    def download_audio(
        self, ref: VideoRef, dest_dir: Path, on_progress: ProgressCallback
    ) -> DownloadedFile:
        """Download the audio-only stream."""
        yt = self._open(ref, on_progress)
        return self._download(yt, ref, dest_dir, _pick_audio)

    def download_video(
        self, ref: VideoRef, resolution: Resolution, dest_dir: Path, on_progress: ProgressCallback
    ) -> DownloadedFile:
        """Download the progressive video stream at the requested resolution."""
        yt = self._open(ref, on_progress)
        picker = _pick_lowest if resolution is Resolution.LOWEST else _pick_highest
        return self._download(yt, ref, dest_dir, picker)

    @staticmethod
    def _open(ref: VideoRef, on_progress: ProgressCallback) -> YouTube:
        def hook(stream: Stream, _chunk: bytes, bytes_remaining: int) -> None:
            on_progress(stream.filesize - bytes_remaining, stream.filesize)

        return _guard(lambda: YouTube(ref.url, on_progress_callback=hook), ref)

    @staticmethod
    def _download(
        yt: YouTube, ref: VideoRef, dest_dir: Path, pick: Callable[[YouTube], Stream | None]
    ) -> DownloadedFile:
        # `yt.streams` is a lazy property that fetches (and may raise): evaluate inside the guard.
        stream = _guard(lambda: pick(yt), ref)
        if stream is None:
            raise StreamUnavailableError(f"No matching stream for {ref.id}")
        path: str | None = _guard(lambda: stream.download(output_path=str(dest_dir)), ref)
        if path is None:
            raise ProviderError(f"pytubefix returned no file path for {ref.id}")
        title: str = _guard(lambda: yt.title, ref)
        return DownloadedFile(path=Path(path), title=title)
