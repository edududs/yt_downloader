from yt_downloader.adapters.outbound.youtube.pytubefix_provider import PytubefixProvider
from yt_downloader.adapters.outbound.youtube.registry import build_youtube_provider
from yt_downloader.config.settings import YouTubeSettings


def test_builds_pytubefix_by_default() -> None:
    provider = build_youtube_provider(YouTubeSettings())
    assert isinstance(provider, PytubefixProvider)
