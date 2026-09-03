# hexagonal-refactor Validation

**Date**: 2026-09-03
**Spec**: `.specs/features/hexagonal-refactor/spec.md`
**Diff range**: `a954aad..HEAD` (branch `refactor/hexagonal-architecture`)
**Verifier**: independent sub-agent (author ≠ verifier)

Coverage was re-derived from `spec.md` under evidence-or-zero: every AC below carries a
`file:line` + the assertion expression, or it is marked as a gap. The author's own tables
were not consulted.

---

## Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| 1 Toolchain, harness, deps | ✅ Done | `a7e3294`; ruff `select=["ALL"]`, pyright `strict=["src"]`, tests moved to root `tests/` |
| 2 Domain errors + models | ✅ Done | `71cc0d3` |
| 3 Domain url_parser | ✅ Done | `8caa787` |
| 4 Ports + fakes | ✅ Done | `09e7b6a`; pyright is the test (gate exit 0) |
| 5 LocalFilesystem | ✅ Done | `93db21d` |
| 6 FfmpegConverter | ✅ Done | `1634390`; integration test green |
| 7 RichProgressReporter | ✅ Done | `af81275` |
| 8 PytubefixProvider | ✅ Done | `b2b9fdc`; integration test green (real network) |
| 9 Settings + registry | ✅ Done | `c123b64` |
| 10 DownloadMediaUseCase | ✅ Done | `df7c8a4` |
| 11 DownloadPlaylistUseCase | ✅ Done | `e685493` |
| 12 Container | ✅ Done | `cec56c7` |
| 13 CLI + main + delete legacy | ✅ Done | `2556f00` + `b31970a` (AC-12.7 cp1252 fix) |
| 14 Coverage gate + docs | ✅ Done | `1522bd2` |

All 14 rows in `tasks.md` are ✅; no blocked or partial task. Working tree clean at
verification time (`git status --short` empty before and after the sensor run).

---

## Spec-Anchored Acceptance Criteria

### Global constraints (GC)

| Criterion | Spec-defined outcome | Evidence | Result |
| --------- | -------------------- | -------- | ------ |
| GC-1 no pydub / yt-dlp; ffmpeg only in `adapters/outbound/audio/` | zero hits | `grep -rn "pydub" src tests pyproject.toml` → empty; `grep -rn "yt_dlp\|yt.dlp" src pyproject.toml` → empty (only hit is the deliberate invalid-provider string `tests/test_config.py:58`); `grep -rln "ffmpeg" src` → `adapters/outbound/audio/ffmpeg_converter.py` (subprocess) plus `bootstrap/container.py:32` and `config/settings.py:31` which only carry the path *string* | ✅ PASS |
| GC-2 `pytubefix` imported only under `adapters/outbound/youtube/` | one file | `grep -rlE "^(from\|import) pytubefix" src` → `src/yt_downloader/adapters/outbound/youtube/pytubefix_provider.py` only | ✅ PASS |
| GC-3 `Settings` imported only by bootstrap/, config/, cli/, youtube/registry.py | exactly that set | importers of `yt_downloader.config`: `bootstrap/container.py:14`, `adapters/inbound/cli/app.py:11`, `adapters/outbound/youtube/registry.py:6`, `config/__init__.py`, `config/settings.py` — no domain/application/other-adapter import | ✅ PASS |
| GC-4 gate green before every commit | all four steps exit 0 | `uv run ruff format . && uv run ruff check . && uv run pyright && uv run pytest -q` → exit 0, `87 passed, 2 deselected`, coverage 95.83% | ✅ PASS |
| GC-5 CLI keeps 3 commands + 8 flag groups | commands and flags present | commands `app.py:70,109,160`; flags `-o` `app.py:74,113`, `-r` `:76,115`, `--audio-only` `:78,118`, `--mp3/--no-mp3` `:80,121`, `-b/--bitrate` `:83,124`, `--batch-size` `:127`, `--async/--no-async` `:130`, `--debug` `:35`. CLI tests exercise `info` `test_cli.py:48`, `download-video` `:63`, `download-playlist` `:107`, `-r` `:87`, `-b` `:93`, `--audio-only` `:72`, `--no-mp3` `:80`, `--no-async` `:117` | ⚠️ Spec-precision gap — `-o/--output`, `--batch-size` and `--debug` are declared but have **no test citation** (see Gap 1) |
| GC-6 use cases raise/catch only `DomainError`; adapters translate vendor exceptions | translation at the adapter boundary, `except DomainError` in use cases | adapters translate: `pytubefix_provider.py:29-30` `except Exception as exc: raise ProviderError(...)`, `ffmpeg_converter.py:36-37` `except FileNotFoundError → ConversionFailedError`, `:38-40` `except subprocess.CalledProcessError → ConversionFailedError`. Use cases catch only domain: `download_media.py:48` `except DomainError as exc:`, `download_playlist.py:50` `except DomainError as exc: return DownloadFailure(...)`. CLI boundary `app.py:103,151,166` `except DomainError`. Asserted at `test_pytubefix_provider.py:115` `pytest.raises(ProviderError, match="bot detected")` and `test_ffmpeg_converter.py:43` `pytest.raises(ConversionFailedError, match="bad input")` | ✅ PASS |

