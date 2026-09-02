"""Choose the YouTubeProviderPort implementation from settings."""

from typing import assert_never

from yt_downloader.application.ports.youtube_provider import YouTubeProviderPort
from yt_downloader.config.settings import YouTubeSettings

from .pytubefix_provider import PytubefixProvider


def build_youtube_provider(settings: YouTubeSettings) -> YouTubeProviderPort:
    """Registry: adding a provider = one adapter module + one case here + one Literal member."""
    match settings.provider:
        case "pytubefix":
            return PytubefixProvider()
        case _:
            assert_never(settings.provider)
