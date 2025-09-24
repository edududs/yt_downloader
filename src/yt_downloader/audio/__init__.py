"""Audio processing package for yt-downloader.

This package handles audio conversion and processing operations.
"""

from .converter import AudioConversionError, AudioConverter
from .interfaces import AudioConverterInterface

__all__ = ["AudioConversionError", "AudioConverter", "AudioConverterInterface"]
