"""Audio converter interfaces."""

from abc import ABC, abstractmethod
from pathlib import Path


class AudioConverterInterface(ABC):
    """Interface for audio conversion operations."""

    @abstractmethod
    def convert_to_mp3(
        self, input_path: Path | str, output_path: Path | str | None = None, bitrate: str = "128k"
    ) -> str:
        """Convert audio file to MP3 format.

        Args:
            input_path: Path to the input audio file
            output_path: Directory path where the MP3 file will be saved
            bitrate: Audio bitrate for MP3 conversion

        Returns:
            Path to the converted MP3 file

        """

    @abstractmethod
    async def convert_to_mp3_async(
        self, input_path: Path | str, output_path: Path | str | None = None, bitrate: str = "128k"
    ) -> str:
        """Convert audio file to MP3 format asynchronously.

        Args:
            input_path: Path to the input audio file
            output_path: Directory path where the MP3 file will be saved
            bitrate: Audio bitrate for MP3 conversion

        Returns:
            Path to the converted MP3 file

        """

    @abstractmethod
    async def batch_convert_to_mp3_async(
        self,
        input_paths: list[Path | str],
        output_path: Path | str,
        bitrate: str = "128k",
        max_concurrent: int = 3,
    ) -> list[str]:
        """Convert multiple audio files to MP3 asynchronously with concurrency control.

        Args:
            input_paths: List of paths to input audio files
            output_path: Directory where to save the MP3 files
            bitrate: Audio bitrate for MP3 conversion
            max_concurrent: Maximum number of concurrent conversions

        Returns:
            List of paths to the converted MP3 files

        Raises:
            AudioConversionError: If any conversion fails

        """

    @abstractmethod
    def batch_convert_to_mp3(
        self,
        input_paths: list[Path | str],
        output_path: Path | str | None = None,
        bitrate: str = "128k",
    ) -> list[str]:
        """Convert multiple audio files to MP3 format.

        Args:
            input_paths: List of paths to input audio files
            output_path: Directory path where the MP3 files will be saved
            bitrate: Audio bitrate for MP3 conversion

        Returns:
            List of paths to the converted MP3 files

        """
