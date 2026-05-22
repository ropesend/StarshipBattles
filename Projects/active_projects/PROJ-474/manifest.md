# PROJ-474 File Manifest

> Generated during planning. Used by /claude-proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `tests/static_guards/test_facade_read_path_imports_guard.py` | Test (guard) | Add `_UISAFE_SYMBOLS` data + matcher branch; add parity + no-misfile tests; move promoted entries out of `TAIL`; drop `EmpireEconomySnapshot` entry. PRIMARY change site. |
| `docs/02_PATTERNS.md` | Doc | Pattern #5: add a parseable fenced canonical `module.member` token block; add `ComponentActivationState` + the promoted symbols to the UI-safe list. |
| `game/ui/panels/empire_treasury_panel.py` | Production | Move `EmpireEconomySnapshot` import under `TYPE_CHECKING` (annotation-only; `from __future__ import annotations` already present? verify). Sole production edit. |

## Conflict notes
- Single-phase project; no intra-project parallel conflicts.
- Cross-project: PROJ-475/476 also edit
  `tests/static_guards/test_facade_read_path_imports_guard.py` (removing TAIL
  entries as they migrate). PROJ-474 runs FIRST (see decisions), so it owns the
  structural change; 475/476 then edit the file-scoped transitional set only.
- `docs/02_PATTERNS.md` Pattern #5 is touched by 475 (honesty-note updates) and
  476 — sequence 474→475→476 avoids overlap.

## Verification gate
- `tests/static_guards/test_facade_read_path_imports_guard.py` green incl. new
  parity + no-misfile tests.
- Affected UI imports still resolve: `pytest tests/ -k "treasury or new_game_setup or race_setup or galaxy_test or builder or transfer or planet_abilities or orders_window" --testmon` (smoke), then sharded suite at close.
