"""Audio processing events and observers."""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class AudioEvent:
    """Base class for audio processing events."""

    def __init__(self, event_type: str, data: dict[str, Any]):
        """Initialize event with type and data.

        Args:
            event_type: Type of the event (e.g., 'download_completed', 'conversion_started')
            data: Event data payload

        """
        self.event_type = event_type
        self.data = data


class AudioEventObserver(ABC):
    """Abstract base class for audio event observers."""

    @abstractmethod
    async def on_event(self, event: AudioEvent) -> None:
        """Handle an audio event.

        Args:
            event: The audio event to handle

        """


class AudioConverterObserver(AudioEventObserver):
    """Observer that handles audio conversion events."""

    def __init__(self, converter: "AudioConverter"):
        """Initialize with an audio converter.

        Args:
            converter: Audio converter instance

        """
        self.converter = converter

    async def on_event(self, event: AudioEvent) -> None:
        """Handle audio conversion events."""
        if event.event_type == "download_completed":
            await self._handle_download_completed(event)

    async def _handle_download_completed(self, event: AudioEvent) -> None:
        """Handle download completed event by converting to MP3."""
        input_path = event.data.get("file_path")
        output_path = event.data.get("output_path")
        bitrate = event.data.get("bitrate", "128k")

        if not input_path:
            logger.error("No file path provided in download_completed event")
            return

        try:
            logger.info(f"🎵 Auto-converting downloaded file to MP3: {input_path}")
            mp3_path = await self.converter.convert_to_mp3_async(input_path, output_path, bitrate)

            # Emit conversion completed event
            conversion_event = AudioEvent(
                "conversion_completed",
                {"original_path": input_path, "mp3_path": mp3_path, "bitrate": bitrate},
            )

            logger.info(f"✅ Auto-conversion completed: {mp3_path}")

        except Exception as e:
            logger.error(f"❌ Auto-conversion failed for {input_path}: {e}")


class AudioEventManager:
    """Manager for audio events and observers."""

    def __init__(self):
        """Initialize event manager."""
        self._observers: list[AudioEventObserver] = []

    def add_observer(self, observer: AudioEventObserver) -> None:
        """Add an observer to the event manager.

        Args:
            observer: Observer to add

        """
        self._observers.append(observer)
        logger.debug(f"Added observer: {observer.__class__.__name__}")

    def remove_observer(self, observer: AudioEventObserver) -> None:
        """Remove an observer from the event manager.

        Args:
            observer: Observer to remove

        """
        self._observers.remove(observer)
        logger.debug(f"Removed observer: {observer.__class__.__name__}")

    async def emit_event(self, event: AudioEvent) -> None:
        """Emit an event to all observers.

        Args:
            event: Event to emit

        """
        logger.debug(f"Emitting event: {event.event_type}")
        tasks = []
        for observer in self._observers:
            task = asyncio.create_task(observer.on_event(event))
            tasks.append(task)

        # Wait for all observers to handle the event
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
