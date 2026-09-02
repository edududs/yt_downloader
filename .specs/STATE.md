# STATE

## Decisions

- AD-001 (2026-09-01): Hexagonal refactor follows `docs/plans/2026-09-02-hexagonal-refactor.md` — its §Decisões (15 items) and §Contratos are the binding spec; `.specs/features/hexagonal-refactor/spec.md` gives them requirement IDs.
- AD-002 (2026-09-02): Execution is inline (user choice) after Task 1 ran via subagent-driven-development. Sub-agent batching offer declined by user ("inline edits").
- AD-003 (2026-09-02): Commits carry no Co-Authored-By trailer nor AI mention (user rule). Push only to open the PR the user requested at the end.
- AD-004 (2026-09-02): pyright `standard` globally, `strict = ["src"]` — plan test code uses unannotated fixtures.
- AD-005 (2026-09-02): `docs/` excluded from ruff — ruff 0.16 formats code fences inside markdown.

## Handoff

- Feature: hexagonal-refactor — branch `refactor/hexagonal-architecture` (worktree `.claude/worktrees/hexagonal-refactor`)
- Done: Task 1 (a7e3294). SDD ledger for Task 1 at `.superpowers/sdd/2026-09-02-hexagonal-refactor/progress.md` (git-ignored).
- Next: Task 2 (domain models) — see `.specs/features/hexagonal-refactor/tasks.md`.
