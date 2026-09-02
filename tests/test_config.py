# pylint: disable=no-member
"""Tests for configuration settings."""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from yt_downloader.config.settings import Settings


class TestSettings:
    """Test cases for Settings class."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()

        assert settings.app_name == "yt-downloader"
        assert settings.version == "0.1.0"
        assert settings.debug is False

        assert settings.download.output_dir == "downloads"
        assert settings.download.audio_bitrate == "128k"
        assert settings.download.video_resolution == "lowest"
        assert settings.download.batch_size == 10
        assert settings.download.timeout == 30

        assert settings.audio.convert_to_mp3 is True
        assert settings.audio.default_bitrate == "128k"
        assert settings.audio.ffmpeg_path is None

    @patch.dict(os.environ, {"YT_DOWNLOADER_APP_NAME": "custom-downloader"})
    def test_env_override_app_name(self):
        """Test environment variable override for app name."""
        settings = Settings()
        assert settings.app_name == "custom-downloader"

    @patch.dict(os.environ, {"YT_DOWNLOADER_DEBUG": "true"})
    def test_env_override_debug(self):
        """Test environment variable override for debug."""
        settings = Settings()
        assert settings.debug is True

    @patch.dict(os.environ, {"YT_DOWNLOADER_DOWNLOAD__OUTPUT_DIR": "/custom/path"})
    def test_env_override_download_output_dir(self):
        """Test environment variable override for download output directory."""
        settings = Settings()
        assert settings.download.output_dir == "/custom/path"

    @patch.dict(os.environ, {"YT_DOWNLOADER_DOWNLOAD__VIDEO_RESOLUTION": "highest"})
    def test_env_override_video_resolution(self):
        """Test environment variable override for video resolution."""
        settings = Settings()
        assert settings.download.video_resolution == "highest"

    @patch.dict(os.environ, {"YT_DOWNLOADER_AUDIO__CONVERT_TO_MP3": "false"})
    def test_env_override_convert_to_mp3(self):
        """Test environment variable override for MP3 conversion."""
        settings = Settings()
        assert settings.audio.convert_to_mp3 is False

    @patch.dict(os.environ, {"YT_DOWNLOADER_AUDIO__DEFAULT_BITRATE": "192k"})
    def test_env_override_audio_bitrate(self):
        """Test environment variable override for audio bitrate."""
        settings = Settings()
        assert settings.audio.default_bitrate == "192k"

    @patch.dict(
        os.environ,
        {
            "YT_DOWNLOADER_DOWNLOAD__BATCH_SIZE": "20",
            "YT_DOWNLOADER_DOWNLOAD__TIMEOUT": "60",
        },
    )
    def test_env_override_numeric_values(self):
        """Test environment variable override for numeric values."""
        settings = Settings()
        assert settings.download.batch_size == 20
        assert settings.download.timeout == 60

    def test_invalid_video_resolution(self):
        """Test invalid video resolution raises validation error."""
        with pytest.raises(ValueError, match="video_resolution"):
            Settings(download={"video_resolution": "invalid"})  # pyright: ignore[reportArgumentType]

    def test_settings_immutability(self):
        """Test that settings are immutable after creation."""
        settings = Settings()

        # Should not be able to modify settings directly
        with pytest.raises(ValidationError):
            settings.app_name = "new-name"

        with pytest.raises(ValidationError):
            settings.download.output_dir = "/new/path"
