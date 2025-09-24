"""Application settings using Pydantic."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DownloadSettings(BaseModel):
    """Settings for download operations."""

    model_config = ConfigDict(frozen=True)

    output_dir: str = Field(default="downloads", description="Default output directory")
    audio_bitrate: str = Field(default="128k", description="Default audio bitrate")
    video_resolution: Literal["lowest", "highest"] = Field(
        default="lowest", description="Default video resolution"
    )
    batch_size: int = Field(default=10, description="Default batch size for async operations")
    timeout: int = Field(default=30, description="Download timeout in seconds")


class AudioSettings(BaseModel):
    """Settings for audio processing."""

    model_config = ConfigDict(frozen=True)

    convert_to_mp3: bool = Field(default=True, description="Auto-convert audio to MP3")
    default_bitrate: str = Field(default="128k", description="Default MP3 bitrate")
    ffmpeg_path: str | None = Field(default=None, description="Path to FFmpeg executable")


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_prefix="YT_DOWNLOADER_",
        env_nested_delimiter="__",
        frozen=True,
    )

    # Download settings
    download: DownloadSettings = Field(default_factory=DownloadSettings)

    # Audio settings
    audio: AudioSettings = Field(default_factory=AudioSettings)

    # Application settings
    app_name: str = Field(default="yt-downloader", description="Application name")
    version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Enable debug mode")


# Global settings instance
settings = Settings()
