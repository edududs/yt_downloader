"""Domain value objects and request/result types.

Every type is frozen. Illegal combinations (audio + resolution, no-mp3 +
bitrate) are unrepresentable via the MediaSpec sum type.
"""

import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from .errors import InvalidBitrateError, InvalidConcurrencyError


class Resolution(StrEnum):
    """Video resolution selector. Values double as CLI choices."""

    LOWEST = "lowest"
    HIGHEST = "highest"


_BITRATE_RE = re.compile(r"^\d{2,3}k$")


@dataclass(frozen=True, slots=True)
class Bitrate:
    """MP3 bitrate such as '128k'."""

    value: str

    def __post_init__(self) -> None:
        if not _BITRATE_RE.fullmatch(self.value):
            raise InvalidBitrateError(f"Invalid bitrate {self.value!r}; expected e.g. '128k'")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class VideoRef:
    """A single YouTube video (11-char id) and the URL it was parsed from."""

    id: str
    url: str


@dataclass(frozen=True, slots=True)
class PlaylistRef:
    """A YouTube playlist (PL… id) and the URL it was parsed from."""

    id: str
    url: str


@dataclass(frozen=True, slots=True)
class VideoDownload:
    """Download the video stream at the given resolution."""

    resolution: Resolution


@dataclass(frozen=True, slots=True)
class AudioDownload:
    """Download the audio-only stream; convert to MP3 when a bitrate is given."""

    mp3_bitrate: Bitrate | None


MediaSpec = VideoDownload | AudioDownload


@dataclass(frozen=True, slots=True)
class DownloadRequest:
    """Download one video according to a MediaSpec."""

    target: VideoRef
    media: MediaSpec
    output_dir: Path


@dataclass(frozen=True, slots=True)
class PlaylistDownloadRequest:
    """Download every video of a playlist; concurrency=1 means sequential."""

    target: PlaylistRef
    media: MediaSpec
    output_dir: Path
    concurrency: int

    def __post_init__(self) -> None:
        if self.concurrency < 1:
            raise InvalidConcurrencyError(f"Concurrency must be >= 1, got {self.concurrency}")


@dataclass(frozen=True, slots=True)
class DownloadedFile:
    """A file that landed on disk, plus the video title for display."""

    path: Path
    title: str


@dataclass(frozen=True, slots=True)
class PlaylistInfo:
    """Resolved playlist metadata."""

    ref: PlaylistRef
    title: str
    videos: tuple[VideoRef, ...]


@dataclass(frozen=True, slots=True)
class DownloadFailure:
    """One video of a batch that failed, with the domain error message."""

    target: VideoRef
    reason: str


@dataclass(frozen=True, slots=True)
class BatchDownloadResult:
    """Outcome of a playlist download; order follows the playlist."""

    successes: tuple[DownloadedFile, ...]
    failures: tuple[DownloadFailure, ...]
