from collections.abc import Callable
from pathlib import Path
from typing import ClassVar

import pytest

from yt_downloader.adapters.outbound.youtube import pytubefix_provider
from yt_downloader.adapters.outbound.youtube.pytubefix_provider import PytubefixProvider
from yt_downloader.application.ports.youtube_provider import YouTubeProviderPort
from yt_downloader.domain.errors import ProviderError, StreamUnavailableError
from yt_downloader.domain.models import PlaylistRef, Resolution, VideoRef

REF = VideoRef(id="dQw4w9WgXcQ", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
PL_REF = PlaylistRef(id="PLabc", url="https://www.youtube.com/playlist?list=PLabc")


class _FakeStream:
    filesize = 100

    def download(self, output_path: str) -> str:
        target = Path(output_path) / "video.mp4"
        target.write_bytes(b"x")
        return str(target)


class _FakeStreams:
    def __init__(self, stream: _FakeStream | None) -> None:
        self._stream = stream
        self.picked: list[str] = []

    def get_audio_only(self) -> _FakeStream | None:
        self.picked.append("audio")
        return self._stream

    def get_lowest_resolution(self) -> _FakeStream | None:
        self.picked.append("lowest")
        return self._stream

    def get_highest_resolution(self) -> _FakeStream | None:
        self.picked.append("highest")
        return self._stream


class _FakeYouTube:
    instances: ClassVar[list["_FakeYouTube"]] = []
    stream: ClassVar[_FakeStream | None] = _FakeStream()
    raise_on_init: ClassVar[Exception | None] = None
    raise_on_streams: ClassVar[Exception | None] = None

    def __init__(
        self, url: str, on_progress_callback: Callable[[_FakeStream, bytes, int], None]
    ) -> None:
        if self.raise_on_init:
            raise self.raise_on_init
        self.url = url
        self.hook = on_progress_callback
        self.title = "Fake Title"
        self._streams = _FakeStreams(self.stream)
        _FakeYouTube.instances.append(self)

    @property
    def streams(self) -> _FakeStreams:
        """Lazy like pytubefix: the real property fetches and may raise."""
        if self.raise_on_streams:
            raise self.raise_on_streams
        return self._streams


class _FakePlaylist:
    def __init__(self, url: str) -> None:
        self.url = url
        self.title = "Fake Playlist"
        self.video_urls = [
            "https://www.youtube.com/watch?v=aaaaaaaaaaa",
            "https://www.youtube.com/watch?v=bbbbbbbbbbb",
        ]


@pytest.fixture(autouse=True)
def _patch_vendor(monkeypatch: pytest.MonkeyPatch) -> None:
    _FakeYouTube.instances = []
    _FakeYouTube.stream = _FakeStream()
    _FakeYouTube.raise_on_init = None
    _FakeYouTube.raise_on_streams = None
    monkeypatch.setattr(pytubefix_provider, "YouTube", _FakeYouTube)
    monkeypatch.setattr(pytubefix_provider, "Playlist", _FakePlaylist)


def test_download_audio_returns_file_and_title(tmp_path: Path) -> None:
    provider: YouTubeProviderPort = PytubefixProvider()
    result = provider.download_audio(REF, tmp_path, lambda _d, _t: None)
    assert result.path == tmp_path / "video.mp4"
    assert result.title == "Fake Title"
    assert _FakeYouTube.instances[0].streams.picked == ["audio"]


@pytest.mark.parametrize(
    ("resolution", "picked"), [(Resolution.LOWEST, "lowest"), (Resolution.HIGHEST, "highest")]
)
def test_download_video_picks_resolution(
    tmp_path: Path, resolution: Resolution, picked: str
) -> None:
    PytubefixProvider().download_video(REF, resolution, tmp_path, lambda _d, _t: None)
    assert _FakeYouTube.instances[0].streams.picked == [picked]


def test_progress_hook_translates_bytes_remaining(tmp_path: Path) -> None:
    seen: list[tuple[int, int]] = []
    PytubefixProvider().download_audio(
        REF, tmp_path, lambda done, total: seen.append((done, total))
    )
    _FakeYouTube.instances[0].hook(_FakeStream(), b"", 40)
    assert seen == [(60, 100)]


def test_missing_stream_is_domain_error(tmp_path: Path) -> None:
    _FakeYouTube.stream = None
    with pytest.raises(StreamUnavailableError):
        PytubefixProvider().download_audio(REF, tmp_path, lambda _d, _t: None)


def test_vendor_exception_is_translated(tmp_path: Path) -> None:
    _FakeYouTube.raise_on_init = RuntimeError("bot detected")
    with pytest.raises(ProviderError, match="bot detected"):
        PytubefixProvider().download_audio(REF, tmp_path, lambda _d, _t: None)


def _audio(provider: PytubefixProvider, dest: Path) -> None:
    provider.download_audio(REF, dest, lambda _d, _t: None)


def _lowest(provider: PytubefixProvider, dest: Path) -> None:
    provider.download_video(REF, Resolution.LOWEST, dest, lambda _d, _t: None)


def _highest(provider: PytubefixProvider, dest: Path) -> None:
    provider.download_video(REF, Resolution.HIGHEST, dest, lambda _d, _t: None)


@pytest.mark.parametrize("download", [_audio, _lowest, _highest])
def test_lazy_streams_failure_is_translated(
    tmp_path: Path, download: Callable[[PytubefixProvider, Path], None]
) -> None:
    _FakeYouTube.raise_on_streams = RuntimeError("video unavailable")
    with pytest.raises(ProviderError, match="video unavailable"):
        download(PytubefixProvider(), tmp_path)


def test_fetch_playlist_parses_video_refs() -> None:
    info = PytubefixProvider().fetch_playlist(PL_REF)
    assert info.title == "Fake Playlist"
    assert [v.id for v in info.videos] == ["aaaaaaaaaaa", "bbbbbbbbbbb"]
    assert info.ref == PL_REF


@pytest.mark.integration
def test_real_download_audio(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.undo()  # use the real pytubefix
    result = PytubefixProvider().download_audio(REF, tmp_path, lambda _d, _t: None)
    assert result.path.exists()
    assert result.title
