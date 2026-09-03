# Spec — hexagonal-refactor

Source of truth for contracts, rationale and file layout: `docs/plans/2026-09-02-hexagonal-refactor.md` (§Decisões, §Contratos, §Arquitetura alvo). This file only assigns requirement IDs and acceptance criteria so tests and the verifier can trace them.

## Global constraints (GC)

- GC-1 No `pydub`, no `yt-dlp`. Conversion via ffmpeg subprocess only inside `adapters/outbound/audio/`.
- GC-2 `pytubefix` imported only inside `adapters/outbound/youtube/`.
- GC-3 `Settings` imported only by `bootstrap/`, `config/`, `adapters/inbound/cli/`, `adapters/outbound/youtube/registry.py`.
- GC-4 Gate before every commit: `uv run ruff format . && uv run ruff check . && uv run pyright && uv run pytest -q` all green.
- GC-5 CLI keeps `download-video`, `download-playlist`, `info` and flags `-o -r --audio-only --mp3/--no-mp3 -b --batch-size --async/--no-async --debug`.
- GC-6 Use cases raise/catch only `DomainError`; adapters translate vendor exceptions.

## Requirements

### REQ-01 Domain models (Task 2)
- AC-01.1 `Bitrate("64k"|"128k"|"320k")` accepted; `str()` returns the value.
- AC-01.2 `Bitrate` rejects `"" "128" "128K" "1k" "1024k" "128kbps" "abc"` with `InvalidBitrateError`.
- AC-01.3 `Bitrate` is frozen (assignment raises `AttributeError`).
- AC-01.4 `Resolution("lowest") is LOWEST`, `Resolution("highest") is HIGHEST`.
- AC-01.5 `VideoDownload` and `AudioDownload` are distinct types; `AudioDownload(mp3_bitrate=None)` allowed.
- AC-01.6 `PlaylistDownloadRequest(concurrency=0)` raises `InvalidConcurrencyError`.

### REQ-02 URL parser (Task 3)
- AC-02.1 Video URLs (watch?v=, youtu.be/, embed/, with extra query, without scheme) → `VideoRef(id, url)`.
- AC-02.2 Playlist URLs (playlist?list=PL…, watch?v=…&list=PL…) → `PlaylistRef`; playlist wins over video.
- AC-02.3 Non-YouTube / missing id / non-PL list / short id → `InvalidUrlError`.
- AC-02.4 `parse_video_url` rejects playlist URL; `parse_playlist_url` rejects video URL (both `InvalidUrlError`).

### REQ-03 Ports + fakes (Task 4)
- AC-03.1 Fakes for all four ports plus `ProgressSessionPort` type-check against the Protocols (pyright, `tests/fakes.py` conformance assignments).

### REQ-04 LocalFilesystem (Task 5)
- AC-04.1 `ensure_dir` creates nested dirs and returns the resolved path; idempotent.
- AC-04.2 `delete` removes a file and tolerates a missing one.

### REQ-05 FfmpegConverter (Task 6)
- AC-05.1 argv: `[ffmpeg_path, …, "-i", source, …, "-b:a", bitrate, target]`, target = `dest_dir/<stem>.mp3`, returned.
- AC-05.2 Non-zero exit → `ConversionFailedError` containing stderr.
- AC-05.3 Missing binary → `ConversionFailedError` containing "not found".
- AC-05.4 (integration) real ffmpeg round-trip produces a non-empty mp3.

### REQ-06 RichProgressReporter (Task 7)
- AC-06.1 `log` at info/warn/error reaches the console inside a session.
- AC-06.2 `add_task/update(completed|advance|description)/complete` drive the Rich task (completed=total, finished).
- AC-06.3 `total` may arrive late via `update(total=)`; `complete` fills to it.
- AC-06.4 `log` works outside a session.

