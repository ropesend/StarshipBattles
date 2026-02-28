# Phase 1: Straight Deletes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-156 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (done by PROJ-157)
**Objective:** Delete 9 test files that test no production code (mocks-on-mocks, local reimplementations, hasattr checks, empty scaffolds). ~1,393 lines removed.
**Priority:** Immediate

---

## Tasks

### Task 1.1: Delete dead test files [Simple]
**Tests:** `pytest tests/ -n 12` after all deletes
**Expected:** Test count drops by number of deleted test methods. 145 pre-existing failures unchanged.

- [x] Delete `tests/unit/ai/controllable_interface/test_interface_definition.py` (259 lines - pure hasattr checks on IControllable ABC)
- [x] Delete `tests/unit/combat/test_combat_endurance_edge_cases.py` (27 lines - empty scaffolds with `pass`)
- [x] Delete `tests/unit/combat/test_targeting_edge_cases.py` (23 lines - import/hasattr checks only)
- [x] Delete `tests/unit/ai/formation_prediction/test_other_behaviors.py` (164 lines - weaker copies of test_behavior_units.py)
- [x] Delete `tests/unit/research/research_controls/test_handle_event.py` (274 lines - zero production code, tests mocks)
- [x] Delete `tests/unit/research/research_controls/test_event_formatting.py` (182 lines - zero production code, tests inline strings)
- [x] Delete `tests/unit/research/research_controls/test_node_selection.py` (113 lines - zero production code, tests arithmetic)
- [x] Delete `tests/unit/combat/test_lead.py` (143 lines - tests local `solve_lead()` reimplementation, not production)
- [x] Delete `tests/unit/combat/test_ccd.py` (208 lines - tests local `check_collision()`, NOT `engine/collision_edge_cases/test_ccd.py`)

**Notes:** All 9 files confirmed deleted by PROJ-157.

### Task 1.2: Check for orphaned directories [Simple]
**Tests:** N/A (directory check only)

- [x] Check `tests/unit/research/research_controls/` - `test_reset_state.py` remains, directory kept correctly
- [x] Check `tests/unit/ai/formation_prediction/` - `test_formation_behavior.py` still exists. Directory kept correctly.

**Notes:** Both directories retain real test files, no orphan cleanup needed.

### Task 1.3: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite
- [x] Verify: no new failures beyond the 145 pre-existing ones
- [x] Record new passed count (should be ~12,788 minus deleted test methods)

**Notes:** Verified as part of PROJ-157 audit. Post-PROJ-157 baseline: 12,185 collected.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
