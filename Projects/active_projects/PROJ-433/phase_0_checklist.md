# Phase 0: Characterization — pin current `component_inspector` surface with focused tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-433 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** none
**Review Mode:** lightweight
**Files (planned):**
- `tests/unit/strategy/services/test_component_inspector.py` (or new sibling)
- `tests/unit/strategy/services/test_component_inspector_layers.py`

**Objective:** Pin the current public surface of `game/strategy/services/component_inspector.py` (16 functions, the `__all__` list) with focused tests so Phase 1's mechanical move lands on top of explicit regression coverage. Decide the public-surface contract for Phase 1 — re-export package (Option A) vs. caller migration (Option B) — based on a grep audit of all import sites.

---

## Tasks

### Task 0.1: Snapshot the current `__all__` set [Simple]
**File:** `tests/unit/strategy/services/test_component_inspector.py` (or sibling)

- [ ] Add a focused test that imports `game.strategy.services.component_inspector` and asserts the `__all__` set is exactly the 16-name set listed in `design.md`.
- [ ] Test must pass against `proj/PROJ-433/main` HEAD today; it is a "drift gate" that fires if Phase 1 accidentally drops a name from the public surface.

### Task 0.2: Grep all import sites [Simple]
**Tests:** none (analysis task)

- [ ] Run `rg -n "from game.strategy.services.component_inspector|import.*component_inspector" game tests`.
- [ ] Record the call-site count in `findings_ledger.md`.
- [ ] List which functions are imported from where — this informs Phase 1's `lookup_design_max_hp` placement decision and the Option A vs. B decision.

### Task 0.3: Confirm Surface A test coverage [Standard]
**Tests:** `pytest tests/unit/strategy/services/test_component_inspector*.py -v`

- [ ] Inventory the existing tests for Surface A helpers (`get_component_abilities`, `extract_abilities_from_component`, `get_component_type`, `get_component_threshold`, `iterate_design_components`, `iter_facility_ability_entries`, `ship_has_ability`, `find_ship_with_ability`, `count_ability`, `list_ship_abilities`, `get_ability_list`, `has_warp_capability`).
- [ ] Record gaps in `findings_ledger.md`. If a helper has no focused test today, decide whether to backfill in Phase 0 or accept the gap (helpers reachable only via Surface B don't need an extra direct test).

### Task 0.4: Confirm Surface B test coverage [Simple]
**Tests:** `pytest tests/unit/strategy/services/test_component_inspector_layers.py -v`

- [ ] Confirm all 6 tests added by PROJ-425 Phase 2 still pass.
- [ ] Confirm they cover `iter_components_by_layer`, `damaged_components_by_layer`, `count_damaged_components`, and `lookup_design_max_hp` directly (or transitively).

### Task 0.5: Lock the Option A vs. Option B decision [Simple]
**File:** `Projects/active_projects/PROJ-433/decisions.md`

- [ ] Based on the Task 0.2 grep count, choose Option A (re-export shim at `component_inspector.py`) or Option B (delete + migrate all callers in Phase 1).
- [ ] Add a decisions.md row capturing the choice and the import-site count that drove it.
- [ ] Update `manifest.md` to reflect the chosen option (which import sites Phase 1 will touch).

### Task 0.6: Baseline LOC + test pass counts [Simple]
**Tests:** `pytest tests/unit/strategy/services/test_component_inspector*.py -q`

- [ ] Record current `wc -l game/strategy/services/component_inspector.py` in `findings_ledger.md` (expected: 537).
- [ ] Record the focused-suite pass count.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `__all__` snapshot test added and green
- [ ] Import-site grep recorded in `findings_ledger.md`
- [ ] Option A vs. B decision locked in `decisions.md`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 1
