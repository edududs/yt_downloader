"""Port for audio transcoding."""

from pathlib import Path
from typing import Protocol

from yt_downloader.domain.models import Bitrate


class AudioConverterPort(Protocol):
    """Transcode `source` into `<dest_dir>/<source.stem>.mp3`; raise ConversionFailedError."""

    def to_mp3(self, source: Path, dest_dir: Path, bitrate: Bitrate) -> Path:
        """Return the mp3 path; leave `source` untouched; raise ConversionFailedError."""
        ...
