"""In-memory fakes for the four outbound ports. Structural typing = the contract test."""

import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Self

from yt_downloader.application.ports.audio_converter import AudioConverterPort
from yt_downloader.application.ports.filesystem import FilesystemPort
from yt_downloader.application.ports.progress_reporter import (
    LogLevel,
    ProgressSessionPort,
    TaskId,
)
from yt_downloader.application.ports.youtube_provider import ProgressCallback, YouTubeProviderPort
from yt_downloader.domain.errors import (
    ConversionFailedError,
    ProviderError,
    StreamUnavailableError,
)
from yt_downloader.domain.models import (
    Bitrate,
    DownloadedFile,
    PlaylistInfo,
    PlaylistRef,
    Resolution,
    VideoRef,
)


@dataclass
class FakeYouTubeProvider:
    """Writes a 5-byte file per download; tracks calls and peak concurrency."""

    playlist: PlaylistInfo | None = None
    fail_ids: frozenset[str] = frozenset()
    total_bytes: int = 100
    work_seconds: float = 0.0
    calls: list[tuple[str, str]] = field(default_factory=list)
    peak_concurrency: int = 0
    _active: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def fetch_playlist(self, ref: PlaylistRef) -> PlaylistInfo:
        if self.playlist is None:
            raise ProviderError(f"fake: no playlist for {ref.id}")
        return self.playlist

    def download_audio(
        self, ref: VideoRef, dest_dir: Path, on_progress: ProgressCallback
    ) -> DownloadedFile:
        return self._download("audio", ref, dest_dir, ".m4a", on_progress)

    def download_video(
        self, ref: VideoRef, resolution: Resolution, dest_dir: Path, on_progress: ProgressCallback
    ) -> DownloadedFile:
        return self._download(f"video:{resolution}", ref, dest_dir, ".mp4", on_progress)

    def _download(
        self, kind: str, ref: VideoRef, dest_dir: Path, suffix: str, on_progress: ProgressCallback
    ) -> DownloadedFile:
        with self._lock:
            self.calls.append((kind, ref.id))
            self._active += 1
            self.peak_concurrency = max(self.peak_concurrency, self._active)
        try:
            if ref.id in self.fail_ids:
                raise StreamUnavailableError(f"fake: no stream for {ref.id}")
            if self.work_seconds:
                time.sleep(self.work_seconds)
            on_progress(self.total_bytes // 2, self.total_bytes)
            on_progress(self.total_bytes, self.total_bytes)
            path = dest_dir / f"{ref.id}{suffix}"
            path.write_bytes(b"bytes")
            return DownloadedFile(path=path, title=f"Title {ref.id}")
        finally:
            with self._lock:
                self._active -= 1


@dataclass
class FakeAudioConverter:
    """Writes '<stem>.mp3' into the destination; optionally always fails."""

    fail: bool = False
    calls: list[tuple[Path, Bitrate]] = field(default_factory=list)

    def to_mp3(self, source: Path, dest_dir: Path, bitrate: Bitrate) -> Path:
        self.calls.append((source, bitrate))
        if self.fail:
            raise ConversionFailedError(f"fake: cannot convert {source.name}")
        target = dest_dir / f"{source.stem}.mp3"
        target.write_bytes(b"mp3")
        return target


@dataclass
class FakeFilesystem:
    """Real tmp-dir operations, but records deletions."""

    deleted: list[Path] = field(default_factory=list)

    def ensure_dir(self, path: Path) -> Path:
        resolved = path.resolve()
        resolved.mkdir(parents=True, exist_ok=True)
        return resolved

    def delete(self, path: Path) -> None:
        self.deleted.append(path)
        path.unlink(missing_ok=True)


@dataclass
class TaskState:
    description: str
    total: int | None
    completed: int = 0
    done: bool = False


@dataclass
class RecordingProgress:
    """Records every port call; also a no-op context manager (ProgressSessionPort)."""

    logs: list[tuple[LogLevel, str]] = field(default_factory=list)
    tasks: dict[TaskId, TaskState] = field(default_factory=dict)
    entered: int = 0
    exited: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def __enter__(self) -> Self:
        self.entered += 1
        return self

    def __exit__(self, *exc: object) -> None:
        self.exited += 1

    def add_task(self, description: str, *, total: int | None = None) -> TaskId:
        with self._lock:
            task = TaskId(len(self.tasks))
            self.tasks[task] = TaskState(description=description, total=total)
            return task

    def update(
        self,
        task: TaskId,
        *,
        advance: int = 0,
        completed: int | None = None,
        total: int | None = None,
        description: str | None = None,
    ) -> None:
        with self._lock:
            state = self.tasks[task]
            state.completed = completed if completed is not None else state.completed + advance
            if total is not None:
                state.total = total
            if description is not None:
                state.description = description

    def complete(self, task: TaskId) -> None:
        with self._lock:
            self.tasks[task].done = True

    def log(self, message: str, *, level: LogLevel = "info") -> None:
        with self._lock:
            self.logs.append((level, message))

    def messages(self) -> list[str]:
        return [message for _, message in self.logs]


# Structural conformance — pyright fails this module if a fake drifts from its port.
_youtube: YouTubeProviderPort = FakeYouTubeProvider()
_converter: AudioConverterPort = FakeAudioConverter()
_fs: FilesystemPort = FakeFilesystem()
_progress: ProgressSessionPort = RecordingProgress()
