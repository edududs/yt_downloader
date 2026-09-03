"""Parse YouTube URLs into VideoRef / PlaylistRef. Playlist wins when both are present."""

import re
from urllib.parse import parse_qs, urlparse

from .errors import InvalidUrlError
from .models import PlaylistRef, VideoRef

_DOMAIN_RE = re.compile(r"^(?:https?://)?(?:www\.)?(?:youtube\.com|youtu\.be)", re.IGNORECASE)
_PLAYLIST_ID_RE = re.compile(r"^PL[a-zA-Z0-9_-]+$")
_VIDEO_ID_PATTERNS = (
    re.compile(r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})"),
    re.compile(r"(?:https?://)?youtu\.be/([a-zA-Z0-9_-]{11})"),
    re.compile(r"(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})"),
)


def parse_youtube_url(url: str) -> VideoRef | PlaylistRef:
    """Return a PlaylistRef if the URL carries a playlist id, else a VideoRef.

    Raises:
        InvalidUrlError: not a YouTube domain, or neither id could be extracted.
    """
    if not _DOMAIN_RE.match(url):
        raise InvalidUrlError(f"Not a YouTube URL: {url!r}")
    playlist_id = _extract_playlist_id(url)
    if playlist_id is not None:
        return PlaylistRef(id=playlist_id, url=url)
    video_id = _extract_video_id(url)
    if video_id is not None:
        return VideoRef(id=video_id, url=url)
    raise InvalidUrlError(f"No video or playlist id found in: {url!r}")


def parse_video_url(url: str) -> VideoRef:
    """Parse a URL that must be a single video."""
    ref = parse_youtube_url(url)
    if not isinstance(ref, VideoRef):
        raise InvalidUrlError(f"Expected a video URL, got a playlist: {url!r}")
    return ref


def parse_playlist_url(url: str) -> PlaylistRef:
    """Parse a URL that must be a playlist."""
    ref = parse_youtube_url(url)
    if not isinstance(ref, PlaylistRef):
        raise InvalidUrlError(f"Expected a playlist URL, got a video: {url!r}")
    return ref


def _extract_playlist_id(url: str) -> str | None:
    values = parse_qs(urlparse(url).query).get("list")
    if not values:
        return None
    candidate = values[0]
    return candidate if _PLAYLIST_ID_RE.match(candidate) else None


def _extract_video_id(url: str) -> str | None:
    for pattern in _VIDEO_ID_PATTERNS:
        match = pattern.search(url)
        if match:
            return match.group(1)
    return None
