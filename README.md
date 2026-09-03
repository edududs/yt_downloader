# yt-downloader

A YouTube video and audio downloader CLI built with Python, pytubefix, Typer and Rich. Hexagonal architecture (ports & adapters): the YouTube library, the audio converter, the filesystem and the progress display are all swappable adapters behind small ports.

## Features

- Download a single video (lowest/highest progressive resolution) or its audio only
- Convert audio to MP3 via **ffmpeg** at a chosen bitrate
- Download whole playlists with bounded concurrency and live progress bars
- Live Rich progress: one bar per download plus an overall playlist bar, log lines per stage
- Configuration via environment variables (pydantic-settings)
- Fully typed (`pyright` strict on `src/`), linted with `ruff` (`select = ["ALL"]`)

## Requirements

- Python >= 3.12
- **ffmpeg** on `PATH` (or set `YT_DOWNLOADER_AUDIO__FFMPEG_PATH`) — needed only for MP3 conversion

## Installation

```bash
# Using uv (recommended)
uv add git+https://github.com/edududs/yt_downloader.git

# Using pip
pip install git+https://github.com/edududs/yt_downloader.git
```

## Usage

### Download a single video

```bash
# Default resolution comes from settings (lowest)
yt-downloader download-video "https://www.youtube.com/watch?v=VIDEO_ID"

# Explicit resolution (lowest | highest)
yt-downloader download-video --resolution highest "https://www.youtube.com/watch?v=VIDEO_ID"

# Download to a specific directory
yt-downloader download-video -o ./downloads "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Download audio from a video

```bash
# Audio only, converted to MP3 (default)
yt-downloader download-video --audio-only "https://www.youtube.com/watch?v=VIDEO_ID"

# Keep the original audio container, no conversion
yt-downloader download-video --audio-only --no-mp3 "https://www.youtube.com/watch?v=VIDEO_ID"

# Custom bitrate
yt-downloader download-video --audio-only --bitrate 192k "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Download a playlist

```bash
# Playlist audio as MP3, concurrent (default)
yt-downloader download-playlist "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# Playlist videos
yt-downloader download-playlist --no-audio-only "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# Sequential download
yt-downloader download-playlist --no-async "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# Concurrency (async mode)
yt-downloader download-playlist --batch-size 5 "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

Playlist downloads never abort on a single failed video: failures are listed at the end. The command exits with code 1 only when nothing could be downloaded.

### Inspect a URL

```bash
yt-downloader info "https://www.youtube.com/watch?v=VIDEO_ID"
yt-downloader info "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

## Configuration

Environment variables (prefix `YT_DOWNLOADER_`, nested with `__`). CLI flags always win over settings.

```bash
export YT_DOWNLOADER_DOWNLOAD__OUTPUT_DIR="/path/to/downloads"   # default: downloads
export YT_DOWNLOADER_DOWNLOAD__VIDEO_RESOLUTION=highest           # lowest | highest
export YT_DOWNLOADER_DOWNLOAD__BATCH_SIZE=20                      # concurrent playlist downloads
export YT_DOWNLOADER_AUDIO__CONVERT_TO_MP3=true
export YT_DOWNLOADER_AUDIO__DEFAULT_BITRATE="192k"
export YT_DOWNLOADER_AUDIO__FFMPEG_PATH="/opt/ffmpeg/bin/ffmpeg"  # default: ffmpeg (on PATH)
export YT_DOWNLOADER_YOUTUBE__PROVIDER=pytubefix                  # only provider today
export YT_DOWNLOADER_DEBUG=true
```

## Architecture

```
src/yt_downloader/
├── domain/        models (frozen), errors, url_parser — no dependencies
├── application/
│   ├── ports/     Protocols: YouTubeProviderPort, AudioConverterPort, FilesystemPort, ProgressReporterPort
│   └── use_cases/ DownloadMediaUseCase, DownloadPlaylistUseCase
├── adapters/
│   ├── inbound/cli/     Typer app, presenters, logging
│   └── outbound/        youtube/pytubefix_provider + registry, audio/ffmpeg_converter,
│                        filesystem/local, progress/rich_reporter
├── bootstrap/     container.py — the only place that names concrete adapters
└── config/        pydantic-settings
```

Rules: adapters implement ports; use cases know only ports and `DomainError`; every vendor exception is translated at the adapter boundary. Swapping the YouTube library means one adapter module plus one entry in `adapters/outbound/youtube/registry.py`.

## Development

```bash
git clone https://github.com/edududs/yt_downloader.git
cd yt_downloader
uv sync            # installs the dev group (pytest, ruff, pyright)
```

Quality gate (run before every commit):

```bash
uv run ruff format . && uv run ruff check . && uv run pyright && uv run pytest
```

Integration tests (real ffmpeg, real network) are skipped by default:

```bash
uv run pytest -m integration
```

Build the package:

```bash
uv build
```
