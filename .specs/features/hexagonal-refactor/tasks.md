# Tasks — hexagonal-refactor

Task bodies (files, code, tests, commit messages) live in `docs/plans/2026-09-02-hexagonal-refactor.md` §Task N. This file tracks status, dependencies and gates only.

## Gate Check Commands

- quick: `uv run pytest tests/<file> -q`
- build: `uv run ruff format . && uv run ruff check . && uv run pyright && uv run pytest -q`
- integration (Tasks 6, 8): `uv run pytest tests/<file> -q -m integration`

Every task ends with the **build** gate (project rule GC-4), then one atomic commit.

## Execution Plan

| # | Task | REQ | Depends on | Gate | Status |
|---|------|-----|------------|------|--------|
| 1 | Toolchain, harness, deps | GC | — | build | ✅ a7e3294 |
| 2 | Domain errors + models | REQ-01 | 1 | build | ⬜ |
| 3 | Domain url_parser | REQ-02 | 2 | build | ⬜ |
| 4 | Ports + fakes | REQ-03 | 2 | build (pyright is the test) | ⬜ |
| 5 | LocalFilesystem | REQ-04 | 4 | build | ⬜ |
| 6 | FfmpegConverter | REQ-05 | 4 | build + integration | ⬜ |
| 7 | RichProgressReporter | REQ-06 | 4 | build | ⬜ |
| 8 | PytubefixProvider | REQ-07 | 3, 4 | build + integration | ⬜ |
| 9 | Settings + registry | REQ-08 | 2, 8 | build | ⬜ |
| 10 | DownloadMediaUseCase | REQ-09 | 4 | build | ⬜ |
| 11 | DownloadPlaylistUseCase | REQ-10 | 10 | build | ⬜ |
| 12 | Container | REQ-11 | 5–11 | build | ⬜ |
| 13 | CLI + main + delete legacy | REQ-12 | 12 | build + greps + manual smoke | ⬜ |
| 14 | Coverage gate + docs | REQ-13 | 13 | build | ⬜ |

## Test Coverage Matrix

| Layer | Files | Coverage expectation |
|---|---|---|
| domain | tests/test_domain_models.py, tests/test_url_parser.py | 1:1 with AC-01.*, AC-02.* |
| ports | tests/fakes.py (pyright structural conformance) | AC-03.1 |
| adapters | tests/test_local_filesystem.py, test_ffmpeg_converter.py, test_rich_reporter.py, test_pytubefix_provider.py, test_registry.py, test_config.py | 1:1 with AC-04..08 |
| application | tests/test_download_media.py, test_download_playlist.py | 1:1 with AC-09, AC-10; edge cases each a dedicated test |
| bootstrap + cli | tests/test_container.py, tests/test_cli.py | AC-11, AC-12: happy path + each listed error path |