### REQ-07 PytubefixProvider (Task 8)
- AC-07.1 `download_audio` picks `get_audio_only`, returns `DownloadedFile(path, title)`.
- AC-07.2 `download_video(LOWEST|HIGHEST)` picks the matching stream getter.
- AC-07.3 Hook translates `(stream, chunk, bytes_remaining)` → `on_progress(filesize − remaining, filesize)`.
- AC-07.4 No stream → `StreamUnavailableError`; vendor exception → `ProviderError` with original message.
- AC-07.5 `fetch_playlist` returns title + `VideoRef`s parsed from `video_urls`.
- AC-07.6 A vendor exception raised by the lazy `YouTube.streams` property is translated to `ProviderError` on every entry point (audio, lowest, highest). (PR review P1.)

### REQ-08 Settings + registry (Task 9)
- AC-08.1 Defaults: output_dir `downloads`, resolution LOWEST, batch_size 10, convert_to_mp3 True, bitrate "128k", ffmpeg_path "ffmpeg", provider "pytubefix".
- AC-08.2 Env overrides for every nested field; invalid resolution / unknown provider / batch_size 0 → `ValidationError` naming the field.
- AC-08.3 Settings frozen; `audio_bitrate` and `timeout` fields removed.
- AC-08.4 `build_youtube_provider(YouTubeSettings())` → `PytubefixProvider`.

### REQ-09 DownloadMediaUseCase (Task 10)
- AC-09.1 Video: provider `download_video` called, converter not called, task completed.
- AC-09.2 Audio without mp3: `.m4a` kept, converter not called, nothing deleted.
- AC-09.3 Audio with mp3: converter called with `(downloaded path, bitrate)`, original deleted, result `.mp3` keeps title, "Done" logged.
- AC-09.4 Progress task ends with total=completed=bytes, description=title, done.
- AC-09.5 Conversion failure → `ConversionFailedError` raised, original NOT deleted, last log level "error".
- AC-09.6 Stream failure propagates; output dir created.

### REQ-10 DownloadPlaylistUseCase (Task 11)
- AC-10.1 All succeed → successes in playlist order, overall task total=completed=N, done.
- AC-10.2 Per-video `DomainError` → `DownloadFailure(target, reason)` collected, others succeed.
- AC-10.3 Peak concurrency ≤ `concurrency`; `concurrency=1` → peak 1.
- AC-10.4 Empty playlist → `EmptyPlaylistError`; fetch failure (`ProviderError`) propagates.

### REQ-11 Container (Task 12)
- AC-11.1 `build_container(Settings(), console)` wires RichProgressReporter + both use cases; `console` identity preserved.

### REQ-12 CLI (Task 13)
- AC-12.1 `info` prints type + id; invalid URL → exit 1 with "Error".
- AC-12.2 `download-video` default → video lowest (from settings); `--audio-only` → mp3 by default; `--no-mp3` → `.m4a`.
- AC-12.3 `-r 4k` → exit 2; `-b lots` → exit 1 mentioning bitrate; playlist URL → exit 1.
- AC-12.4 `download-playlist` default audio+async, prints "N/N"; `--no-async` → peak concurrency 1; partial failure exit 0 listing failed ids; total failure exit 1.
- AC-12.5 Progress session entered and exited exactly once per command.
- AC-12.6 Legacy `audio/ commands/ services/` deleted; ruff/pyright legacy excludes removed; GC-1..3 greps empty.
- AC-12.8 Explicit falsy option values are validated, not defaulted: `--batch-size 0` → exit 1 mentioning concurrency, no download started; `-b ""` → exit 1 mentioning bitrate. (PR review P2.)
- AC-12.7 Presenter output is encodable on a strict cp1252 console (Windows without UTF-8): `download-video` and `download-playlist` (with one failure) finish with exit 0 and no exception. (Found in manual smoke: `✅` raised UnicodeEncodeError.)

### REQ-13 Closure (Task 14)
- AC-13.1 `--cov-fail-under` = measured − 5 (rounded down to multiple of 5).
- AC-13.2 README/CHANGELOG/CONTRIBUTING updated per plan Task 14.
