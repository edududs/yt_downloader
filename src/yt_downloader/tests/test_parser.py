"""Tests for URL parser functionality."""

from yt_downloader.services.parser import URLParser


class TestURLParser:
    """Test cases for URLParser class."""

    def test_is_youtube_url_valid(self):
        """Test valid YouTube URLs."""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30",
            "https://youtu.be/dQw4w9WgXcQ?t=30",
        ]

        for url in valid_urls:
            assert URLParser.is_youtube_url(url), f"Failed for URL: {url}"

    def test_is_youtube_url_invalid(self):
        """Test invalid YouTube URLs."""
        invalid_urls = [
            "https://www.google.com",
            "https://vimeo.com/123456",
            "not-a-url",
            "https://youtube.com/playlist",  # Missing parameters
        ]

        for url in invalid_urls:
            assert not URLParser.is_youtube_url(url), f"Failed for URL: {url}"

    def test_is_playlist_url_valid(self):
        """Test valid playlist URLs."""
        valid_playlist_urls = [
            "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy4qtr5mYJ2hBJc5VcWKvLk",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmRdnEQy4qtr5mYJ2hBJc5VcWKvLk",
            "https://youtube.com/playlist?list=PLrAXtmRdnEQy4qtr5mYJ2hBJc5VcWKvLk",
        ]

        for url in valid_playlist_urls:
            assert URLParser.is_playlist_url(url), f"Failed for URL: {url}"

    def test_is_playlist_url_invalid(self):
        """Test invalid playlist URLs."""
        invalid_playlist_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Regular video
            "https://youtu.be/dQw4w9WgXcQ",  # Regular video
            "https://www.youtube.com/playlist",  # Missing list parameter
        ]

        for url in invalid_playlist_urls:
            assert not URLParser.is_playlist_url(url), f"Failed for URL: {url}"

    def test_is_video_url_valid(self):
        """Test valid video URLs."""
        valid_video_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
        ]

        for url in valid_video_urls:
            assert URLParser.is_video_url(url), f"Failed for URL: {url}"

    def test_is_video_url_invalid(self):
        """Test invalid video URLs."""
        invalid_video_urls = [
            "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy4qtr5mYJ2hBJc5VcWKvLk",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmRdnEQy4qtr5mYJ2hBJc5VcWKvLk",
            "https://www.google.com",
        ]

        for url in invalid_video_urls:
            assert not URLParser.is_video_url(url), f"Failed for URL: {url}"

    def test_extract_video_id(self):
        """Test video ID extraction."""
        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtube.com/watch?v=dQw4w9WgXcQ&t=30", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ]

        for url, expected_id in test_cases:
            assert URLParser.extract_video_id(url) == expected_id, f"Failed for URL: {url}"

    def test_extract_video_id_invalid(self):
        """Test video ID extraction with invalid URLs."""
        invalid_urls = [
            "https://www.google.com",
            "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy4qtr5mYJ2hBJc5VcWKvLk",
            "not-a-url",
        ]

        for url in invalid_urls:
            assert URLParser.extract_video_id(url) is None, f"Failed for URL: {url}"

    def test_extract_playlist_id(self):
        """Test playlist ID extraction."""
        test_cases = [
            (
                "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy4qtr5mYJ2hBJc5VcWKvLk",
                "PLrAXtmRdnEQy4qtr5mYJ2hBJc5VcWKvLk",
            ),
            (
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmRdnEQy4qtr5mYJ2hBJc5VcWKvLk",
                "PLrAXtmRdnEQy4qtr5mYJ2hBJc5VcWKvLk",
            ),
        ]

        for url, expected_id in test_cases:
            assert URLParser.extract_playlist_id(url) == expected_id, f"Failed for URL: {url}"

    def test_extract_playlist_id_invalid(self):
        """Test playlist ID extraction with invalid URLs."""
        invalid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/playlist",  # Missing list parameter
            "https://www.google.com",
        ]

        for url in invalid_urls:
            assert URLParser.extract_playlist_id(url) is None, f"Failed for URL: {url}"

    def test_get_url_type(self):
        """Test URL type determination."""
        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "video"),
            ("https://youtu.be/dQw4w9WgXcQ", "video"),
            (
                "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy4qtr5mYJ2hBJc5VcWKvLk",
                "playlist",
            ),
            (
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmRdnEQy4qtr5mYJ2hBJc5VcWKvLk",
                "playlist",
            ),
            ("https://www.google.com", "invalid"),
            ("not-a-url", "invalid"),
        ]

        for url, expected_type in test_cases:
            assert URLParser.get_url_type(url) == expected_type, f"Failed for URL: {url}"
