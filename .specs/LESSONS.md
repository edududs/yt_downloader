# LESSONS — auto-maintained by scripts/lessons.py

> Machine-owned. Do NOT hand-edit. Changes are overwritten on the next `lessons.py` write.
> Canonical state lives in `.specs/lessons.json`. Edit lessons only via the script.
> promote_threshold=2 distinct features · window_days=45 · quarantine_threshold=2

## Confirmed (load these at Specify/Design)

Corroborated across multiple features. Safe to apply as guidance.

_none_

## Candidates (under observation — do NOT load as guidance yet)

Seen once or not yet corroborated. Tracked, not trusted.

### L-001 — When an AC says 'per command' or 'per route', parametrize the test over every command instead of covering the first one.
- signal: `spec_precision_gap` · recurrence: 1 feature(s) · scope: `tests/cli` · harmful: 0
- features: hexagonal-refactor
- evidence: AC-12.5 / tests/test_cli.py:157 (tests/cli)
- last seen: 2026-09-03T12:05:58Z

### L-002 — A CLI fixture that pre-fills settings hides flags; every flag the spec preserves needs one explicit invocation test.
- signal: `spec_precision_gap` · recurrence: 1 feature(s) · scope: `tests/cli` · harmful: 0
- features: hexagonal-refactor
- evidence: GC-5 / tests/test_cli.py fixture (tests/cli)
- last seen: 2026-09-03T12:05:58Z

## Quarantined (failed when applied — ignore)

A confirmed lesson that recurred alongside failure. Kept for the maintainer to review.

_none_