### REQ-01 Domain models

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --------- | -------------------- | ----------------------- | ------ |
| AC-01.1 `Bitrate("64k"\|"128k"\|"320k")` accepted, `str()` returns value | the same string back | `tests/test_domain_models.py:18` — `assert str(Bitrate(value)) == value`, parametrized `["64k","128k","320k"]` at `:16` | ✅ PASS |
| AC-01.2 rejects `"" "128" "128K" "1k" "1024k" "128kbps" "abc"` | `InvalidBitrateError` | `tests/test_domain_models.py:23-24` — `pytest.raises(InvalidBitrateError): Bitrate(value)`, parametrized with exactly those 7 values at `:21` | ✅ PASS |
| AC-01.3 `Bitrate` frozen | assignment raises `AttributeError` | `tests/test_domain_models.py:29-30` — `pytest.raises(AttributeError): bitrate.value = "192k"` | ✅ PASS |
| AC-01.4 `Resolution("lowest") is LOWEST`, `("highest") is HIGHEST` | identity | `tests/test_domain_models.py:34-35` — `assert Resolution("lowest") is Resolution.LOWEST` / `... is Resolution.HIGHEST` | ✅ PASS |
| AC-01.5 `VideoDownload`/`AudioDownload` distinct; `mp3_bitrate=None` allowed | distinct types, None accepted | `tests/test_domain_models.py:41-42` — `assert not isinstance(video, AudioDownload)`; `assert audio.mp3_bitrate is None` | ✅ PASS |
| AC-01.6 `PlaylistDownloadRequest(concurrency=0)` | `InvalidConcurrencyError` | `tests/test_domain_models.py:47-50` — `pytest.raises(InvalidConcurrencyError)` around `PlaylistDownloadRequest(..., concurrency=0)` | ✅ PASS |

### REQ-02 URL parser

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --------- | -------------------- | ----------------------- | ------ |
| AC-02.1 video URL forms → `VideoRef(id, url)` | exact `VideoRef` value | `tests/test_url_parser.py:29` — `assert ref == VideoRef(id=VIDEO_ID, url=url)` over 7 forms at `:18-24` (watch?v=, youtu.be, no-www, extra query `&t=30`, `youtu.be?t=30`, `embed/`, scheme-less) | ✅ PASS |
| AC-02.2 playlist URLs → `PlaylistRef`; playlist wins | exact `PlaylistRef` value | `tests/test_url_parser.py:42` — `assert ref == PlaylistRef(id=PLAYLIST_ID, url=url)`; the "playlist wins" case is `:37` (`watch?v=…&list=PL…`) | ✅ PASS |
| AC-02.3 non-YouTube / missing id / non-PL list / short id | `InvalidUrlError` | `tests/test_url_parser.py:58-59` — `pytest.raises(InvalidUrlError): parse_youtube_url(url)` over `:48-54` (empty, garbage, google, vimeo, `playlist` w/o list, `list=NOTAPLAYLIST`, `v=short`) | ✅ PASS |
| AC-02.4 `parse_video_url` rejects playlist; `parse_playlist_url` rejects video | `InvalidUrlError` both ways | `tests/test_url_parser.py:63-64` and `:68-69` — `pytest.raises(InvalidUrlError)` for each direction | ✅ PASS |

### REQ-03 Ports + fakes

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --------- | -------------------- | ----------------------- | ------ |
| AC-03.1 fakes type-check against the Protocols | pyright accepts the conformance assignments | `tests/fakes.py:175-178` — `_youtube: YouTubeProviderPort = FakeYouTubeProvider()`, `_converter: AudioConverterPort = FakeAudioConverter()`, `_fs: FilesystemPort = FakeFilesystem()`, `_progress: ProgressSessionPort = RecordingProgress()`; `uv run pyright` exits 0 in the gate. Additional runtime-side conformance: `tests/test_local_filesystem.py:8` `fs: FilesystemPort = LocalFilesystem()`, `test_ffmpeg_converter.py:22` `converter: AudioConverterPort = FfmpegConverter(...)`, `test_rich_reporter.py:17` `session: ProgressSessionPort = reporter`, `test_pytubefix_provider.py:81` `provider: YouTubeProviderPort = PytubefixProvider()` | ✅ PASS |

### REQ-04 LocalFilesystem

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --------- | -------------------- | ----------------------- | ------ |
| AC-04.1 `ensure_dir` creates nested dirs, returns resolved path, idempotent | `result == target.resolve()` and dir exists; second call no-op | `tests/test_local_filesystem.py:11-12` — `assert result == target.resolve()`, `assert result.is_dir()`; idempotence `:17-19` — two calls then `assert (tmp_path/"x").is_dir()` | ✅ PASS |
| AC-04.2 `delete` removes file, tolerates missing | file gone; second delete does not raise | `tests/test_local_filesystem.py:26-28` — `assert not file.exists()` then `fs.delete(file)  # no raise` | ✅ PASS |

