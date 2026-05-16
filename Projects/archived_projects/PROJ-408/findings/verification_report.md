# PROJ-408 Verification Report

**Date:** 2026-05-09
**Branch:** `feat/03c-phase-aware-execution`
**Effective scope:** C-01, C-02, C-04 (C-05 / C-06 already shipped Wave 1; C-03 deferred to PROJ-409).

## Summary

Landed direct unit coverage for the three remaining PROJ-380..399 review gaps. **No production code changed** — all work is in `tests/`. Eleven new tests + one introspection-only test deleted.

## Per-task

### C-01 — `EmpireBuildQueueWindow` real-construction test
- **File:** `tests/unit/ui/screens/test_empire_build_queue_window.py`
- **Replaced:** `test_constructor_requires_facade` (inspected `inspect.signature(EmpireBuildQueueWindow.__init__)`, no construction).
- **Added:** `test_add_item_to_source_routes_command_through_facade` — constructs the window, invokes `_add_item_to_source`, asserts `_facade.handle_command` was called once with an `AddToConstructionQueueCommand` carrying the threaded `design_id`, `category`, `queue_id`, `entity_id`, `entity_type`.
- **Result:** PASS. Module: 118 passed (unchanged count: -1 introspection +1 real-construction).
- **Commit:** `049193339`.

### C-02 — Facade `EnginePhaseError` -> `TurnFailedError` conversion
- **File:** `tests/unit/strategy/facade/test_strategy_session_facade.py`
- **Added:** new class `TestProcessTurnErrorConversion` with 5 tests:
  1. Class identity (`type(exc) is TurnFailedError`).
  2. Message + code + context + PROJ-395 properties (`phase_name`, `tick`, `turn_number`, `save_path`).
  3. `__cause__` chaining preserved.
  4. `_state.invalidate_all` not called on the error path.
  5. Non-`EnginePhaseError` (e.g., `RuntimeError`) propagates unchanged.
- **Result:** 5/5 PASS. Full facade module: 324 passed (was 319; +5).
- **Commit:** `1add34b20`.

### C-04 — `PlanetSelectionWindow` facade threading
- **File:** `tests/unit/ui/screens/test_planet_selection_window.py`
- **Added:** new class `TestFacadeThreading` with 5 tests covering construction-time storage, default `None`, colonized-planet fetch + thread-through to `PlanetReportPanel(view=...)`, uncolonized short-circuit, and `facade=None` fallback. Patched `PlanetReportPanel`, `get_default_asset_manager`, and `pygame_gui.elements.UIWindow.update` so the panel-creation branch in `update()` runs without a real display.
- **Result:** 5/5 PASS. Module: 23 passed.
- **Commit:** `b9b622eee`.

## Wave 1 cross-check (must remain green)

- **C-05** (PROJ-404 negative save-shape tests) — `tests/unit/strategy/ship_instance/ -k missing_components`: **PASS**.
- **C-06** (PROJ-401 missing-`species_id` rejection) — `tests/unit/strategy/validation/ -k missing_species_id`: **PASS**.

## Validators

- `python Projects/scripts/validate_phase.py PROJ-408 1` — **PASSED**.
- `python Projects/scripts/validate_audit_ready.py PROJ-408` — **PASSED**.

## Deferrals

None. All three in-scope items landed cleanly. No production class was too tangled to construct under existing fixtures.
