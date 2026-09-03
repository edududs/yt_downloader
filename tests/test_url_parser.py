import pytest

from yt_downloader.domain.errors import InvalidUrlError
from yt_downloader.domain.models import PlaylistRef, VideoRef
from yt_downloader.domain.url_parser import (
    parse_playlist_url,
    parse_video_url,
    parse_youtube_url,
)

VIDEO_ID = "dQw4w9WgXcQ"
PLAYLIST_ID = "PLrAXtmRdnEQy4qtr5mYJ2hBJc5VcWKvLk"


@pytest.mark.parametrize(
    "url",
    [
        f"https://www.youtube.com/watch?v={VIDEO_ID}",
        f"https://youtu.be/{VIDEO_ID}",
        f"https://youtube.com/watch?v={VIDEO_ID}",
        f"https://www.youtube.com/watch?v={VIDEO_ID}&t=30",
        f"https://youtu.be/{VIDEO_ID}?t=30",
        f"https://www.youtube.com/embed/{VIDEO_ID}",
        f"www.youtube.com/watch?v={VIDEO_ID}",
    ],
)
def test_parses_video_urls(url: str) -> None:
    ref = parse_youtube_url(url)
    assert ref == VideoRef(id=VIDEO_ID, url=url)


@pytest.mark.parametrize(
    "url",
    [
        f"https://www.youtube.com/playlist?list={PLAYLIST_ID}",
        f"https://youtube.com/playlist?list={PLAYLIST_ID}",
        f"https://www.youtube.com/watch?v={VIDEO_ID}&list={PLAYLIST_ID}",  # playlist wins
    ],
)
def test_parses_playlist_urls(url: str) -> None:
    ref = parse_youtube_url(url)
    assert ref == PlaylistRef(id=PLAYLIST_ID, url=url)


@pytest.mark.parametrize(
    "url",
    [
        "",
        "not a url",
        "https://www.google.com",
        "https://vimeo.com/123456",
        "https://youtube.com/playlist",
        "https://www.youtube.com/playlist?list=NOTAPLAYLIST",
        "https://www.youtube.com/watch?v=short",
    ],
)
def test_rejects_non_youtube_urls(url: str) -> None:
    with pytest.raises(InvalidUrlError):
        parse_youtube_url(url)


def test_parse_video_url_rejects_playlist() -> None:
    with pytest.raises(InvalidUrlError):
        parse_video_url(f"https://www.youtube.com/playlist?list={PLAYLIST_ID}")


def test_parse_playlist_url_rejects_video() -> None:
    with pytest.raises(InvalidUrlError):
        parse_playlist_url(f"https://youtu.be/{VIDEO_ID}")
