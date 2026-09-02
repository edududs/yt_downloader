from pathlib import Path

from yt_downloader.adapters.outbound.filesystem.local import LocalFilesystem
from yt_downloader.application.ports.filesystem import FilesystemPort


def test_ensure_dir_creates_nested_and_returns_resolved(tmp_path: Path) -> None:
    fs: FilesystemPort = LocalFilesystem()
    target = tmp_path / "a" / "b"
    result = fs.ensure_dir(target)
    assert result == target.resolve()
    assert result.is_dir()


def test_ensure_dir_is_idempotent(tmp_path: Path) -> None:
    fs = LocalFilesystem()
    fs.ensure_dir(tmp_path / "x")
    fs.ensure_dir(tmp_path / "x")
    assert (tmp_path / "x").is_dir()


def test_delete_removes_file_and_tolerates_missing(tmp_path: Path) -> None:
    fs = LocalFilesystem()
    file = tmp_path / "f.txt"
    file.write_text("x")
    fs.delete(file)
    assert not file.exists()
    fs.delete(file)  # no raise
