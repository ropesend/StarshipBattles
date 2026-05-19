# PROJ-455 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Phase 1 — End-to-end fixture construction

### New test files

| File | Type | Notes |
|------|------|-------|
| `tests/integration/test_process_planet_action_tick_end_to_end.py` | Test (new) | Primary deliverable. Contains the `_StubPlanet` fixture (adapted from the precedent at `tests/integration/test_fms_planet_lay_mines.py`), scenario builders for all 5 FMS order types, `engine_and_processor` fixture, and the smoke test for LAY_MINES end-to-end. |

### Production files

| File | Type | Notes |
|------|------|-------|
| (none — Phase 1 is fixture construction only) | | |

## Phase 2 — Parametrised end-to-end test across 5 FMS order types

### Modified test files

| File | Type | Notes |
|------|------|-------|
| `tests/integration/test_process_planet_action_tick_end_to_end.py` | Test (modified) | Add `test_process_planet_action_tick_end_to_end` parametrised across the 5 `order_metadata.planet_fms_action_order_types`. Add `test_planet_fms_e2e_parametrise_matches_registry_view` guard. |

### Production files

| File | Type | Notes |
|------|------|-------|
| (none — Phase 2 adds tests only; the production engine path is already wired correctly per PROJ-445 Phase 1) | | |

## Phase 3 — DI log status update

### Documentation / coordination

| File | Type | Notes |
|------|------|-------|
| `AgentCoordination/discovered_issues/log.jsonl` | Coordination doc | Update DI-2026-05-18-001 (ActionExecutionEngine half — line 1 of the file): set `"status": "resolved"` and add `"resolution_note": "Updated 2026-XX-XX PROJ-455 Phase 2: ActionExecutionEngine half closed by end-to-end tests at tests/integration/test_process_planet_action_tick_end_to_end.py parametrised across all 5 planet_fms_action_order_types."` |

---

## Cross-bucket conflicts to watch

| File | Other projects touching | Resolution |
|------|------------------------|------------|
| `tests/integration/test_process_planet_action_tick_end_to_end.py` | None (new file) | No conflict. |
| `AgentCoordination/discovered_issues/log.jsonl` | All sibling projects update their own DI entries; PROJ-455 updates only DI-001 ActionExecutionEngine half. Merge conflicts on this file are resolved by per-line atomicity (jsonl format). | No structural conflict; only line-level merges. |
| `tests/integration/test_fms_planet_lay_mines.py` | None — read-only reference for the fixture shape | No conflict. |

## Production code touched

**Zero production files touched.** PROJ-455 is purely a test-coverage project. If implementation discovers a real production bug in `_process_planet_action_tick` (vs. a structural mismatch the existing handler tests would catch), log it via `/claude-di-log` and surface for a follow-up project — do NOT fix inline.

## File count summary

- **1 new test file** (Phase 1 + 2 share the same file)
- **0 production files touched**
- **0 modified test files** (existing `test_fms_planet_lay_mines.py` stays as-is)
- **1 coordination file updated** (Phase 3 — `log.jsonl`)
- **Total LOC delta (test-side):** ≈200-300 lines — comparable to the precedent `test_fms_planet_lay_mines.py` (297 LOC)