### REQ-05 FfmpegConverter

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --------- | -------------------- | ----------------------- | ------ |
| AC-05.1 argv shape + target `dest_dir/<stem>.mp3` returned | `argv[0]==ffmpeg_path`, `-i`→source, `-b:a`→bitrate, last arg == target | `tests/test_ffmpeg_converter.py:27` — `assert target == tmp_path / "song.mp3"`; `:29` `argv[0] == "/opt/ffmpeg"`; `:30` `argv[-1] == str(target)`; `:32` `argv[argv.index("-b:a") + 1] == "192k"`; `:33` `argv[argv.index("-i") + 1] == str(source)` | ✅ PASS |
| AC-05.2 non-zero exit → `ConversionFailedError` containing stderr | error message carries stderr text | `tests/test_ffmpeg_converter.py:43` — `pytest.raises(ConversionFailedError, match="bad input")` (stderr injected at `:40`) | ✅ PASS |
| AC-05.3 missing binary → `ConversionFailedError` containing "not found" | literal "not found" in message | `tests/test_ffmpeg_converter.py:54` — `pytest.raises(ConversionFailedError, match="not found")` | ✅ PASS |
| AC-05.4 (integration) real round-trip → non-empty mp3 | file exists, size > 0 | `tests/test_ffmpeg_converter.py:77-78` — `assert target.exists()`, `assert target.stat().st_size > 0`; ran green in the integration pass | ✅ PASS |

### REQ-06 RichProgressReporter

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --------- | -------------------- | ----------------------- | ------ |
| AC-06.1 `log` at info/warn/error reaches console inside a session | all three messages present in console output | `tests/test_rich_reporter.py:23-25` — `assert "plain info" in out`, `assert "careful" in out`, `assert "broken" in out` | ✅ PASS |
| AC-06.2 `add_task/update/complete` drive the Rich task (completed=total, finished) | `completed == 6` after `completed=4`+`advance=2`; after `complete`, `completed == total == 10` and `finished` | `tests/test_rich_reporter.py:35-36` — `assert state.completed == 6`, `assert state.description == "renamed"`; `:38-39` — `assert ...tasks[0].completed == 10`, `assert ...tasks[0].finished` | ✅ PASS |
| AC-06.3 late `total`; `complete` fills to it | `total` None → 100, then `completed == 100` | `tests/test_rich_reporter.py:46` — `assert ...total is None`; `:48` — `assert ...total == 100`; `:50` — `assert ...completed == 100` | ✅ PASS |
| AC-06.4 `log` works outside a session | message printed before `start()` | `tests/test_rich_reporter.py:56` — `assert "before start" in buffer.getvalue()` | ✅ PASS |

### REQ-07 PytubefixProvider

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --------- | -------------------- | ----------------------- | ------ |
| AC-07.1 `download_audio` picks `get_audio_only`, returns `DownloadedFile(path, title)` | getter "audio" picked; path + title returned | `tests/test_pytubefix_provider.py:83-85` — `assert result.path == tmp_path / "video.mp4"`, `assert result.title == "Fake Title"`, `assert ...streams.picked == ["audio"]` | ✅ PASS |
| AC-07.2 `download_video(LOWEST\|HIGHEST)` picks matching getter | "lowest" / "highest" | `tests/test_pytubefix_provider.py:95` — `assert ...streams.picked == [picked]`, parametrized `(LOWEST,"lowest"),(HIGHEST,"highest")` at `:89` | ✅ PASS |
| AC-07.3 hook translates to `(filesize − remaining, filesize)` | filesize 100, remaining 40 → `(60, 100)` | `tests/test_pytubefix_provider.py:104` — `assert seen == [(60, 100)]` after `hook(_FakeStream(), b"", 40)` at `:103` | ✅ PASS |
| AC-07.4 no stream → `StreamUnavailableError`; vendor exception → `ProviderError` w/ original message | both error types; original text preserved | `tests/test_pytubefix_provider.py:109-110` — `pytest.raises(StreamUnavailableError)`; `:115-116` — `pytest.raises(ProviderError, match="bot detected")` | ✅ PASS |
| AC-07.5 `fetch_playlist` returns title + `VideoRef`s from `video_urls` | title + parsed ids | `tests/test_pytubefix_provider.py:121-123` — `assert info.title == "Fake Playlist"`, `assert [v.id for v in info.videos] == ["aaaaaaaaaaa","bbbbbbbbbbb"]`, `assert info.ref == PL_REF` | ✅ PASS |

