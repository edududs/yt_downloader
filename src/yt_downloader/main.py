"""Console-script entry point (see [project.scripts])."""

from yt_downloader.adapters.inbound.cli.app import app

__all__ = ["app"]

if __name__ == "__main__":
    app()
