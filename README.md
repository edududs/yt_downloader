# yt-downloader

A modular, scalable YouTube video and audio downloader built with Python and pytubefix. Features clean architecture with support for playlists, async downloads, and automatic MP3 conversion.

## ✅ Status

- ✅ Modular architecture with clear separation of concerns
- ✅ Pydantic-based configuration system
- ✅ CLI with Typer and Rich
- ✅ URL parsing and validation
- ✅ Audio conversion with pydub
- ✅ Unit tests with pytest
- ✅ Package build and installation
- ✅ Async download support (implemented)
- ✅ Observer pattern for audio events (implemented)

## 🚧 Work in Progress

- Integration tests for full download workflows
- Playlist download functionality testing
- Performance optimization
- Error handling improvements

## Architecture

This project follows a modular architecture with clear separation of concerns:

- **config/**: Configuration management using Pydantic
- **services/**: Core business logic (downloading, URL parsing)
- **commands/**: CLI command implementations (Command pattern)
- **audio/**: Audio processing and conversion (Observer pattern)
- **tests/**: Unit and integration tests

## Installation

### From GitHub (recommended for latest version)

```bash
# Using pip
pip install git+https://github.com/edududs/yt_downloader.git

# Using uv (recommended)
uv add git+https://github.com/edududs/yt_downloader.git
```

### From source (for development)

```bash
git clone https://github.com/edududs/yt_downloader.git
cd yt_downloader
pip install -e .
```

## Usage

### Download a single video

```bash
# Download video (highest resolution)
yt-downloader download-video "https://www.youtube.com/watch?v=VIDEO_ID"

# Download video (lowest resolution)
yt-downloader download-video --resolution lowest "https://www.youtube.com/watch?v=VIDEO_ID"

# Download to specific directory
yt-downloader download-video -o ./downloads "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Download audio from video

```bash
# Download audio and convert to MP3 (default)
yt-downloader download-video --audio-only "https://www.youtube.com/watch?v=VIDEO_ID"

# Download audio without conversion
yt-downloader download-video --audio-only --no-mp3 "https://www.youtube.com/watch?v=VIDEO_ID"

# Custom bitrate
yt-downloader download-video --audio-only --bitrate 192k "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Download playlist

```bash
# Download playlist audio (async by default)
yt-downloader download-playlist "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# Download playlist videos
yt-downloader download-playlist --no-audio-only "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# Synchronous download
yt-downloader download-playlist --no-async "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

### Get URL information

```bash
yt-downloader info "https://www.youtube.com/watch?v=VIDEO_ID"
yt-downloader info "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

## Features

- **Modular Architecture**: Clean separation of concerns with packages for config, services, commands, and audio
- **Async Downloads**: High-performance playlist downloads with configurable batch sizes
- **Audio Conversion**: Automatic MP3 conversion using FFmpeg with Observer pattern
- **Rich CLI**: Beautiful command-line interface with progress indicators
- **Configuration**: Flexible settings using Pydantic with environment variable support
- **Error Handling**: Robust error handling with detailed logging
- **Type Safety**: Full type hints and Pydantic validation

## Configuration

Configure the application using environment variables:

```bash
export YT_DOWNLOADER_DOWNLOAD__OUTPUT_DIR="/path/to/downloads"
export YT_DOWNLOADER_AUDIO__DEFAULT_BITRATE="192k"
export YT_DOWNLOADER_DOWNLOAD__BATCH_SIZE=20
export YT_DOWNLOADER_DEBUG=true
```

## Requirements

- Python >= 3.12
- pytubefix >= 6.9.0

## Development

This project uses `uv` for dependency management and `uv_build` for building.

### Setup development environment

```bash
git clone https://github.com/edududs/yt_downloader.git
cd yt-downloader
uv sync --dev
```

### Build the package

```bash
uv build
```

### Run tests

```bash
uv run pytest
```

## Design Patterns

This project implements several software design patterns:

- **Command Pattern**: CLI commands are encapsulated objects
- **Observer Pattern**: Audio conversion is triggered by download events
- **Strategy Pattern**: Sync/async download strategies
- **Facade Pattern**: Each package exposes a simplified interface
- **Factory Pattern**: Component initialization through configuration

