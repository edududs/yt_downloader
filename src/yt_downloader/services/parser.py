"""URL parsing utilities for YouTube videos and playlists."""

import re
from typing import Literal
from urllib.parse import parse_qs, urlparse


class URLParser:
    """Parser for YouTube URLs to extract video and playlist information."""

    @staticmethod
    def is_youtube_url(url: str) -> bool:
        """Check if the URL is a valid YouTube URL (video or playlist)."""
        # Check if it's a YouTube domain
        youtube_domain_pattern = r"(?:https?://)?(?:www\.)?(?:youtube\.com|youtu\.be)"
        if not re.match(youtube_domain_pattern, url, re.IGNORECASE):
            return False

        # Must be either a valid video or playlist URL
        return URLParser.is_video_url(url) or URLParser.is_playlist_url(url)

    @staticmethod
    def is_playlist_url(url: str) -> bool:
        """Check if the URL is a YouTube playlist URL."""
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        # Must have playlist parameter with valid playlist ID
        if "list" in query_params:
            playlist_id = query_params["list"][0]
            # Validate playlist ID format (PL followed by alphanumeric characters)
            if re.match(r"PL[a-zA-Z0-9_-]+", playlist_id):
                return True

        return False

    @staticmethod
    def is_video_url(url: str) -> bool:
        """Check if the URL is a YouTube video URL (not a playlist)."""
        return URLParser.extract_video_id(url) is not None and not URLParser.is_playlist_url(url)

    @staticmethod
    def extract_video_id(url: str) -> str | None:
        """Extract video ID from YouTube URL."""
        patterns = [
            r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})",
            r"(?:https?://)?youtu\.be/([a-zA-Z0-9_-]{11})",
            r"(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def extract_playlist_id(url: str) -> str | None:
        """Extract playlist ID from YouTube playlist URL."""
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        if "list" in query_params:
            playlist_id = query_params["list"][0]
            # Validate playlist ID format (PL followed by alphanumeric characters)
            if re.match(r"PL[a-zA-Z0-9_-]+", playlist_id):
                return playlist_id
        return None

    @staticmethod
    def get_url_type(url: str) -> Literal["video", "playlist", "invalid"]:
        """Determine the type of YouTube URL."""
        if not URLParser.is_youtube_url(url):
            return "invalid"
        if URLParser.is_playlist_url(url):
            return "playlist"
        return "video"