### REQ-08 Settings + registry

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --------- | -------------------- | ----------------------- | ------ |
| AC-08.1 seven defaults | `downloads`, LOWEST, 10, True, "128k", "ffmpeg", "pytubefix" | `tests/test_config.py:16-22` — `assert settings.download.output_dir == Path("downloads")`, `... video_resolution is Resolution.LOWEST`, `... batch_size == 10`, `... convert_to_mp3 is True`, `... default_bitrate == "128k"`, `... ffmpeg_path == "ffmpeg"`, `... youtube.provider == "pytubefix"` | ✅ PASS |
| AC-08.2 env overrides for every nested field; invalid resolution / unknown provider / batch_size 0 → `ValidationError` naming the field | each nested field takes the env value; error message names the field | overrides asserted `tests/test_config.py:44-49` (output_dir, video_resolution, batch_size, convert_to_mp3, default_bitrate, ffmpeg_path); errors `:54` `pytest.raises(ValidationError, match="video_resolution")`, `:60` `match="provider"`, `:66` `match="batch_size"` | ⚠️ Spec-precision gap — `YT_DOWNLOADER_YOUTUBE__PROVIDER` is set at `:39` but **never asserted**, so the one nested field on `YouTubeSettings` has no override assertion (see Gap 2) |
| AC-08.3 frozen; `audio_bitrate`/`timeout` removed | assignment raises `ValidationError`; attributes absent | `tests/test_config.py:72-73` — `assert not hasattr(settings.download, "audio_bitrate")`, `... "timeout")`; `:78-81` — `pytest.raises(ValidationError): settings.debug = True` and `settings.download.batch_size = 1` | ✅ PASS |
| AC-08.4 `build_youtube_provider(YouTubeSettings())` → `PytubefixProvider` | instance of `PytubefixProvider` | `tests/test_registry.py:8` — `assert isinstance(provider, PytubefixProvider)` | ✅ PASS |

### REQ-09 DownloadMediaUseCase

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --------- | -------------------- | ----------------------- | ------ |
| AC-09.1 video: `download_video` called, converter not called, task completed | one `video:highest` call, `converter.calls == []`, task done | `tests/test_download_media.py:41-43` — `assert youtube.calls == [("video:highest", REF.id)]`, `assert converter.calls == []`, `assert next(iter(progress.tasks.values())).done`; plus `:39` `result.path.suffix == ".mp4"` | ✅ PASS |
| AC-09.2 audio w/o mp3: `.m4a` kept, converter not called, nothing deleted | suffix `.m4a`, no convert, no delete | `tests/test_download_media.py:49-51` — `assert result.path.suffix == ".m4a"`, `assert converter.calls == []`, `assert fs.deleted == []` | ✅ PASS |
| AC-09.3 audio w/ mp3: converter called with `(path, bitrate)`, original deleted, `.mp3` keeps title, "Done" logged | exact call tuple, exact deleted path, title preserved | `tests/test_download_media.py:57-62` — `assert result.path.suffix == ".mp3"`, `assert result.title == f"Title {REF.id}"`, `assert call == (tmp_path.resolve() / f"{REF.id}.m4a", Bitrate("192k"))`, `assert fs.deleted == [tmp_path.resolve() / f"{REF.id}.m4a"]`, `assert any("Done" in m for m in progress.messages())` | ✅ PASS |
| AC-09.4 progress task ends total=completed=bytes, description=title, done | `total == 100`, `completed == 100`, description == title, done | `tests/test_download_media.py:69-72` — `assert state.total == 100`, `assert state.completed == 100`, `assert state.description == f"Title {REF.id}"`, `assert state.done` | ✅ PASS |
| AC-09.5 conversion failure → raised, original NOT deleted, last log level "error" | `ConversionFailedError`, `fs.deleted == []`, `.m4a` still on disk, last log `"error"` | `tests/test_download_media.py:78-82` — `pytest.raises(ConversionFailedError)`, `assert fs.deleted == []`, `assert (tmp_path / f"{REF.id}.m4a").exists()`, `assert progress.logs[-1][0] == "error"` | ✅ PASS |
| AC-09.6 stream failure propagates; output dir created | `StreamUnavailableError` escapes; nested dir exists | `tests/test_download_media.py:88-89` — `pytest.raises(StreamUnavailableError)`; `:95-96` — `assert target.is_dir()` for `tmp_path/"deep"/"er"` | ✅ PASS |

### REQ-10 DownloadPlaylistUseCase

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --------- | -------------------- | ----------------------- | ------ |
| AC-10.1 all succeed → successes in playlist order; overall total=completed=N, done | titles in playlist order, no failures, `total == completed == 5`, done | `tests/test_download_playlist.py:40-45` — `assert [f.title for f in result.successes] == [f"Title {v.id}" for v in VIDEOS]`, `assert result.failures == ()`, `assert overall.total == len(VIDEOS)`, `assert overall.completed == len(VIDEOS)`, `assert overall.done` | ✅ PASS |
| AC-10.2 per-video `DomainError` → `DownloadFailure(target, reason)`; others succeed | 4 successes, 1 failure carrying the right target + reason | `tests/test_download_playlist.py:54-57` — `assert len(result.successes) == 4`, `(failure,) = result.failures`, `assert failure.target == VIDEOS[1]`, `assert VIDEOS[1].id in failure.reason` | ✅ PASS |
| AC-10.3 peak concurrency ≤ `concurrency`; `concurrency=1` → peak 1 | `1 <= peak <= 2` for concurrency=2; `peak == 1` for concurrency=1 | `tests/test_download_playlist.py:64` — `assert 1 <= youtube.peak_concurrency <= 2`; `:71` — `assert youtube.peak_concurrency == 1` | ✅ PASS |
| AC-10.4 empty playlist → `EmptyPlaylistError`; fetch failure (`ProviderError`) propagates | both raise | `tests/test_download_playlist.py:76-77` — `pytest.raises(EmptyPlaylistError)`; `:82-83` — `pytest.raises(ProviderError)` | ✅ PASS |

