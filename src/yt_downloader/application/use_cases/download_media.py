"""Download one video or its audio, optionally transcoding to MP3."""

from pathlib import Path
from typing import assert_never

from yt_downloader.application.ports.audio_converter import AudioConverterPort
from yt_downloader.application.ports.filesystem import FilesystemPort
from yt_downloader.application.ports.progress_reporter import ProgressReporterPort, TaskId
from yt_downloader.application.ports.youtube_provider import ProgressCallback, YouTubeProviderPort
from yt_downloader.domain.errors import DomainError
from yt_downloader.domain.models import (
    AudioDownload,
    DownloadedFile,
    DownloadRequest,
    MediaSpec,
    VideoDownload,
)


class DownloadMediaUseCase:
    """Blocking. Playlist use case runs it in worker threads."""

    def __init__(
        self,
        *,
        youtube: YouTubeProviderPort,
        converter: AudioConverterPort,
        fs: FilesystemPort,
        progress: ProgressReporterPort,
    ) -> None:
        self._youtube = youtube
        self._converter = converter
        self._fs = fs
        self._progress = progress

    def execute(self, request: DownloadRequest) -> DownloadedFile:
        """Ensure dir → download → (convert + delete original) → report."""
        dest = self._fs.ensure_dir(request.output_dir)
        task = self._progress.add_task(request.target.id)

        def on_progress(done: int, total: int) -> None:
            self._progress.update(task, completed=done, total=total)

        try:
            downloaded = self._download(request, dest, on_progress)
            self._progress.update(task, description=downloaded.title)
            result = self._postprocess(downloaded, request.media, dest, task)
        except DomainError as exc:
            self._progress.log(f"{request.target.id}: {exc}", level="error")
            raise
        self._progress.complete(task)
        self._progress.log(f"Done: {result.path}")
        return result

    def _download(
        self, request: DownloadRequest, dest: Path, on_progress: ProgressCallback
    ) -> DownloadedFile:
        match request.media:
            case VideoDownload(resolution=resolution):
                self._progress.log(f"Downloading video {request.target.id} ({resolution})")
                return self._youtube.download_video(request.target, resolution, dest, on_progress)
            case AudioDownload():
                self._progress.log(f"Downloading audio {request.target.id}")
                return self._youtube.download_audio(request.target, dest, on_progress)
            case _:
                assert_never(request.media)

    def _postprocess(
        self, downloaded: DownloadedFile, media: MediaSpec, dest: Path, task: TaskId
    ) -> DownloadedFile:
        if not isinstance(media, AudioDownload) or media.mp3_bitrate is None:
            return downloaded
        self._progress.update(
            task, description=f"Converting {downloaded.title} → mp3 ({media.mp3_bitrate})"
        )
        mp3 = self._converter.to_mp3(downloaded.path, dest, media.mp3_bitrate)
        self._fs.delete(downloaded.path)
        return DownloadedFile(path=mp3, title=downloaded.title)
