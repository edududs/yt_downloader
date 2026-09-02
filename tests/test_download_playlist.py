from pathlib import Path

import pytest

from tests.fakes import FakeAudioConverter, FakeFilesystem, FakeYouTubeProvider, RecordingProgress
from yt_downloader.application.use_cases.download_media import DownloadMediaUseCase
from yt_downloader.application.use_cases.download_playlist import DownloadPlaylistUseCase
from yt_downloader.domain.errors import EmptyPlaylistError, ProviderError
from yt_downloader.domain.models import (
    AudioDownload,
    Bitrate,
    PlaylistDownloadRequest,
    PlaylistInfo,
    PlaylistRef,
    VideoRef,
)

PL = PlaylistRef(id="PLabc", url="https://www.youtube.com/playlist?list=PLabc")
VIDEOS = tuple(VideoRef(id=c * 11, url=f"https://youtu.be/{c * 11}") for c in "abcde")


def build(youtube: FakeYouTubeProvider) -> tuple[DownloadPlaylistUseCase, RecordingProgress]:
    progress = RecordingProgress()
    media = DownloadMediaUseCase(
        youtube=youtube, converter=FakeAudioConverter(), fs=FakeFilesystem(), progress=progress
    )
    return DownloadPlaylistUseCase(
        youtube=youtube, download_media=media, progress=progress
    ), progress


def request(tmp_path: Path, concurrency: int = 3) -> PlaylistDownloadRequest:
    return PlaylistDownloadRequest(PL, AudioDownload(Bitrate("128k")), tmp_path, concurrency)


async def test_all_succeed_in_playlist_order(tmp_path: Path) -> None:
    youtube = FakeYouTubeProvider(playlist=PlaylistInfo(PL, "Mix", VIDEOS))
    use_case, progress = build(youtube)
    result = await use_case.execute(request(tmp_path))
    assert [f.title for f in result.successes] == [f"Title {v.id}" for v in VIDEOS]
    assert result.failures == ()
    overall = next(iter(progress.tasks.values()))
    assert overall.total == len(VIDEOS)
    assert overall.completed == len(VIDEOS)
    assert overall.done


async def test_failures_are_collected_not_raised(tmp_path: Path) -> None:
    youtube = FakeYouTubeProvider(
        playlist=PlaylistInfo(PL, "Mix", VIDEOS), fail_ids=frozenset({VIDEOS[1].id})
    )
    use_case, _ = build(youtube)
    result = await use_case.execute(request(tmp_path))
    assert len(result.successes) == 4
    (failure,) = result.failures
    assert failure.target == VIDEOS[1]
    assert VIDEOS[1].id in failure.reason


async def test_concurrency_is_bounded(tmp_path: Path) -> None:
    youtube = FakeYouTubeProvider(playlist=PlaylistInfo(PL, "Mix", VIDEOS), work_seconds=0.05)
    use_case, _ = build(youtube)
    await use_case.execute(request(tmp_path, concurrency=2))
    assert 1 <= youtube.peak_concurrency <= 2


async def test_sequential_when_concurrency_is_one(tmp_path: Path) -> None:
    youtube = FakeYouTubeProvider(playlist=PlaylistInfo(PL, "Mix", VIDEOS), work_seconds=0.01)
    use_case, _ = build(youtube)
    await use_case.execute(request(tmp_path, concurrency=1))
    assert youtube.peak_concurrency == 1


async def test_empty_playlist_is_an_error(tmp_path: Path) -> None:
    use_case, _ = build(FakeYouTubeProvider(playlist=PlaylistInfo(PL, "Empty", ())))
    with pytest.raises(EmptyPlaylistError):
        await use_case.execute(request(tmp_path))


async def test_provider_failure_on_fetch_propagates(tmp_path: Path) -> None:
    use_case, _ = build(FakeYouTubeProvider(playlist=None))
    with pytest.raises(ProviderError):
        await use_case.execute(request(tmp_path))