### REQ-11 Container

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --------- | -------------------- | ----------------------- | ------ |
| AC-11.1 `build_container(Settings(), console)` wires reporter + both use cases; console identity preserved | `container.console is console`; concrete types | `tests/test_container.py:15-19` — `assert container.console is console`, `assert isinstance(container.progress, RichProgressReporter)`, `assert isinstance(container.download_media, DownloadMediaUseCase)`, `assert isinstance(container.download_playlist, DownloadPlaylistUseCase)`, `assert container.settings.youtube.provider == "pytubefix"` | ✅ PASS |

### REQ-12 CLI

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --------- | -------------------- | ----------------------- | ------ |
| AC-12.1 `info` prints type + id; invalid URL → exit 1 with "Error" | "video" + id in output; exit 1 + "Error" | `tests/test_cli.py:49-51` — `assert result.exit_code == 0`, `assert "video" in result.output`, `assert "dQw4w9WgXcQ" in result.output`; `:56-57` — `assert result.exit_code == 1`, `assert "Error" in result.output` | ✅ PASS |
| AC-12.2 default → video lowest from settings; `--audio-only` → mp3 by default; `--no-mp3` → `.m4a` | provider call `("video:lowest", id)`; `.mp3` in output; `.m4a` in output | `tests/test_cli.py:65-66` — `assert youtube.calls == [("video:lowest", "dQw4w9WgXcQ")]`, `assert ".mp4" in result.output`; `:74-75` — `assert youtube.calls == [("audio", "dQw4w9WgXcQ")]`, `assert ".mp3" in result.output`; `:83` — `assert ".m4a" in result.output` | ✅ PASS |
| AC-12.3 `-r 4k` → exit 2; `-b lots` → exit 1 mentioning bitrate; playlist URL → exit 1 | 2 / 1+"bitrate" / 1 | `tests/test_cli.py:88` — `assert result.exit_code == 2`; `:95-96` — `assert result.exit_code == 1`, `assert "bitrate" in result.output.lower()`; `:101` — `assert result.exit_code == 1` | ✅ PASS |
| AC-12.4 playlist default audio+async prints "N/N"; `--no-async` → peak 1; partial failure exit 0 listing failed ids; total failure exit 1 | all three audio calls, `"3/3"`; peak==1; exit 0 + `"2/3"` + failed id; exit 1 | `tests/test_cli.py:109-110` — `assert sorted(youtube.calls) == sorted(("audio", v.id) for v in VIDEOS)`, `assert "3/3" in result.output`; `:119` — `assert youtube.peak_concurrency == 1`; `:127-129` — `assert result.exit_code == 0`, `assert "2/3" in result.output`, `assert VIDEOS[0].id in result.output`; `:137` — `assert result.exit_code == 1` | ✅ PASS |
| AC-12.5 progress session entered and exited exactly once **per command** | `entered == 1` and `exited == 1` for each command | `tests/test_cli.py:161-162` — `assert progress.entered == 1`, `assert progress.exited == 1` — but only for `download-video` (`:158`) | ⚠️ Spec-precision gap — "per command" is asserted for one of the two session-using commands; `download-playlist` has no enter/exit-count assertion (see Gap 3) |
| AC-12.6 legacy `audio/ commands/ services/` deleted; ruff/pyright legacy excludes removed; GC-1..3 greps empty | dirs gone, no legacy excludes, greps empty | `ls src/yt_downloader/` → `adapters/ application/ bootstrap/ config/ domain/ __init__.py main.py py.typed` (no `audio/`, `commands/`, `services/`, `tests/`); `pyproject.toml:69-71` `extend-exclude = ["docs"]` only; `pyproject.toml:93-97` pyright `include = ["src","tests"]`, `strict = ["src"]`, no legacy exclude; GC-1/2/3 greps above are empty | ✅ PASS |
| AC-12.7 presenter output encodable on strict cp1252; both commands exit 0, no exception | `exception is None`, exit 0 for both | `tests/test_cli.py:151-154` — `assert single.exception is None`, `assert batch.exception is None`, `assert single.exit_code == 0`, `assert batch.exit_code == 0` on a `cp1252 errors="strict"` console (`:144`) with one induced failure (`:148`) | ✅ PASS |

### REQ-13 Closure

