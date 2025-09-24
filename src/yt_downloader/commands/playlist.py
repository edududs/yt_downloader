"""Playlist download command implementation."""

import logging
from typing import Literal

from ..audio import AudioConverter
from ..services import YouTubeDownloader

logger = logging.getLogger(__name__)


class PlaylistCommand:
    """Command for downloading YouTube playlists."""

    def __init__(self, downloader: YouTubeDownloader | None = None):
        """Initialize playlist command.

        Args:
            downloader: YouTube downloader instance. If None, creates a new one.

        """
        self.downloader = downloader or YouTubeDownloader(audio_converter=AudioConverter())  # type: ignore[arg-type]

    def download_playlist_video(
        self,
        url: str,
        output_path: str | None = None,
        resolution: Literal["lowest", "highest"] = "lowest",
    ) -> list[str]:
        """Download videos from YouTube playlist.

        Args:
            url: YouTube playlist URL
            output_path: Output directory path
            resolution: Video resolution to download

        Returns:
            List of paths to downloaded video files

        """
        logger.info(f"Downloading playlist videos: {url}")
        return self.downloader.download_playlist_video(
            playlist_url=url, output_path=output_path, resolution=resolution
        )

    def download_playlist_audio(
        self,
        url: str,
        output_path: str | None = None,
        convert_to_mp3: bool = True,
        bitrate: str = "128k",
    ) -> list[str]:
        """Download audio from YouTube playlist.

        Args:
            url: YouTube playlist URL
            output_path: Output directory path
            convert_to_mp3: Whether to convert to MP3
            bitrate: Audio bitrate for MP3 conversion

        Returns:
            List of paths to downloaded audio files

        """
        logger.info(f"Downloading playlist audio: {url}")
        return self.downloader.download_playlist_audio(
            playlist_url=url,
            output_path=output_path,
            convert_to_mp3=convert_to_mp3,
            bitrate=bitrate,
        )

    async def download_playlist_audio_async(
        self,
        url: str,
        output_path: str | None = None,
        bitrate: str = "128k",
        batch_size: int = 10,
    ) -> tuple[list[str], str]:
        """Download audio from YouTube playlist asynchronously.

        Args:
            url: YouTube playlist URL
            output_path: Output directory path
            bitrate: Audio bitrate for MP3 conversion
            batch_size: Number of concurrent downloads per batch

        Returns:
            Tuple of (list of downloaded file paths, output directory)

        """
        logger.info(f"Downloading playlist audio asynchronously: {url}")
        return await self.downloader.download_playlist_audio_async(
            playlist_url=url, output_path=output_path, bitrate=bitrate, batch_size=batch_size
        )
