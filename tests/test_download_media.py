from pathlib import Path

import pytest

from tests.fakes import FakeAudioConverter, FakeFilesystem, FakeYouTubeProvider, RecordingProgress
from yt_downloader.application.use_cases.download_media import DownloadMediaUseCase
from yt_downloader.domain.errors import ConversionFailedError, StreamUnavailableError
from yt_downloader.domain.models import (
    AudioDownload,
    Bitrate,
    DownloadRequest,
    Resolution,
    VideoDownload,
    VideoRef,
)

REF = VideoRef(id="dQw4w9WgXcQ", url="https://youtu.be/dQw4w9WgXcQ")

World = tuple[
    DownloadMediaUseCase, FakeYouTubeProvider, FakeAudioConverter, FakeFilesystem, RecordingProgress
]


@pytest.fixture
def world() -> World:
    youtube = FakeYouTubeProvider()
    converter = FakeAudioConverter()
    fs = FakeFilesystem()
    progress = RecordingProgress()
    use_case = DownloadMediaUseCase(youtube=youtube, converter=converter, fs=fs, progress=progress)
    return use_case, youtube, converter, fs, progress


def test_video_download_skips_converter(world: World, tmp_path: Path) -> None:
    use_case, youtube, converter, _, progress = world
    result = use_case.execute(
        DownloadRequest(REF, VideoDownload(Resolution.HIGHEST), tmp_path / "out")
    )
    assert result.path.suffix == ".mp4"
    assert result.path.exists()
    assert youtube.calls == [("video:highest", REF.id)]
    assert converter.calls == []
    assert next(iter(progress.tasks.values())).done


def test_audio_without_mp3_keeps_original(world: World, tmp_path: Path) -> None:
    use_case, _, converter, fs, _ = world
    result = use_case.execute(DownloadRequest(REF, AudioDownload(mp3_bitrate=None), tmp_path))
    assert result.path.suffix == ".m4a"
    assert converter.calls == []
    assert fs.deleted == []


def test_audio_with_mp3_converts_and_deletes_original(world: World, tmp_path: Path) -> None:
    use_case, _, converter, fs, progress = world
    result = use_case.execute(DownloadRequest(REF, AudioDownload(Bitrate("192k")), tmp_path))
    assert result.path.suffix == ".mp3"
    assert result.title == f"Title {REF.id}"
    (call,) = converter.calls
    assert call == (tmp_path.resolve() / f"{REF.id}.m4a", Bitrate("192k"))
    assert fs.deleted == [tmp_path.resolve() / f"{REF.id}.m4a"]
    assert any("Done" in m for m in progress.messages())


def test_progress_task_tracks_bytes_and_title(world: World, tmp_path: Path) -> None:
    use_case, _, _, _, progress = world
    use_case.execute(DownloadRequest(REF, AudioDownload(None), tmp_path))
    (state,) = progress.tasks.values()
    assert state.total == 100
    assert state.completed == 100
    assert state.description == f"Title {REF.id}"
    assert state.done


def test_conversion_failure_raises_and_keeps_original(world: World, tmp_path: Path) -> None:
    use_case, _, converter, fs, progress = world
    converter.fail = True
    with pytest.raises(ConversionFailedError):
        use_case.execute(DownloadRequest(REF, AudioDownload(Bitrate("128k")), tmp_path))
    assert fs.deleted == []
    assert (tmp_path / f"{REF.id}.m4a").exists()
    assert progress.logs[-1][0] == "error"


def test_stream_failure_propagates(world: World, tmp_path: Path) -> None:
    use_case, youtube, _, _, _ = world
    youtube.fail_ids = frozenset({REF.id})
    with pytest.raises(StreamUnavailableError):
        use_case.execute(DownloadRequest(REF, AudioDownload(None), tmp_path))


def test_output_dir_is_created(world: World, tmp_path: Path) -> None:
    use_case, _, _, _, _ = world
    target = tmp_path / "deep" / "er"
    use_case.execute(DownloadRequest(REF, AudioDownload(None), target))
    assert target.is_dir()