| Criterion | Spec-defined outcome | Evidence | Result |
| --------- | -------------------- | -------- | ------ |
| AC-13.1 `--cov-fail-under` = measured − 5, floored to a multiple of 5 | measured 95.83 → 90.83 → **90** | `pyproject.toml:62` — `"--cov-fail-under=90"`; gate output: `Required test coverage of 90% reached. Total coverage: 95.83%` | ✅ PASS |
| AC-13.2 README/CHANGELOG/CONTRIBUTING updated per plan Task 14 | all three changed in the range | `git diff --stat a954aad..HEAD -- README.md CHANGELOG.md CONTRIBUTING.md` → `CHANGELOG.md +20`, `CONTRIBUTING.md 48±`, `README.md 148±` (commit `1522bd2`) | ✅ PASS |

**Status**: ⚠️ 44/44 ACs + 6/6 GCs have `file:line` evidence; **0 uncovered**, **3 spec-precision gaps** (GC-5, AC-08.2, AC-12.5). No ❌ GAP.

---

## Discrimination Sensor

Run in scratch state: the real file was edited with `sed`, the covering test file run, then the
file restored from a scratchpad copy. `git status --short` was empty after each restore and after
the full sensor run (no `git stash` used).

| # | Mutation | File:line | Description | Killed? |
| - | -------- | --------- | ----------- | ------- |
| 1 | Remove required side effect | `src/yt_downloader/application/use_cases/download_media.py:77` | `self._fs.delete(downloaded.path)` → `pass` | ✅ Killed — `test_download_media.py::test_audio_with_mp3_converts_and_deletes_original` failed at `:61` (`assert [] == [WindowsPath('…dQw4w9WgXcQ.m4a')]`); 1 failed, 6 passed |
| 2 | Widen a bound | `src/yt_downloader/application/use_cases/download_playlist.py:43` | `asyncio.Semaphore(request.concurrency)` → `Semaphore(request.concurrency + 5)` | ✅ Killed — 2 failed, 4 passed: `test_concurrency_is_bounded` and `test_sequential_when_concurrency_is_one` (`assert 5 == 1` at `:71`) |
| 3 | Wrong computed value | `src/yt_downloader/adapters/outbound/youtube/pytubefix_provider.py:73` | `on_progress(stream.filesize - bytes_remaining, …)` → `on_progress(bytes_remaining, …)` | ✅ Killed — `test_progress_hook_translates_bytes_remaining` failed at `:104` (`assert [(40, 100)] == [(60, 100)]`); 1 failed, 6 passed, 1 deselected |
| 4 | Flip exit condition | `src/yt_downloader/adapters/inbound/cli/app.py:156` | `if not result.successes:` → `if result.failures:` | ✅ Killed — 2 failed, 12 passed: `test_download_playlist_partial_failure_exits_0_and_lists_failures` and `test_output_is_safe_on_cp1252_console` (`assert SystemExit(1) is None` at `:152`) |

**Sensor depth**: lightweight (4 behavior-level mutations across application, adapter-outbound and adapter-inbound layers)
**Result**: 4/4 killed — PASS ✅

---

## Code Quality

Judged against `references/coding-principles.md` (ports & adapters, minimum code, no
speculative flexibility) and the project's own GC-1..GC-6.

| Check | Status |
| ----- | ------ |
| No features beyond what was asked | ✅ — every new module maps to a spec REQ; no extra commands, no unused config keys (`audio_bitrate`/`timeout` were *removed*, not kept "just in case") |
| No abstractions for single-use code | ✅ — the one registry (`registry.py`) exists because AC-08.4 asks for it and `assert_never` keeps it honest; `_guard` in `pytubefix_provider.py:25` is used 8 times |
| No unnecessary "flexibility" added | ✅ — ports expose only the operations the use cases call (`FilesystemPort` is 2 methods, not a filesystem abstraction) |
| Only touched files required for task | ✅ — diff surface is `src/yt_downloader/**`, `tests/**`, `pyproject.toml` gate config, and the three docs named by AC-13.2 |
| Didn't "improve" unrelated code | ✅ — legacy deletions are all mandated by AC-12.6 |
| Matches existing patterns/style | ✅ — ruff `select=["ALL"]` with documented ignores; pyright `strict` over `src`; no `Any` in the diff |
| Tests map to ACs and are non-shallow (spot-check) | ✅ — spot-checked `tests/test_download_media.py`: no mock-call-count-only or no-throw-only test. The weakest candidate, `test_stream_failure_propagates:88`, asserts the exact spec-named exception type (AC-09.6); `test_audio_with_mp3_converts_and_deletes_original:59-61` asserts the *exact* converter argument tuple and the *exact* deleted path, not a call count. Sensor mutation 1 empirically confirms discrimination |
| Spec-anchored outcome check | ⚠️ — 3 spec-precision gaps flagged (GC-5, AC-08.2, AC-12.5); no assertion contradicts a spec-defined outcome |
| Per-layer Coverage Expectation met | ✅ — domain 1:1 with AC-01/AC-02; adapters 1:1 with AC-04..08; application 1:1 with AC-09/AC-10 with a dedicated test per edge case; CLI covers happy path + every listed error path (invalid URL, bad resolution, bad bitrate, wrong URL kind, partial failure, total failure, cp1252) |
| Every test maps to a spec requirement — no unclaimed tests | ✅ — `tests/test_cli.py`: 14 tests → AC-12.1 (2), AC-12.2 (3), AC-12.3 (3), AC-12.4 (4), AC-12.5 (1), AC-12.7 (1). `tests/test_download_media.py`: 7 tests → AC-09.1..09.5 (1 each) and AC-09.6 (2: stream failure + output dir). No unclaimed test in either file |
| Documented project guidelines followed | ✅ — `docs/plans/2026-09-02-hexagonal-refactor.md` §Decisões/§Contratos; global `CLAUDE.md` toolchain rule (uv + ruff `ALL` + pyright) satisfied by `pyproject.toml:66-99` |

