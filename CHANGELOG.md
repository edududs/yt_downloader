# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Hexagonal restructure: `domain` / `application` (ports + use cases) / `adapters` / `bootstrap`. CLI commands and flags are unchanged.
- MP3 conversion now shells out to `ffmpeg` directly; `pydub` removed (it imports `audioop`, gone in Python 3.13).
- Live Rich progress bars with per-stage log lines; playlists show one bar per video plus an overall bar.
- Playlist concurrency is a semaphore (`--batch-size` = max concurrent) instead of sequential batches.
- Dependencies upgraded: pytubefix 10, typer 0.27, rich 15, pydantic 2.13, pytest 9.
- Dev tooling: `ruff` (`select = ["ALL"]`), `pyright` strict on `src/`, tests moved to `tests/`, coverage gate 90%.

### Fixed
- Final report no longer crashes on Windows consoles without UTF-8 (emoji removed from output).

### Removed
- Settings `download.audio_bitrate` (duplicate, never read) and `download.timeout` (never read).
- Unused observer/event module and the `commands/` pass-through layer.

### Breaking
- A failed MP3 conversion now errors (the original file is kept) instead of a silent warning.
- `download-playlist` exits with code 1 when no video could be downloaded.
- `--resolution` validates `lowest|highest` at parse time.

## [0.1.0] - 2024-12-XX

### Added
- Initial release of yt-downloader
- Support for downloading individual YouTube videos
- Support for downloading YouTube playlists
- Audio conversion to MP3 format
- Async download support for better performance
- CLI interface using Typer
- Rich progress indicators
- Configuration management with Pydantic
- Comprehensive test suite

### Features
- Download videos in lowest or highest resolution
- Convert audio to MP3 with custom bitrate
- Batch download from playlists with concurrency control
- Configurable output directories
- Debug mode support

### Technical
- Built with Python 3.12+
- Uses modern async/await patterns
- Type hints throughout codebase
- Comprehensive error handling
- Modular architecture with clean separation of concerns
