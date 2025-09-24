"""Audio converter implementation using pydub."""

import asyncio
import logging
from pathlib import Path
from typing import cast

from pydub import AudioSegment

logger = logging.getLogger(__name__)


class AudioConversionError(Exception):
    """Custom exception for audio conversion errors."""


class AudioConverter:
    """Audio converter using pydub for MP3 conversion."""

    SUPPORTED_INPUT_FORMATS = {".m4a", ".webm", ".mp4", ".flac", ".wav", ".ogg", ".aac"}
    SUPPORTED_OUTPUT_FORMATS = {".mp3", ".wav", ".flac", ".ogg"}

    def __init__(self):
        """Initialize the audio converter."""
        try:
            # Test if pydub is available
            AudioSegment.from_file  # noqa: B018
        except AttributeError as exc:
            raise AudioConversionError(
                "pydub is required for audio conversion. Install with: pip install pydub"
            ) from exc

    def convert_to_mp3(
        self, input_path: Path | str, output_path: Path | str | None = None, bitrate: str = "128k"
    ) -> str:
        """Convert audio file to MP3 format.

        Args:
            input_path: Path to the input audio file
            output_path: Directory where to save the MP3 file. If None, saves in input directory
            bitrate: Audio bitrate for MP3 conversion

        Returns:
            Path to the converted MP3 file

        Raises:
            FileNotFoundError: If input file doesn't exist
            AudioConversionError: If conversion fails

        """
        input_path = Path(input_path)

        if not input_path.exists():
            msg = f"Input file not found: {input_path}"
            logger.error(msg)
            raise FileNotFoundError(msg)

        # Validate input format
        if input_path.suffix.lower() not in self.SUPPORTED_INPUT_FORMATS:
            msg = f"Unsupported input format: {input_path.suffix}. Supported: {self.SUPPORTED_INPUT_FORMATS}"
            logger.error(msg)
            raise AudioConversionError(msg)

        # Determine output path
        output_path = input_path.parent if output_path is None else Path(output_path)

        # Create output directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate output filename
        input_name = input_path.stem
        output_file = output_path / f"{input_name}.mp3"

        try:
            logger.info(f"Converting {input_path} to MP3 with bitrate {bitrate}...")

            # Load audio file
            audio = AudioSegment.from_file(str(input_path))

            # Export as MP3 with high quality settings
            audio.export(
                str(output_file),
                format="mp3",
                bitrate=bitrate,
                parameters=["-q:a", "0"],  # Highest quality VBR
            )

            logger.info(f"Conversion completed: {output_file}")
            return str(output_file)

        except Exception as e:
            msg = f"Failed to convert {input_path} to MP3: {e}"
            logger.exception(msg, exc_info=e)
            raise AudioConversionError(msg) from e

    def validate_audio_file(self, file_path: Path | str) -> bool:
        """Validate if file is a valid audio file.

        Args:
            file_path: Path to the audio file

        Returns:
            True if valid audio file, False otherwise

        """
        file_path = Path(file_path)

        if not file_path.exists():
            return False

        if file_path.suffix.lower() not in self.SUPPORTED_INPUT_FORMATS:
            return False

        try:
            # Try to load the file to validate it's actually an audio file
            AudioSegment.from_file(str(file_path))
            return True
        except Exception:
            return False

    def get_audio_info(self, file_path: Path | str) -> dict:
        """Get audio file information.

        Args:
            file_path: Path to the audio file

        Returns:
            Dictionary with audio file information

        """
        file_path = Path(file_path)

        if not file_path.exists():
            msg = f"File not found: {file_path}"
            raise FileNotFoundError(msg)

        try:
            audio = AudioSegment.from_file(str(file_path))

            return {
                "duration_ms": len(audio),
                "duration_seconds": len(audio) / 1000,
                "channels": audio.channels,
                "sample_width": audio.sample_width,
                "frame_rate": audio.frame_rate,
                "file_size_bytes": file_path.stat().st_size,
                "file_size_mb": round(file_path.stat().st_size / (1024 * 1024), 2),
                "format": file_path.suffix[1:].upper(),
            }
        except Exception as e:
            msg = f"Failed to get audio info: {e}"
            raise AudioConversionError(msg) from e

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
        logger.info(
            f"Starting batch async conversion of {len(input_paths)} files with max_concurrent={max_concurrent}"
        )

        # Create semaphore to control concurrency
        semaphore = asyncio.Semaphore(max_concurrent)

        async def convert_with_semaphore(input_path: Path | str) -> str:
            """Convert a single file with semaphore control."""
            async with semaphore:
                logger.info(f"Converting {input_path}...")
                try:
                    result = await self.convert_to_mp3_async(input_path, output_path, bitrate)
                    logger.info(f"✅ Converted {input_path} -> {result}")
                    return result
                except Exception as e:
                    msg = f"Failed to convert {input_path}: {e}"
                    logger.exception(f"❌ {msg}", exc_info=e)
                    raise AudioConversionError(msg) from e

        # Create tasks for all conversions
        tasks = [convert_with_semaphore(path) for path in input_paths]

        try:
            # Execute all tasks concurrently with controlled concurrency
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle exceptions and collect successful results
            successful_results = []
            exceptions = []

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    exceptions.append((input_paths[i], result))
                else:
                    successful_results.append(result)

            # Log summary
            logger.info(
                f"Batch conversion completed: {len(successful_results)}/{len(input_paths)} successful"
            )

            if exceptions:
                logger.warning(f"Failed conversions: {len(exceptions)}")
                for path, exc in exceptions:
                    logger.warning(f"  - {path}: {exc}")

            return cast("list[str]", successful_results)

        except Exception as e:
            msg = f"Batch conversion failed: {e}"
            logger.exception(msg, exc_info=e)
            raise AudioConversionError(msg) from e

    async def convert_to_mp3_async(
        self, input_path: Path | str, output_path: Path | str | None = None, bitrate: str = "128k"
    ) -> str:
        """Convert audio file to MP3 format asynchronously."""
        # Execute conversion in thread pool to avoid blocking
        return await asyncio.to_thread(
            self.convert_to_mp3,
            input_path=input_path,
            output_path=output_path,
            bitrate=bitrate,
        )

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
        converted_paths = []
        for input_path in input_paths:
            try:
                converted_path = self.convert_to_mp3(input_path, output_path, bitrate)
                converted_paths.append(converted_path)
            except Exception:
                logger.exception(f"Failed to convert {input_path}")
                # Continue with other files
                continue

        return converted_paths