**Layering note (positive)**: `domain/` imports nothing outside itself; `application/` imports only
`domain` + its own ports; vendor SDKs (`pytubefix`, `rich`, `subprocess`) appear only under
`adapters/outbound/**`; `typer` only under `adapters/inbound/cli/**`. `bootstrap/container.py` is
the single module importing concrete adapters. That is the hexagon the spec asked for.

---

## Edge Cases

- [x] Playlist id and video id in the same URL → playlist wins (`test_url_parser.py:37`)
- [x] Conversion fails → original `.m4a` kept, not deleted (`test_download_media.py:80-81`)
- [x] Empty playlist → `EmptyPlaylistError` rather than a silent empty result (`test_download_playlist.py:76`)
- [x] Partial playlist failure → exit 0 and failures listed (`test_cli.py:127-129`)
- [x] Total playlist failure → exit 1 (`test_cli.py:137`)
- [x] cp1252 (non-UTF-8 Windows console) output does not raise (`test_cli.py:151-154`)
- [x] `total` unknown at task creation, arriving later (`test_rich_reporter.py:46-50`)
- [x] Deleting an already-missing file (`test_local_filesystem.py:28`)
- [x] ffmpeg binary absent from PATH (`test_ffmpeg_converter.py:54`)

---

## Gate Check

- **Gate command**: `uv run ruff format . && uv run ruff check . && uv run pyright && uv run pytest -q`
- **Result**: exit 0 — `87 passed, 2 deselected`, 0 failed, 0 skipped. `ruff format` reported no
  reformatting, `ruff check` clean, `pyright` clean.
- **Coverage**: 95.83% total, gate `--cov-fail-under=90` satisfied. Uncovered lines are the
  `assert_never` fallbacks (`download_media.py:65-66`, `registry.py:16-17`), the `complete()`
  unknown-total branch (`rich_reporter.py:41`), one provider guard (`pytubefix_provider.py:86`)
  and the `main.py` `__main__` block — all unreachable-by-design or entry-point lines.
- **Integration**: `uv run pytest -q -m integration --no-cov` → `2 passed, 87 deselected` (real
  ffmpeg round-trip + real pytubefix network download). Both green on this machine.
- **Test count before feature**: 21 (legacy `test_config` + `test_parser`)
- **Test count after feature**: 89 collected (87 default + 2 integration)
- **Delta**: +68
- **Deleted tests**: legacy `src/yt_downloader/tests/test_audio_converter.py` (125 lines) — justified:
  pydub was removed by GC-1 and the module under test no longer exists; its behaviour is replaced by
  `tests/test_ffmpeg_converter.py` (4 tests incl. a real-binary integration test). Legacy
  `test_config.py`/`test_parser.py` were rewritten, not dropped, and the replacements assert strictly
  more (frozen-ness, removed fields, provider validation).
- **Assertion weakening**: none found. Every rewritten test asserts equal or more specific values
  than its legacy counterpart.
- **Failures**: none.

---

## Fix Plans

All three items are **Minor** — no blocker, no major. The feature is releasable as-is; these
harden the test suite against future regressions.

### Fix 1 (Minor): three CLI flags declared but never exercised — GC-5

- **Root cause**: `tests/test_cli.py` always relies on `settings.download.output_dir` (set from
  `tmp_path` in the `container` fixture at `:33`), so `-o/--output` never takes the override path;
  `--batch-size` and `--debug` have no test at all. GC-5 says the CLI "keeps" those flags — a
  regression that dropped or renamed them would only be caught by `--help` breaking, not by a test.
- **Fix task**: add three CLI tests — (a) `download-video -o <other_tmp>` asserts the downloaded
  file lands under the override directory, not `settings.download.output_dir`; (b)
  `download-playlist --batch-size 1` with `work_seconds` set asserts `youtube.peak_concurrency == 1`
  (proving the flag beats `settings.download.batch_size`); (c) `--debug` before the subcommand exits 0
  (a smoke assertion is enough — `setup_logging` is skipped when `ctx.obj` is injected).
- **Where**: `tests/test_cli.py`
- **Verify**: `uv run pytest tests/test_cli.py -q`; then mutate `app.py:99` `output or settings…` →
  `settings…` and confirm test (a) fails.
