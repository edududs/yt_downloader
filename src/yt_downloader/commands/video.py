"""Video download command implementation."""

import logging
from typing import Literal

from ..audio import AudioConverter
from ..services import YouTubeDownloader

logger = logging.getLogger(__name__)


class VideoCommand:
    """Command for downloading individual YouTube videos."""

    def __init__(self, downloader: YouTubeDownloader | None = None):
        """Initialize video command.

        Args:
            downloader: YouTube downloader instance. If None, creates a new one.

        """
        self.downloader = downloader or YouTubeDownloader(audio_converter=AudioConverter())

    def download_video(
        self,
        url: str,
        output_path: str | None = None,
        resolution: Literal["lowest", "highest"] = "lowest",
    ) -> str:
        """Download a video from YouTube.

        Args:
            url: YouTube video URL
            output_path: Output directory path
            resolution: Video resolution to download

        Returns:
            Path to the downloaded video file

        """
        logger.info(f"Downloading video: {url}")
        return self.downloader.download_video(
            video_url=url, output_path=output_path, resolution=resolution
        )

    def download_audio(
        self,
        url: str,
        output_path: str | None = None,
        convert_to_mp3: bool = True,
        bitrate: str = "128k",
    ) -> str:
        """Download audio from YouTube video.

        Args:
            url: YouTube video URL
            output_path: Output directory path
            convert_to_mp3: Whether to convert to MP3
            bitrate: Audio bitrate for MP3 conversion

        Returns:
            Path to the downloaded audio file

        """
        logger.info(f"Downloading audio: {url}")
        return self.downloader.download_audio(
            video_url=url, output_path=output_path, convert_to_mp3=convert_to_mp3, bitrate=bitrate
        )

    async def download_audio_async(
        self,
        url: str,
        output_path: str | None = None,
        convert_to_mp3: bool = True,
        bitrate: str = "128k",
    ) -> str:
        """Download audio from YouTube video asynchronously.

        Args:
            url: YouTube video URL
            output_path: Output directory path
            convert_to_mp3: Whether to convert to MP3
            bitrate: Audio bitrate for MP3 conversion

        Returns:
            Path to the downloaded audio file

        """
        logger.info(f"Downloading audio asynchronously: {url}")
        return await self.downloader.download_audio_async(
            video_url=url, output_path=output_path, convert_to_mp3=convert_to_mp3, bitrate=bitrate
        )

    async def download_and_convert_audio_event(
        self,
        url: str,
        output_path: str | None = None,
        bitrate: str = "128k",
    ) -> str:
        """Download and convert audio in a single event.

        Args:
            url: YouTube video URL
            output_path: Output directory path
            bitrate: Audio bitrate for MP3 conversion

        Returns:
            Path to the converted MP3 file

        """
        logger.info(f"Downloading and converting audio: {url}")
        return await self.downloader.download_and_convert_audio_event(
            video_url=url, output_path=output_path, bitrate=bitrate
        )
