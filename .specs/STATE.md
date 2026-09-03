# STATE

## Decisions

- AD-001 (2026-09-01): Hexagonal refactor follows `docs/plans/2026-09-02-hexagonal-refactor.md` — its §Decisões (15 items) and §Contratos are the binding spec; `.specs/features/hexagonal-refactor/spec.md` gives them requirement IDs.
- AD-002 (2026-09-02): Execution is inline (user choice) after Task 1 ran via subagent-driven-development. Sub-agent batching offer declined by user ("inline edits").
- AD-003 (2026-09-02): Commits carry no Co-Authored-By trailer nor AI mention (user rule). Push only to open the PR the user requested at the end.
- AD-004 (2026-09-02): pyright `standard` globally, `strict = ["src"]` — plan test code uses unannotated fixtures.
- AD-005 (2026-09-02): `docs/` excluded from ruff — ruff 0.16 formats code fences inside markdown.

## Handoff (2026-09-03 — feature complete, verified, PR open)

- Status: Tasks 1–14 done. Verifier PASS (`features/hexagonal-refactor/validation.md`): 50/50 criteria, 4/4 mutants killed; its 3 spec-precision gaps closed by extra CLI tests. Suite 91 passed + 2 integration; coverage 95.8% (gate 90); ruff/pyright clean; manual smoke (real download → mp3) OK.
- Lessons: L-001, L-002 (candidates) in `LESSONS.md`.
- Next: review/merge the PR on GitHub. After merge, delete the worktree `.claude/worktrees/hexagonal-refactor`.

### Previous handoff (2026-09-02, kept for history)

- Feature: hexagonal-refactor — branch `refactor/hexagonal-architecture`, worktree `D:/Projects/yt-downloader/.claude/worktrees/hexagonal-refactor` (**keep the worktree on exit — it holds uncommitted work**).
- Completed & committed: Tasks 1–11 (a7e3294 … e685493). Last commit: `e685493 feat(application): DownloadPlaylistUseCase with bounded concurrency`. Suite at that commit: 72 passed + 2 integration (ffmpeg real, pytubefix 10.11 real) passed separately; ruff/pyright clean.
- In progress (Task 12 + 13, **uncommitted, gate NOT yet run**):
  - New: `src/yt_downloader/bootstrap/{__init__,container}.py`, `src/yt_downloader/adapters/inbound/{__init__.py,cli/__init__.py,cli/app.py,cli/presenters.py,cli/logging_setup.py}`, `tests/test_container.py`, `tests/test_cli.py` (RED confirmed: collection errors before impl).
  - Modified: `src/yt_downloader/main.py` (thin entry), `pyproject.toml` (legacy `extend-exclude`/pyright `exclude` removed), `.specs/features/hexagonal-refactor/tasks.md`.
  - Staged deletions: `src/yt_downloader/{audio,commands,services}/` (git rm done).
- Next step, in order:
  1. `uv run ruff format . && uv run ruff check . && uv run pyright && uv run pytest -q` — expect 86 passed (72 + 1 container + 13 cli). Fix lint/type findings only (no test changes).
  2. Guardrail greps (plan Task 13 Step 5): no `pytubefix` import outside `adapters/outbound/youtube/`; no `subprocess` outside `adapters/outbound/audio/`; no `config.settings` import outside bootstrap / cli / registry.
  3. Manual smoke (network): `uv run yt-downloader info <url>` and `uv run yt-downloader download-video --audio-only -o ./tmp-smoke <url>`; delete `./tmp-smoke`.
  4. Commit T12 (`bootstrap/` + `tests/test_container.py`: "feat(bootstrap): composition root"), then T13 (everything else: "feat(cli): skinny Typer adapter over use cases; remove legacy services/commands/audio" with BREAKING notes from plan). Mark 12/13 ✅ in tasks.md.
  5. Task 14: measure coverage → set `--cov-fail-under` = measured − 5 (rounded down to multiple of 5); README/CHANGELOG/CONTRIBUTING per plan §Task 14; commit "docs: …".
  6. Verifier (tlc `validate.md`, fresh sub-agent or standalone fresh-eyes pass) → `.specs/features/hexagonal-refactor/validation.md`.
  7. Push branch and open PR with `gh` (user requested a PR; no AI attribution in commits/PR body). Do NOT push before the user says go.
- Blockers: none. Known: pyright `strict=["src"]` ignores per-rule config overrides → the pytubefix module uses a file-level `# pyright: reportMissingTypeStubs=false`.
- Plan doc (task bodies + code): `docs/plans/2026-09-02-hexagonal-refactor.md`. Spec IDs: `.specs/features/hexagonal-refactor/spec.md`.