- **Done when**: all three flags have a citation and the (a) mutant is killed.
- **Priority**: Minor

### Fix 2 (Minor): `youtube.provider` nested env override unasserted — AC-08.2

- **Root cause**: `tests/test_config.py:39` sets `YT_DOWNLOADER_YOUTUBE__PROVIDER=pytubefix` inside
  `test_env_override_nested` but the test body (`:44-49`) never asserts `settings.youtube.provider`.
  Because the value equals the default, the assertion would be tautological today — but AC-08.2 says
  "every nested field", and if the env-nesting for `YouTubeSettings` broke, nothing would notice.
- **Fix task**: add `assert settings.youtube.provider == "pytubefix"` to `test_env_override_nested`,
  or (stronger) drop the env var from that test and rely on `test_unknown_provider_fails_fast:60`,
  which already proves the env var is read for this field — then adjust AC-08.2's wording so the
  spec and the suite agree.
- **Where**: `tests/test_config.py:30-49`
- **Verify**: `uv run pytest tests/test_config.py -q`
- **Done when**: the `youtube.provider` env path has an assertion or the AC is narrowed.
- **Priority**: Minor

### Fix 3 (Minor): session enter/exit counted for one command only — AC-12.5

- **Root cause**: `test_progress_session_is_opened_and_closed` (`tests/test_cli.py:157`) invokes only
  `download-video`. AC-12.5 says "exactly once **per command**"; `download-playlist` also opens a
  session (`app.py:149`) and is the riskier one (it wraps `asyncio.run`).
- **Fix task**: parametrize the test over `["download-video", VIDEO_URL]` and
  `["download-playlist", PLAYLIST_URL]`, keeping `entered == 1` / `exited == 1`.
- **Where**: `tests/test_cli.py:157-162`
- **Verify**: `uv run pytest tests/test_cli.py -q`; then remove `with container.progress:` from
  `download_playlist` (`app.py:149`) and confirm the new case fails.
- **Done when**: both session-using commands are covered and the mutant is killed.
- **Priority**: Minor

---

## Requirement Traceability Update

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| GC-1 | Implementing | ✅ Verified |
| GC-2 | Implementing | ✅ Verified |
| GC-3 | Implementing | ✅ Verified |
| GC-4 | Implementing | ✅ Verified |
| GC-5 | Implementing | ⚠️ Verified with precision gap (Fix 1) |
| GC-6 | Implementing | ✅ Verified |
| REQ-01 | Implementing | ✅ Verified |
| REQ-02 | Implementing | ✅ Verified |
| REQ-03 | Implementing | ✅ Verified |
| REQ-04 | Implementing | ✅ Verified |
| REQ-05 | Implementing | ✅ Verified |
| REQ-06 | Implementing | ✅ Verified |
| REQ-07 | Implementing | ✅ Verified |
| REQ-08 | Implementing | ⚠️ Verified with precision gap (Fix 2) |
| REQ-09 | Implementing | ✅ Verified |
| REQ-10 | Implementing | ✅ Verified |
| REQ-11 | Implementing | ✅ Verified |
| REQ-12 | Implementing | ⚠️ Verified with precision gap (Fix 3) |
| REQ-13 | Implementing | ✅ Verified |

---

## Summary

**Overall**: ✅ Ready (with 3 Minor hardening items)

**Spec-anchored check**: 50/50 criteria (44 ACs + 6 GCs) traced to `file:line` + assertion;
0 uncovered; 3 spec-precision gaps (GC-5, AC-08.2, AC-12.5)
**Sensor**: 4/4 mutations killed
**Gate**: 87 passed, 2 deselected, 0 failed, 95.83% coverage; integration 2 passed

**What works**:

- The hexagon is real, not nominal: `domain/` has no outward imports, `application/` sees only ports,
  every vendor SDK is confined to one adapter package, and `bootstrap/container.py` is the sole
  module that knows concrete adapters. GC-1/2/3 greps are empty.
- Error handling is a genuine anti-corruption layer: `pytubefix` and `subprocess` exceptions are
  translated at the boundary, and both use cases catch nothing but `DomainError` (GC-6).
- The riskiest behaviours — required side effects, concurrency bounding, byte-progress arithmetic,
  and the CLI exit contract — are all empirically discriminating (sensor 4/4).
- Legacy `audio/`, `commands/`, `services/` and the old in-package `tests/` are gone; no legacy
  lint or type-check excludes remain.
- The cp1252 regression found in manual smoke testing has a dedicated regression test
  (`test_cli.py:140`) that a strict-encoding console actually exercises.

**Issues found**: three Minor test-coverage gaps, detailed in Fix Plans 1–3. None affects shipped
behaviour; each closes a hole where a future regression would go unnoticed.

**Next steps**: merge is not blocked. Route Fix 1–3 to an implementer as one small follow-up task
(all three land in `tests/test_cli.py` and `tests/test_config.py`; no source change), then re-run
the build gate.
