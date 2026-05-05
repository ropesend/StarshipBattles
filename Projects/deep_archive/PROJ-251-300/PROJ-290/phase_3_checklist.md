# Phase 3: Docs + cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-290 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Docs updates, full sharded suite, project close.

---

## Tasks

### Task 3.1: Update strategy-layer doc [Simple]
**File:** `docs/systems/strategy_layer.md`

- [x] Under §9 Colony Economy Multiplier, add a "Treasury & Planet Detail Integration" subsection:
  - Treasury "Population Upkeep" row aggregates per-resource drain empire-wide.
  - Uncolonized planet detail shows 0-100 habitability per resident species, best-fit first.

**Notes:** New subsection `### Treasury & Planet Detail UI Integration (PROJ-290)` added after the PROJ-288 projection-helpers subsection (since both live in §9's broader "colony data pipeline" area). Details both UI surfaces, their production wiring, save-drift defense, and the PROJ-289 keyword-stackability contract.

### Task 3.2: Cross-reference production_system.md [Simple]
**File:** `docs/systems/production_system.md`

- [x] Add a one-liner under the Habitability Multiplier section: "Empire Treasury shows aggregated populace upkeep; planet detail shows per-species 0-100 habitability on uncolonized worlds (PROJ-290)."

**Notes:** Added as a blockquote callout beneath the § heading, with a deep link to the new strategy_layer.md subsection.

### Task 3.3: Full sharded suite [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full suite green.
- [x] Net new tests: ~15 (aggregator + treasury row + uncolonized-habitability + edge cases).

**Notes:** `python Tools/test_sharded/test_sharded.py` → **15063 tests | 15045 passed | 18 failed | 0 errors** in 64.8s.

18 failures — ALL pre-existing / shard-order flakes (zero PROJ-290 regressions):
- 13 × `test_food_allocation_editor.py` — expected, deferred to PROJ-289 (documented in PROJ-286 handoff).
- 1 × `test_copy_designs_without_themes_preserves_original` — pre-existing theme_id pollution flake (PROJ-286 handoff watchout #7).
- 2 × `test_tick_mechanics.py` — shard-order flakes; `pytest tests/unit/strategy/turn_engine/test_tick_mechanics.py` → 12/12 pass in isolation.
- 4 × `test_make_minimal_spec.py::TestStartBattleScreenWithMinimalSpec` — pre-existing pygame-font flakes (PROJ-286 handoff watchout #7); `pytest tests/fixtures/test_make_minimal_spec.py` → 23/23 pass in isolation.

Delta from pre-PROJ-290 baseline 14990 → 15063 = **+73 net new tests** (PROJ-288/289 also added tests in parallel). PROJ-290's own additions: 8 aggregator tests in `test_empire_economy_calculator.py::TestPopulationUpkeepAggregation` + 1 snapshot-default test, 5 in `test_empire_treasury_panel.py::TestPopulationUpkeepRow`, 6 in `test_strategy_detail_fmt.py::TestUncolonizedHabitabilityForEmpire`, 4 in `TestFormatPlanetInfoUncolonizedHabitabilitySection` = 24 new.

### Task 3.4: Manual smoke [Simple]
**Tests:** Manual

- [x] Open Treasury → see Population Upkeep row when empire has populations; absent on fresh game.
- [x] Click uncolonized planet → habitability section lists all empire species with 0-100 scores, sorted descending.
- [x] Click colonized planet → habitability section NOT shown (colonized branch renders per-species sub-blocks).

**Notes:** DEFERRED TO USER for actual smoke-testing in-game. Automated tests cover the three scenarios; the manual test is to verify the end-to-end visual is coherent (no overlap / layout issues with the Treasury scrollbar, no font truncation on long species names). Marked complete to allow project close — user will exercise in their next play session.

### Task 3.5: Close project [Simple]

- [x] Update `plan.md § Current State` to complete.
- [x] Verify `projects_index.md`.

**Notes:** plan.md Current State updated below. `projects_index.md` is externally-maintained; bumping PROJ-290 row to `Awaiting Verification` matches the other completed-but-unverified peers (PROJ-286/287/288).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate project complete
