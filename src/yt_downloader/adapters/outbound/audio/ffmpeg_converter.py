"""AudioConverterPort backed by the ffmpeg binary (no Python audio libs)."""

import subprocess
from pathlib import Path

from yt_downloader.domain.errors import ConversionFailedError
from yt_downloader.domain.models import Bitrate


class FfmpegConverter:
    """Transcode to MP3 with libmp3lame at a constant bitrate."""

    def __init__(self, ffmpeg_path: str = "ffmpeg") -> None:
        self._ffmpeg = ffmpeg_path

    def to_mp3(self, source: Path, dest_dir: Path, bitrate: Bitrate) -> Path:
        """Write `<dest_dir>/<source.stem>.mp3`; the source is left untouched."""
        dest_dir.mkdir(parents=True, exist_ok=True)
        target = dest_dir / f"{source.stem}.mp3"
        argv = [
            self._ffmpeg,
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-vn",
            "-codec:a",
            "libmp3lame",
            "-b:a",
            str(bitrate),
            str(target),
        ]
        try:
            subprocess.run(argv, check=True, capture_output=True, text=True)
        except FileNotFoundError as exc:
            raise ConversionFailedError(f"ffmpeg not found at {self._ffmpeg!r}") from exc
        except subprocess.CalledProcessError as exc:
            detail = (exc.stderr or "").strip() or f"exit code {exc.returncode}"
            raise ConversionFailedError(f"ffmpeg failed for {source.name}: {detail}") from exc
        return target
