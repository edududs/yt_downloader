"""Download every video of a playlist with bounded concurrency; collect failures."""

import asyncio

from yt_downloader.application.ports.progress_reporter import ProgressReporterPort
from yt_downloader.application.ports.youtube_provider import YouTubeProviderPort
from yt_downloader.domain.errors import DomainError, EmptyPlaylistError
from yt_downloader.domain.models import (
    BatchDownloadResult,
    DownloadedFile,
    DownloadFailure,
    DownloadRequest,
    PlaylistDownloadRequest,
    VideoRef,
)

from .download_media import DownloadMediaUseCase


class DownloadPlaylistUseCase:
    """Fan-out over DownloadMediaUseCase in threads, gated by a semaphore."""

    def __init__(
        self,
        *,
        youtube: YouTubeProviderPort,
        download_media: DownloadMediaUseCase,
        progress: ProgressReporterPort,
    ) -> None:
        self._youtube = youtube
        self._download_media = download_media
        self._progress = progress

    async def execute(self, request: PlaylistDownloadRequest) -> BatchDownloadResult:
        """Resolve playlist → download all → summarize. Per-video DomainErrors become failures."""
        self._progress.log(f"Fetching playlist {request.target.id}...")
        playlist = await asyncio.to_thread(self._youtube.fetch_playlist, request.target)
        if not playlist.videos:
            raise EmptyPlaylistError(f"Playlist {request.target.id} has no videos")
        self._progress.log(f"Found {len(playlist.videos)} videos: {playlist.title}")

        overall = self._progress.add_task(f"Playlist: {playlist.title}", total=len(playlist.videos))
        semaphore = asyncio.Semaphore(request.concurrency)

        async def run(ref: VideoRef) -> DownloadedFile | DownloadFailure:
            single = DownloadRequest(target=ref, media=request.media, output_dir=request.output_dir)
            async with semaphore:
                try:
                    return await asyncio.to_thread(self._download_media.execute, single)
                except DomainError as exc:
                    return DownloadFailure(target=ref, reason=str(exc))
                finally:
                    self._progress.update(overall, advance=1)

        outcomes = await asyncio.gather(*(run(ref) for ref in playlist.videos))
        self._progress.complete(overall)

        successes = tuple(o for o in outcomes if isinstance(o, DownloadedFile))
        failures = tuple(o for o in outcomes if isinstance(o, DownloadFailure))
        summary = f"Playlist done: {len(successes)}/{len(playlist.videos)} downloaded"
        if failures:
            summary += f", {len(failures)} failed"
        self._progress.log(summary, level="warn" if failures else "info")
        return BatchDownloadResult(successes=successes, failures=failures)
