"""Port for the few filesystem operations use cases need."""

from pathlib import Path
from typing import Protocol


class FilesystemPort(Protocol):
    """Directory creation and file deletion."""

    def ensure_dir(self, path: Path) -> Path:
        """Create `path` (and parents) if missing; return it resolved."""
        ...

    def delete(self, path: Path) -> None:
        """Remove a file; missing file is not an error."""
        ...
