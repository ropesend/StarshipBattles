# Phase 3: Test Rename

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-298 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace every old-name reference in `tests/` with the canonical new name. After this phase, NO source-tree references to old names remain except the alias declarations themselves.

**Prerequisites:** Phase 2 complete; production source uses only new names.

---

## Implementation approach (used)

Bulk rename via Python regex script with word-boundary patterns. The `Bash` tool ran a small in-line Python program that read each test file, applied 10 word-boundary `re.sub()` patterns, and wrote the file back. Word boundaries (`\bSymbol\b`) prevent substring corruption (e.g. `FleetOrders` plural variable names stay intact). After each batch, ran targeted `pytest` to confirm green.

---

## Tasks

### Task 3.1: Strategy core unit tests [Simple]
**File:** Files under `tests/unit/strategy/` (per `findings/rename_plan.md`)
**Tests:** `pytest tests/unit/strategy/`

- [x] Renamed 11 files: `test_fleet_order_processor.py` (15), `test_fleet_orders_logic.py` (13), `test_advanced_fleet_orders.py` (5), `test_engine_event_emission.py` (8), `conflict_resolution/test_core.py` (2), `turn_engine/test_turn_processing.py` (1), `turn_engine/test_tick_mechanics.py` (9), `turn_engine/conftest.py` (1), `data/test_empire_fleet_registration.py` (7), `data/test_fleet_order_resolution.py` (5), `data/test_superweapon_orders.py` (8). **74 total replacements.**
- [x] Run targeted tests
- [x] **Verification:** zero hits remain in `tests/unit/strategy/` for the targeted symbols (verified by grep)

**Notes:** All tests pass. Filenames stay (e.g., `test_fleet_orders_logic.py` describes domain).

---

### Task 3.2: Unit/strategy engine + 3.3 fleet/services/facade/movement [Simple]
**File:** Files under `tests/unit/strategy/engine/`, `tests/unit/strategy/fleet/`, etc.
**Tests:** `pytest tests/unit/strategy/engine/ tests/unit/strategy/fleet/ ...`

- [x] Renamed 32 files. Notable counts: `test_action_execution_engine.py` (22), `test_superweapon_order_processor.py` (28), `test_superweapon_edge_cases.py` (21), `test_planet_action_engine.py` (20), `fleet/test_basics.py` (31), `fleet/test_fleet_pursuer_tracker.py` (31), `fleet/test_serialization.py` (17), `services/test_fleet_navigation_action_timing.py` (20). **322 total replacements** across the batch.
- [x] Run targeted tests — **1387/1387 pass.**
- [x] **Verification:** zero hits remain

**Notes:**
- Caught one missed file: `tests/unit/strategy/engine/test_build_order_command_handler.py` (4 FleetOrder hits). Renamed in cleanup pass — 13/13 tests pass.

---

### Task 3.4 + 3.5 + 3.6 + 3.7 + 3.8: UI screens + integration + fixtures + repro [Simple]
**File:** UI screen tests, integration tests, fixtures, repro reproducers

- [x] Renamed 33 files in one batch. Notable counts: `test_command_handlers.py` integration (17), `test_roundtrip_orders.py` (21), `test_fleet_orders_refresh.py` (19), `test_fleet_navigation_consistency.py` (19), `test_fleet_join_redirect.py` (16), `test_superweapon_integration.py` (13), `test_planet_specific_colonization.py` (11), `turn_engine/test_basics.py` (11). **244 total replacements.**
- [x] Run targeted tests — **610/610 pass + 1 skipped** (skip is unrelated/pre-existing).
- [x] **Verification:** zero hits remain in tests/ for the targeted symbols

**Notes:**
- One pre-existing failure (`test_build_context.py::test_fleet_satisfies_build_context_protocol`) was confirmed unrelated to PROJ-298 via `git stash` test (failure persisted with all PROJ-298 changes stashed). Out of scope.

---

### Task 3.9: Update stale docstring reference [Simple]
**File:** `game/strategy/data/order_types.py:151`

- [x] Updated the docstring of `Order.from_dict()` to reference `OrderSerializer` (was `FleetOrderSerializer`). The class description now reads accurately.

---

### Final sweep
- [x] `grep -rn "\bFleetOrder\b|\bPlanetOrder\b|\bClearFleetOrdersCommand\b|\bDeleteFleetOrderCommand\b|\bReorderFleetOrderCommand\b|\bFleetOrdersWindow\b|\bFleetOrderSerializer\b|\bFleetOrderProcessor\b" returns ONLY:
  - 8 alias declarations (Phase 4 deletion targets)
  - The `__init__.py` re-export at lines 13, 34, 64 (Phase 4 deletion)
  - The `fleet_orders_window.py` shim file (Phase 4 deletion)
  - Historical migration docstrings (KEEP)
- [x] Total Phase 3 test files modified: ~76 (across 3.1, 3.2/3.3, 3.4-3.8, +1 cleanup). Total replacements: ~644.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `grep -rn "\bFleetOrder\b\|\bPlanetOrder\b\|\bClearFleetOrdersCommand\b\|\bDeleteFleetOrderCommand\b\|\bReorderFleetOrderCommand\b\|\bFleetOrdersWindow\b" game/ tests/` returns ONLY the alias declarations + the shim module + the `__init__.py` re-export + historical comments
- [x] Targeted suite passes (no PROJ-298 regressions)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 4: Delete Aliases & Shim Module)
