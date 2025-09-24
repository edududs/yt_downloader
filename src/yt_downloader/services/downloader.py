"""YouTube video and audio downloader service."""

import asyncio
import logging
from pathlib import Path
from typing import Any, Callable, Literal, Optional, cast

from pytubefix import YouTube
from pytubefix.cli import on_progress
from pytubefix.contrib.playlist import Playlist

from ..audio.interfaces import AudioConverterInterface
from ..config.settings import settings

logger = logging.getLogger(__name__)


class YouTubeDownloader:
    """YouTube video and audio downloader using pytubefix."""

    def __init__(
        self,
        progress_callback: Callable[[Any, bytes, int], None] | None = None,
        audio_converter: AudioConverterInterface | None = None,
    ):
        """Initialize the downloader with optional progress callback and audio converter.

        Args:
            progress_callback: Callback function for download progress tracking.
                             Defaults to pytubefix's built-in progress handler.
            audio_converter: Optional audio converter for MP3 conversion.
                           If None, MP3 conversion features will be disabled.

        """
        self.progress_callback = progress_callback or on_progress
        self.audio_converter = audio_converter

    def download_audio(
        self,
        video_url: str,
        output_path: Path | str | None = None,
        convert_to_mp3: Optional[bool] = None,
        bitrate: Optional[str] = None,
    ) -> str:
        """Download audio-only stream from YouTube video.

        Args:
            video_url: YouTube video URL
            output_path: Directory path where the audio file will be saved
            convert_to_mp3: If True, converts the downloaded file to MP3 format
            bitrate: Audio bitrate for MP3 conversion

        Returns:
            Path to the downloaded audio file

        Raises:
            ValueError: If audio conversion is requested but no converter is available

        """
        if convert_to_mp3 is None:
            convert_to_mp3 = settings.audio.convert_to_mp3  # type: ignore[attr-defined]
        if bitrate is None:
            bitrate = settings.audio.default_bitrate  # type: ignore[attr-defined]
        if output_path is None:
            output_path = settings.download.output_dir  # type: ignore[attr-defined]

        logger.info(f"Starting audio download from: {video_url}")
        yt = YouTube(video_url, on_progress_callback=self.progress_callback)
        audio_stream = yt.streams.get_audio_only()

        if not audio_stream:
            msg = f"No audio stream available for video: {video_url}"
            logger.error(msg)
            raise ValueError(msg)

        audio_stream.download(output_path=output_path)  # type: ignore[attr-defined]
        downloaded_path = Path(output_path).resolve() / audio_stream.default_filename
        logger.info(f"Audio download completed: {downloaded_path}")

        # Convert to MP3 if requested
        if convert_to_mp3:
            if self.audio_converter is None:
                msg = "MP3 conversion requested but no audio converter available."
                logger.error(msg)
                raise ValueError(msg)

            try:
                logger.info("Converting downloaded audio to MP3...")
                mp3_path = self.audio_converter.convert_to_mp3(
                    downloaded_path, output_path, bitrate
                )
                # Remove original file
                downloaded_path.unlink(missing_ok=True)
                logger.info(f"Original file removed: {downloaded_path}")
                return mp3_path
            except Exception as e:
                logger.warning(f"Failed to convert to MP3, keeping original file: {e}")
                return str(downloaded_path)

        return str(downloaded_path)

    def download_video(
        self,
        video_url: str,
        output_path: Path | str | None = None,
        resolution: Optional[Literal["lowest", "highest"]] = None,
    ) -> str:
        """Download video stream from YouTube.

        Args:
            video_url: YouTube video URL
            output_path: Directory path where the video file will be saved
            resolution: Resolution of the video stream to download

        Returns:
            Path to the downloaded video file

        Raises:
            ValueError: If no video stream is available

        """
        if resolution is None:
            resolution = settings.download.video_resolution  # type: ignore[attr-defined]
        if output_path is None:
            output_path = settings.download.output_dir  # type: ignore[attr-defined]

        logger.info(f"Starting video download from: {video_url}")
        yt = YouTube(video_url, on_progress_callback=self.progress_callback)
        video_stream = (
            yt.streams.get_lowest_resolution()
            if resolution == "lowest"
            else yt.streams.get_highest_resolution()
        )

        if not video_stream:
            msg = f"No video stream available for video: {video_url}"
            logger.error(msg)
            raise ValueError(msg)

        video_stream.download(output_path=output_path)  # type: ignore[attr-defined]
        downloaded_path = Path(output_path).resolve() / video_stream.default_filename
        logger.info(f"Video download completed: {downloaded_path}")
        return str(downloaded_path)

    def download_playlist_audio(
        self,
        playlist_url: str,
        output_path: Path | str | None = None,
        convert_to_mp3: Optional[bool] = None,
        bitrate: Optional[str] = None,
    ) -> list[str]:
        """Download audio from all videos in a YouTube playlist.

        Args:
            playlist_url: YouTube playlist URL
            output_path: Directory path where the audio files will be saved
            convert_to_mp3: If True, converts all downloaded files to MP3 format
            bitrate: Audio bitrate for MP3 conversion

        Returns:
            List of paths to the downloaded audio files

        Raises:
            ValueError: If playlist is empty or invalid

        """
        if convert_to_mp3 is None:
            convert_to_mp3 = settings.audio.convert_to_mp3  # type: ignore[attr-defined]
        if bitrate is None:
            bitrate = settings.audio.default_bitrate  # type: ignore[attr-defined]
        if output_path is None:
            output_path = settings.download.output_dir  # type: ignore[attr-defined]

        logger.info(f"Starting playlist audio download from: {playlist_url}")

        try:
            playlist = Playlist(playlist_url)
            logger.info(f"Found {len(playlist.video_urls)} videos in playlist: {playlist.title}")

            if len(playlist.video_urls) == 0:
                msg = f"No videos found in playlist: {playlist_url}"
                logger.error(msg)
                raise ValueError(msg)

            downloaded_paths = []

            for i, video_url in enumerate(playlist.video_urls, 1):
                try:
                    logger.info(f"Downloading audio {i}/{len(playlist.video_urls)}: {video_url}")
                    downloaded_path = self.download_audio(
                        video_url, output_path, convert_to_mp3, bitrate
                    )
                    downloaded_paths.append(downloaded_path)
                except Exception:
                    logger.exception("Failed to download audio from %s", video_url)
                    # Continue with other videos in the playlist
                    continue

            logger.info(
                "Playlist audio download completed. Downloaded %d/%d files",
                len(downloaded_paths),
                len(playlist.video_urls),
            )
            return downloaded_paths

        except Exception as e:
            msg = f"Failed to process playlist {playlist_url}: {e}"
            logger.exception("Failed to process playlist %s", playlist_url)
            raise ValueError(msg) from e

    def download_playlist_video(
        self,
        playlist_url: str,
        output_path: Path | str | None = None,
        resolution: Optional[Literal["lowest", "highest"]] = None,
    ) -> list[str]:
        """Download videos from all videos in a YouTube playlist.

        Args:
            playlist_url: YouTube playlist URL
            output_path: Directory path where the video files will be saved
            resolution: Resolution of the video streams to download

        Returns:
            List of paths to the downloaded video files

        Raises:
            ValueError: If playlist is empty or invalid

        """
        if resolution is None:
            resolution = settings.download.video_resolution  # type: ignore[attr-defined]
        if output_path is None:
            output_path = settings.download.output_dir  # type: ignore[attr-defined]

        logger.info(f"Starting playlist video download from: {playlist_url}")

        try:
            playlist = Playlist(playlist_url)
            logger.info(f"Found {len(playlist.video_urls)} videos in playlist: {playlist.title}")

            if len(playlist.video_urls) == 0:
                msg = f"No videos found in playlist: {playlist_url}"
                logger.error(msg)
                raise ValueError(msg)

            downloaded_paths = []

            for i, video_url in enumerate(playlist.video_urls, 1):
                try:
                    logger.info(f"Downloading video {i}/{len(playlist.video_urls)}: {video_url}")
                    downloaded_path = self.download_video(video_url, output_path, resolution)
                    downloaded_paths.append(downloaded_path)
                except Exception:
                    logger.exception("Failed to download video from %s", video_url)
                    # Continue with other videos in the playlist
                    continue

            logger.info(
                "Playlist video download completed. Downloaded %d/%d files",
                len(downloaded_paths),
                len(playlist.video_urls),
            )
            return downloaded_paths

        except Exception as e:
            msg = f"Failed to process playlist {playlist_url}: {e}"
            logger.exception("Failed to process playlist %s", playlist_url)
            raise ValueError(msg) from e

    async def download_audio_async(
        self,
        video_url: str,
        output_path: Path | str | None = None,
        convert_to_mp3: Optional[bool] = None,
        bitrate: Optional[str] = None,
    ) -> str:
        """Download audio-only stream from YouTube video asynchronously."""
        # Execute download in thread pool to avoid blocking
        return await asyncio.to_thread(
            self.download_audio,
            video_url=video_url,
            output_path=output_path,
            convert_to_mp3=convert_to_mp3,
            bitrate=bitrate,
        )

    async def download_playlist_audio_async(
        self,
        playlist_url: str,
        output_path: Path | str | None = None,
        bitrate: Optional[str] = None,
        batch_size: Optional[int] = None,
    ) -> tuple[list[str], str]:
        """Download and convert audio from all videos in a YouTube playlist asynchronously.

        Processes downloads in batches of specified size for better resource management.

        Args:
            playlist_url: YouTube playlist URL
            output_path: Directory path where the MP3 files will be saved
            bitrate: Audio bitrate for MP3 conversion
            batch_size: Number of concurrent downloads per batch

        Returns:
            Tuple of (list of MP3 file paths, output directory path)

        Raises:
            ValueError: If playlist is empty or invalid

        """
        if bitrate is None:
            bitrate = settings.audio.default_bitrate  # type: ignore[attr-defined]
        if batch_size is None:
            batch_size = settings.download.batch_size  # type: ignore[attr-defined]
        if output_path is None:
            output_path = settings.download.output_dir  # type: ignore[attr-defined]

        logger.info(f"🚀 Starting async playlist download from: {playlist_url}")

        try:
            # Get playlist info synchronously first
            playlist = Playlist(playlist_url)
            logger.info(f"📋 Found {len(playlist.video_urls)} videos in playlist: {playlist.title}")

            if len(playlist.video_urls) == 0:
                msg = f"No videos found in playlist: {playlist_url}"
                logger.error(msg)
                raise ValueError(msg)

            # Create output directory
            output_dir = Path(output_path).resolve()
            output_dir.mkdir(parents=True, exist_ok=True)

            # Process videos in batches
            all_downloaded_paths: list[str] = []
            total_videos = len(playlist.video_urls)

            for batch_start in range(0, total_videos, batch_size):
                batch_end = min(batch_start + batch_size, total_videos)
                batch_urls = playlist.video_urls[batch_start:batch_end]

                logger.info(
                    f"📦 Processing batch {batch_start // batch_size + 1}: videos {batch_start + 1}-{batch_end}/{total_videos}"
                )

                # Create tasks for this batch
                batch_tasks = []
                for video_url in batch_urls:
                    task = asyncio.create_task(
                        self._download_single_video_event(video_url, output_dir, bitrate)
                    )
                    batch_tasks.append(task)

                # Wait for batch to complete
                try:
                    batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

                    # Process results - filter out exceptions since we only want successful paths
                    successful_results = [
                        result for result in batch_results if not isinstance(result, Exception)
                    ]
                    # Type assertion since we filtered out exceptions
                    all_downloaded_paths.extend(cast("list[str]", successful_results))

                except Exception:
                    logger.exception("❌ Batch processing failed")
                    # Continue with next batch even if this one fails

            logger.info(
                f"✅ Playlist download completed: {len(all_downloaded_paths)}/{total_videos} files"
            )
            return all_downloaded_paths, str(output_dir)

        except Exception as e:
            msg = f"Failed to process playlist {playlist_url}: {e}"
            logger.exception(msg)
            raise ValueError(msg) from e

    async def _download_single_video_event(
        self,
        video_url: str,
        output_dir: Path,
        bitrate: str,
    ) -> str:
        """Download and convert a single video as an event (internal helper)."""
        try:
            logger.info(f"🎵 Processing: {video_url}")
            return await self.download_and_convert_audio_event(video_url, output_dir, bitrate)
        except Exception:
            logger.exception(f"❌ Failed to process video: {video_url}")
            raise

    async def download_and_convert_audio_event(
        self,
        video_url: str,
        output_path: Path | str | None = None,
        bitrate: Optional[str] = None,
    ) -> str:
        """Download audio and convert to MP3 in a single asynchronous event.

        This method combines download and conversion into one atomic operation.

        Args:
            video_url: YouTube video URL
            output_path: Directory path where the MP3 file will be saved
            bitrate: Audio bitrate for MP3 conversion

        Returns:
            Path to the converted MP3 file

        Raises:
            ValueError: If audio conversion is not available or fails

        """
        if bitrate is None:
            bitrate = settings.audio.default_bitrate  # type: ignore[attr-defined]
        if output_path is None:
            output_path = settings.download.output_dir  # type: ignore[attr-defined]

        logger.info(f"🎵 Starting download & convert event for: {video_url}")

        if self.audio_converter is None:
            msg = "MP3 conversion requested but no audio converter available."
            logger.error(msg)
            raise ValueError(msg)

        try:
            # Download audio first (without conversion)
            logger.info("📥 Downloading audio stream...")
            downloaded_path = await asyncio.to_thread(
                self._download_audio_only, video_url, output_path
            )

            # Convert to MP3
            logger.info("🔄 Converting to MP3...")
            assert self.audio_converter is not None  # Already checked above
            mp3_path = await self.audio_converter.convert_to_mp3_async(
                downloaded_path, output_path, bitrate
            )

            # Remove original file
            Path(downloaded_path).unlink(missing_ok=True)
            logger.info(f"🗑️ Original file removed: {downloaded_path}")

            logger.info(f"✅ Event completed successfully: {mp3_path}")
            return mp3_path

        except Exception:
            logger.exception(f"❌ Event failed for {video_url}")
            raise

    def _download_audio_only(self, video_url: str, output_path: Path | str | None = None) -> str:
        """Download audio-only stream without conversion (internal helper)."""
        if output_path is None:
            output_path = settings.download.output_dir  # type: ignore[attr-defined]

        logger.info(f"Downloading audio-only stream from: {video_url}")
        yt = YouTube(video_url, on_progress_callback=self.progress_callback)
        audio_stream = yt.streams.get_audio_only()

        if not audio_stream:
            msg = f"No audio stream available for video: {video_url}"
            logger.error(msg)
            raise ValueError(msg)

        audio_stream.download(output_path=output_path)  # type: ignore[attr-defined]
        downloaded_path = Path(output_path).resolve() / audio_stream.default_filename
        logger.info(f"Audio-only download completed: {downloaded_path}")
        return str(downloaded_path)
