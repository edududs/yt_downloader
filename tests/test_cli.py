import dataclasses
import io
from pathlib import Path

import pytest
from rich.console import Console
from typer.testing import CliRunner

from tests.fakes import FakeAudioConverter, FakeFilesystem, FakeYouTubeProvider, RecordingProgress
from yt_downloader.adapters.inbound.cli.app import app
from yt_downloader.application.use_cases.download_media import DownloadMediaUseCase
from yt_downloader.application.use_cases.download_playlist import DownloadPlaylistUseCase
from yt_downloader.bootstrap.container import Container
from yt_downloader.config.settings import DownloadSettings, Settings
from yt_downloader.domain.models import PlaylistInfo, PlaylistRef, VideoRef

VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy4qtr5mYJ2hBJc5VcWKvLk"
PL_REF = PlaylistRef(id="PLrAXtmRdnEQy4qtr5mYJ2hBJc5VcWKvLk", url=PLAYLIST_URL)
VIDEOS = tuple(VideoRef(id=c * 11, url=f"https://youtu.be/{c * 11}") for c in "abc")

runner = CliRunner()


@pytest.fixture
def youtube() -> FakeYouTubeProvider:
    return FakeYouTubeProvider(playlist=PlaylistInfo(PL_REF, "Mix", VIDEOS))


@pytest.fixture
def container(youtube: FakeYouTubeProvider, tmp_path: Path) -> Container:
    progress = RecordingProgress()
    settings = Settings(download=DownloadSettings(output_dir=tmp_path))
    media = DownloadMediaUseCase(
        youtube=youtube, converter=FakeAudioConverter(), fs=FakeFilesystem(), progress=progress
    )
    playlist = DownloadPlaylistUseCase(youtube=youtube, download_media=media, progress=progress)
    return Container(
        settings=settings,
        console=Console(force_terminal=False, width=200),
        progress=progress,
        download_media=media,
        download_playlist=playlist,
    )


def test_info_video(container: Container) -> None:
    result = runner.invoke(app, ["info", VIDEO_URL], obj=container)
    assert result.exit_code == 0
    assert "video" in result.output
    assert "dQw4w9WgXcQ" in result.output


def test_info_invalid_url_exits_1(container: Container) -> None:
    result = runner.invoke(app, ["info", "https://vimeo.com/1"], obj=container)
    assert result.exit_code == 1
    assert "Error" in result.output


def test_download_video_default_resolution_from_settings(
    container: Container, youtube: FakeYouTubeProvider
) -> None:
    result = runner.invoke(app, ["download-video", VIDEO_URL], obj=container)
    assert result.exit_code == 0, result.output
    assert youtube.calls == [("video:lowest", "dQw4w9WgXcQ")]
    assert ".mp4" in result.output


def test_download_video_audio_only_mp3_by_default(
    container: Container, youtube: FakeYouTubeProvider
) -> None:
    result = runner.invoke(app, ["download-video", "--audio-only", VIDEO_URL], obj=container)
    assert result.exit_code == 0, result.output
    assert youtube.calls == [("audio", "dQw4w9WgXcQ")]
    assert ".mp3" in result.output


def test_download_video_audio_only_no_mp3(container: Container) -> None:
    result = runner.invoke(
        app, ["download-video", "--audio-only", "--no-mp3", VIDEO_URL], obj=container
    )
    assert result.exit_code == 0, result.output
    assert ".m4a" in result.output


def test_download_video_rejects_bad_resolution(container: Container) -> None:
    result = runner.invoke(app, ["download-video", "-r", "4k", VIDEO_URL], obj=container)
    assert result.exit_code == 2  # typer usage error


def test_download_video_rejects_bad_bitrate(container: Container) -> None:
    result = runner.invoke(
        app, ["download-video", "--audio-only", "-b", "lots", VIDEO_URL], obj=container
    )
    assert result.exit_code == 1
    assert "bitrate" in result.output.lower()


