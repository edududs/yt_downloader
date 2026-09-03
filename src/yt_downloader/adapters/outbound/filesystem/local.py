"""pathlib-backed FilesystemPort."""

from pathlib import Path


class LocalFilesystem:
    """Local disk."""

    def ensure_dir(self, path: Path) -> Path:
        """Create the directory tree and return the resolved path."""
        resolved = path.resolve()
        resolved.mkdir(parents=True, exist_ok=True)
        return resolved

    def delete(self, path: Path) -> None:
        """Unlink; a missing file is fine."""
        path.unlink(missing_ok=True)
