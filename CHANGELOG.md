# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