def test_download_video_rejects_playlist_url(container: Container) -> None:
    result = runner.invoke(app, ["download-video", PLAYLIST_URL], obj=container)
    assert result.exit_code == 1


def test_download_playlist_default_is_audio_async(
    container: Container, youtube: FakeYouTubeProvider
) -> None:
    result = runner.invoke(app, ["download-playlist", PLAYLIST_URL], obj=container)
    assert result.exit_code == 0, result.output
    assert sorted(youtube.calls) == sorted(("audio", v.id) for v in VIDEOS)
    assert "3/3" in result.output


def test_download_playlist_no_async_is_sequential(
    container: Container, youtube: FakeYouTubeProvider
) -> None:
    youtube.work_seconds = 0.01
    result = runner.invoke(app, ["download-playlist", "--no-async", PLAYLIST_URL], obj=container)
    assert result.exit_code == 0, result.output
    assert youtube.peak_concurrency == 1


def test_download_playlist_partial_failure_exits_0_and_lists_failures(
    container: Container, youtube: FakeYouTubeProvider
) -> None:
    youtube.fail_ids = frozenset({VIDEOS[0].id})
    result = runner.invoke(app, ["download-playlist", PLAYLIST_URL], obj=container)
    assert result.exit_code == 0, result.output
    assert "2/3" in result.output
    assert VIDEOS[0].id in result.output


def test_download_playlist_total_failure_exits_1(
    container: Container, youtube: FakeYouTubeProvider
) -> None:
    youtube.fail_ids = frozenset(v.id for v in VIDEOS)
    result = runner.invoke(app, ["download-playlist", PLAYLIST_URL], obj=container)
    assert result.exit_code == 1


def test_output_is_safe_on_cp1252_console(
    container: Container, youtube: FakeYouTubeProvider
) -> None:
    """Windows consoles without UTF-8 must not crash the final report (no emoji)."""
    strict_cp1252 = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", errors="strict")
    cp1252_container = dataclasses.replace(
        container, console=Console(file=strict_cp1252, force_terminal=False, width=200)
    )
    youtube.fail_ids = frozenset({VIDEOS[0].id})
    single = runner.invoke(app, ["download-video", VIDEO_URL], obj=cp1252_container)
    batch = runner.invoke(app, ["download-playlist", PLAYLIST_URL], obj=cp1252_container)
    assert single.exception is None, single.output
    assert batch.exception is None, batch.output
    assert single.exit_code == 0
    assert batch.exit_code == 0


@pytest.mark.parametrize(
    "args", [["download-video", VIDEO_URL], ["download-playlist", PLAYLIST_URL]]
)
def test_progress_session_is_opened_and_closed_once_per_command(
    container: Container, args: list[str]
) -> None:
    result = runner.invoke(app, args, obj=container)
    assert result.exit_code == 0, result.output
    progress = container.progress
    assert isinstance(progress, RecordingProgress)
    assert progress.entered == 1
    assert progress.exited == 1


def test_output_flag_overrides_settings_dir(container: Container, tmp_path: Path) -> None:
    custom = tmp_path / "custom"
    result = runner.invoke(app, ["download-video", "-o", str(custom), VIDEO_URL], obj=container)
    assert result.exit_code == 0, result.output
    assert (custom / "dQw4w9WgXcQ.mp4").exists()
    assert str(custom.resolve()) in result.output


def test_batch_size_flag_bounds_concurrency(
    container: Container, youtube: FakeYouTubeProvider
) -> None:
    youtube.work_seconds = 0.01
    result = runner.invoke(
        app, ["download-playlist", "--batch-size", "1", PLAYLIST_URL], obj=container
    )
    assert result.exit_code == 0, result.output
    assert youtube.peak_concurrency == 1


def test_debug_flag_is_accepted(container: Container) -> None:
    result = runner.invoke(app, ["--debug", "info", VIDEO_URL], obj=container)
    assert result.exit_code == 0, result.output
