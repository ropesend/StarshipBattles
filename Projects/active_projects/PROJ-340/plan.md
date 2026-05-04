# PROJ-340 — UI services + utility characterization

**Branch:** `feat/03c-phase-aware-execution`
**Started:** 2026-05-04
**Source plan:** `C:\Users\rossr\.claude\plans\noble-stirring-galaxy-agent-ad173653cfa644a72.md`
**Predecessors:** PROJ-337/338/339 (UI test coverage arc — sibling, non-overlapping file sets)

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Characterization tests for 6 production files | Pending | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** Phase 1 (characterization tests)
**Next Action:** Author `tests/unit/ui/services/test_battle_ui_service.py` (smallest file, no I/O).
**Blockers:** None.

## Overview

PROJ-340 adds characterization test coverage to six previously-thin or
untested UI files spanning four packages: `services/`, `assets/`, `widgets/`,
`effects/`, and `panels/`. The arc parallels PROJ-337/338/339 (also in the
UI coverage arc); file sets are disjoint by design so the four projects can
in principle run in parallel.

This is **characterization** work, not TDD. The goal is to pin existing
behavior so future refactors have a safety net. No production behavior is
intentionally changed; observed bugs are filed as separate observations,
not fixed in-line.

## Goals

- **Phase 1:** Author 6 new test modules under `tests/unit/ui/...` that
  cover ~45 behaviors across the in-scope files, following the master-plan's
  "minimum-viable" sizing for boilerplate-heavy panel files and broader
  coverage for stateful or I/O-bearing modules.

## Scope

**In:**
- `game/ui/services/battle_ui_service.py` (299 LOC) — DTO conversion seam
- `game/ui/assets/ship_theme_manager.py` (453 LOC) — theme discovery + lazy image cache
- `game/ui/widgets/scrollable_json_panel.py` (412 LOC) — stateful JSON viewer
- `game/ui/effects/hit_effects.py` (233 LOC) — hit-effect dataclass + draw helpers
- `game/ui/panels/base_gallery.py` (265 LOC) — abstract gallery base
- `game/ui/panels/builder_widgets.py` (294 LOC) — `ModifierEditorPanel`
- 6 new test files (one per production file)

**Out:**
- Any production-side change (refactor, bug fix, API tweak). Findings go
  in `decisions.md` as observations only.
- Files owned by PROJ-337/338/339 (see manifest's overlap check).
- Integration/end-to-end tests; this is unit-level characterization only.

## Success criteria

- 6 new test files added under `tests/unit/ui/services/`,
  `tests/unit/ui/assets/`, `tests/unit/ui/widgets/`,
  `tests/unit/ui/effects/`, and `tests/unit/ui/panels/`.
- ~45 behaviors pinned (see `phase_1_checklist.md` for the per-file table).
- `pytest tests/unit/ui/ -x -q` green.
- `python Tools/test_sharded/test_sharded.py` green (modulo pre-existing
  unrelated failures).
- `python Tools/lint_test_files.py` reports 0 violations on the new files.
- No production file in scope is modified.
- Per-file commit discipline (6 commits — one per production file's tests).

## Source documents

- [`docs/01_ARCHITECTURE.md`](../../../docs/01_ARCHITECTURE.md) — UI layer boundaries
- [`docs/02_PATTERNS.md`](../../../docs/02_PATTERNS.md) — characterization pattern + service seams
- [`docs/03_CONVENTIONS.md`](../../../docs/03_CONVENTIONS.md) §2 (test conventions)
- [`Projects/active_projects/PROJ-329A/`](../PROJ-329A/) — reference directory shape
- Sibling projects PROJ-337 / PROJ-338 / PROJ-339 — same arc, disjoint file sets

## Verification

- `pytest tests/unit/ui/services/test_battle_ui_service.py -x -q`
- `pytest tests/unit/ui/assets/test_ship_theme_manager.py -x -q`
- `pytest tests/unit/ui/widgets/test_scrollable_json_panel.py -x -q`
- `pytest tests/unit/ui/effects/test_hit_effects.py -x -q`
- `pytest tests/unit/ui/panels/test_base_gallery.py -x -q`
- `pytest tests/unit/ui/panels/test_builder_widgets.py -x -q`
- `python Tools/test_sharded/test_sharded.py` — full suite green.
- `python Tools/lint_test_files.py` — 0 violations.
