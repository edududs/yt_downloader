from pathlib import Path

import pytest

from yt_downloader.domain.errors import InvalidBitrateError, InvalidConcurrencyError
from yt_downloader.domain.models import (
    AudioDownload,
    Bitrate,
    PlaylistDownloadRequest,
    PlaylistRef,
    Resolution,
    VideoDownload,
)


@pytest.mark.parametrize("value", ["64k", "128k", "320k"])
def test_bitrate_accepts_kbps_strings(value: str) -> None:
    assert str(Bitrate(value)) == value


@pytest.mark.parametrize("value", ["", "128", "128K", "1k", "1024k", "128kbps", "abc"])
def test_bitrate_rejects_other_strings(value: str) -> None:
    with pytest.raises(InvalidBitrateError):
        Bitrate(value)


def test_bitrate_is_immutable() -> None:
    bitrate = Bitrate("128k")
    with pytest.raises(AttributeError):
        bitrate.value = "192k"  # type: ignore[misc]  # testing frozen dataclass


def test_resolution_values_match_cli_strings() -> None:
    assert Resolution("lowest") is Resolution.LOWEST
    assert Resolution("highest") is Resolution.HIGHEST


def test_media_spec_variants_are_distinct_types() -> None:
    video = VideoDownload(resolution=Resolution.LOWEST)
    audio = AudioDownload(mp3_bitrate=None)
    assert not isinstance(video, AudioDownload)
    assert audio.mp3_bitrate is None


def test_playlist_request_rejects_concurrency_below_one() -> None:
    ref = PlaylistRef(id="PLabc", url="https://www.youtube.com/playlist?list=PLabc")
    with pytest.raises(InvalidConcurrencyError):
        PlaylistDownloadRequest(
            target=ref, media=AudioDownload(mp3_bitrate=None), output_dir=Path("x"), concurrency=0
        )
