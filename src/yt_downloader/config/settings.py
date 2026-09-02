"""Application settings (pydantic-settings). Read only by bootstrap and the CLI adapter."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from yt_downloader.domain.models import Resolution


class DownloadSettings(BaseModel):
    """Defaults for download commands (CLI flags override)."""

    model_config = ConfigDict(frozen=True)

    output_dir: Path = Field(default=Path("downloads"), description="Default output directory")
    video_resolution: Resolution = Field(
        default=Resolution.LOWEST, description="Default resolution"
    )
    batch_size: int = Field(default=10, ge=1, description="Concurrent downloads in async mode")


class AudioSettings(BaseModel):
    """Defaults for audio handling."""

    model_config = ConfigDict(frozen=True)

    convert_to_mp3: bool = Field(default=True, description="Convert audio-only downloads to MP3")
    default_bitrate: str = Field(default="128k", description="MP3 bitrate, e.g. '128k'")
    ffmpeg_path: str = Field(
        default="ffmpeg", description="ffmpeg executable (name on PATH or absolute)"
    )


class YouTubeSettings(BaseModel):
    """Which YouTube library backs the provider port."""

    model_config = ConfigDict(frozen=True)

    provider: Literal["pytubefix"] = Field(
        default="pytubefix", description="YouTube provider adapter"
    )


class Settings(BaseSettings):
    """Root settings. Env prefix YT_DOWNLOADER_, nested with '__'."""

    model_config = SettingsConfigDict(
        env_prefix="YT_DOWNLOADER_", env_nested_delimiter="__", frozen=True
    )

    download: DownloadSettings = Field(default_factory=DownloadSettings)
    audio: AudioSettings = Field(default_factory=AudioSettings)
    youtube: YouTubeSettings = Field(default_factory=YouTubeSettings)
    app_name: str = Field(default="yt-downloader")
    version: str = Field(default="0.1.0")
    debug: bool = Field(default=False)
