import shutil
import subprocess
from pathlib import Path

import pytest

from yt_downloader.adapters.outbound.audio import ffmpeg_converter
from yt_downloader.adapters.outbound.audio.ffmpeg_converter import FfmpegConverter
from yt_downloader.application.ports.audio_converter import AudioConverterPort
from yt_downloader.domain.errors import ConversionFailedError
from yt_downloader.domain.models import Bitrate


def test_builds_argv_and_returns_target(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[list[str]] = []

    def fake_run(argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        captured.append(argv)
        return subprocess.CompletedProcess(argv, 0, "", "")

    monkeypatch.setattr(ffmpeg_converter.subprocess, "run", fake_run)
    converter: AudioConverterPort = FfmpegConverter(ffmpeg_path="/opt/ffmpeg")
    source = tmp_path / "song.m4a"

    target = converter.to_mp3(source, tmp_path, Bitrate("192k"))

    assert target == tmp_path / "song.mp3"
    (argv,) = captured
    assert argv[0] == "/opt/ffmpeg"
    assert argv[-1] == str(target)
    assert "-b:a" in argv
    assert argv[argv.index("-b:a") + 1] == "192k"
    assert argv[argv.index("-i") + 1] == str(source)


def test_nonzero_exit_becomes_conversion_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_run(argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        raise subprocess.CalledProcessError(1, argv, stderr="bad input")

    monkeypatch.setattr(ffmpeg_converter.subprocess, "run", fake_run)
    with pytest.raises(ConversionFailedError, match="bad input"):
        FfmpegConverter().to_mp3(tmp_path / "x.m4a", tmp_path, Bitrate("128k"))


def test_missing_binary_becomes_conversion_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_run(argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        raise FileNotFoundError(argv[0])

    monkeypatch.setattr(ffmpeg_converter.subprocess, "run", fake_run)
    with pytest.raises(ConversionFailedError, match="not found"):
        FfmpegConverter(ffmpeg_path="nope").to_mp3(tmp_path / "x.m4a", tmp_path, Bitrate("128k"))


@pytest.mark.integration
@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not on PATH")
def test_real_ffmpeg_roundtrip(tmp_path: Path) -> None:
    source = tmp_path / "tone.wav"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=1",
            str(source),
        ],
        check=True,
    )
    target = FfmpegConverter().to_mp3(source, tmp_path / "out", Bitrate("64k"))
    assert target.exists()
    assert target.stat().st_size > 0
