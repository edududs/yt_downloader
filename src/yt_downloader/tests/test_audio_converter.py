"""Tests for audio converter functionality."""

import tempfile
from pathlib import Path

import pytest

from yt_downloader.audio.converter import AudioConverter


class TestAudioConverter:
    """Test cases for AudioConverter class."""

    @pytest.fixture
    def converter(self):
        """Create an AudioConverter instance."""
        return AudioConverter()

    @pytest.fixture
    def sample_audio_file(self):
        """Create a temporary sample audio file for testing."""
        try:
            from pydub.generators import Sine

            # Create a simple 1-second sine wave at 440 Hz
            sine_wave = Sine(440).to_audio_segment(duration=1000)
            sine_wave = sine_wave.set_frame_rate(44100).set_channels(1)
        except ImportError:
            # Fallback if pydub.generators is not available
            from pydub import AudioSegment

            sine_wave = AudioSegment.silent(duration=1000, frame_rate=44100)
            sine_wave = sine_wave.set_channels(1)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            sine_wave.export(f.name, format="wav")
            return Path(f.name)

    def test_init(self, converter):
        """Test AudioConverter initialization."""
        assert converter is not None

    def test_convert_to_mp3_file_not_found(self, converter):
        """Test conversion with non-existent file."""
        with pytest.raises(FileNotFoundError, match="Input file not found"):
            converter.convert_to_mp3("/nonexistent/file.wav")

    def test_convert_to_mp3_success(self, converter, sample_audio_file, tmp_path):
        """Test successful MP3 conversion."""
        expected_output = tmp_path / f"{sample_audio_file.stem}.mp3"

        result = converter.convert_to_mp3(sample_audio_file, tmp_path, "128k")

        assert result == str(expected_output)
        assert expected_output.exists()
        assert expected_output.suffix == ".mp3"

        # Clean up
        sample_audio_file.unlink(missing_ok=True)
        expected_output.unlink(missing_ok=True)

    def test_convert_to_mp3_default_output(self, converter, sample_audio_file):
        """Test MP3 conversion with default output path."""
        result = converter.convert_to_mp3(sample_audio_file)

        expected_output = sample_audio_file.parent / f"{sample_audio_file.stem}.mp3"
        assert result == str(expected_output)

        # Clean up
        expected_output.unlink(missing_ok=True)
        sample_audio_file.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_convert_to_mp3_async(self, converter, sample_audio_file, tmp_path):
        """Test asynchronous MP3 conversion."""
        expected_output = tmp_path / f"{sample_audio_file.stem}.mp3"

        result = await converter.convert_to_mp3_async(sample_audio_file, tmp_path, "128k")

        assert result == str(expected_output)
        assert expected_output.exists()
        assert expected_output.suffix == ".mp3"

        # Clean up
        sample_audio_file.unlink(missing_ok=True)
        expected_output.unlink(missing_ok=True)

    def test_batch_convert_to_mp3(self, converter, sample_audio_file, tmp_path):
        """Test batch MP3 conversion."""
        # Create another sample file
        import shutil

        sample_file2 = tmp_path / "sample2.wav"
        shutil.copy2(sample_audio_file, sample_file2)

        input_files = [sample_audio_file, sample_file2]
        results = converter.batch_convert_to_mp3(input_files, tmp_path, "128k")

        assert len(results) == 2
        for result in results:
            output_file = Path(result)
            assert output_file.exists()
            assert output_file.suffix == ".mp3"
            output_file.unlink(missing_ok=True)

        # Clean up
        sample_audio_file.unlink(missing_ok=True)
        sample_file2.unlink(missing_ok=True)

    def test_batch_convert_with_invalid_file(self, converter, tmp_path):
        """Test batch conversion with invalid files."""
        valid_file = tmp_path / "valid.wav"
        # Create a simple text file to simulate invalid audio
        valid_file.write_text("not audio data")

        invalid_file = tmp_path / "nonexistent.wav"

        input_files = [str(valid_file), str(invalid_file)]
        results = converter.batch_convert_to_mp3(input_files, tmp_path, "128k")

        # Should have 0 successful conversions due to invalid files
        assert len(results) == 0

        # Clean up
        valid_file.unlink(missing_ok=True)
