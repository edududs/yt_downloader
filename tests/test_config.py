import os
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from yt_downloader.config.settings import Settings
from yt_downloader.domain.models import Resolution


def test_defaults() -> None:
    settings = Settings()
    assert settings.app_name == "yt-downloader"
    assert settings.debug is False
    assert settings.download.output_dir == Path("downloads")
    assert settings.download.video_resolution is Resolution.LOWEST
    assert settings.download.batch_size == 10
    assert settings.audio.convert_to_mp3 is True
    assert settings.audio.default_bitrate == "128k"
    assert settings.audio.ffmpeg_path == "ffmpeg"
    assert settings.youtube.provider == "pytubefix"


@patch.dict(os.environ, {"YT_DOWNLOADER_DEBUG": "true"})
def test_env_override_top_level() -> None:
    assert Settings().debug is True


@patch.dict(
    os.environ,
    {
        "YT_DOWNLOADER_DOWNLOAD__OUTPUT_DIR": "/custom/path",
        "YT_DOWNLOADER_DOWNLOAD__VIDEO_RESOLUTION": "highest",
        "YT_DOWNLOADER_DOWNLOAD__BATCH_SIZE": "20",
        "YT_DOWNLOADER_AUDIO__CONVERT_TO_MP3": "false",
        "YT_DOWNLOADER_AUDIO__DEFAULT_BITRATE": "192k",
        "YT_DOWNLOADER_AUDIO__FFMPEG_PATH": "/opt/ffmpeg",
        "YT_DOWNLOADER_YOUTUBE__PROVIDER": "pytubefix",
    },
)
def test_env_override_nested() -> None:
    settings = Settings()
    assert settings.download.output_dir == Path("/custom/path")
    assert settings.download.video_resolution is Resolution.HIGHEST
    assert settings.download.batch_size == 20
    assert settings.audio.convert_to_mp3 is False
    assert settings.audio.default_bitrate == "192k"
    assert settings.audio.ffmpeg_path == "/opt/ffmpeg"


@patch.dict(os.environ, {"YT_DOWNLOADER_DOWNLOAD__VIDEO_RESOLUTION": "4k"})
def test_invalid_resolution_fails_fast() -> None:
    with pytest.raises(ValidationError, match="video_resolution"):
        Settings()


@patch.dict(os.environ, {"YT_DOWNLOADER_YOUTUBE__PROVIDER": "yt-dlp"})
def test_unknown_provider_fails_fast() -> None:
    with pytest.raises(ValidationError, match="provider"):
        Settings()


@patch.dict(os.environ, {"YT_DOWNLOADER_DOWNLOAD__BATCH_SIZE": "0"})
def test_batch_size_must_be_positive() -> None:
    with pytest.raises(ValidationError, match="batch_size"):
        Settings()


def test_removed_fields_are_gone() -> None:
    settings = Settings()
    assert not hasattr(settings.download, "audio_bitrate")
    assert not hasattr(settings.download, "timeout")


def test_settings_are_frozen() -> None:
    settings = Settings()
    with pytest.raises(ValidationError):
        settings.debug = True  # type: ignore[misc]  # testing frozen model
    with pytest.raises(ValidationError):
        settings.download.batch_size = 1  # type: ignore[misc]  # testing frozen model
