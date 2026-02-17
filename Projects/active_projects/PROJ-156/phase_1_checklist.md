# Phase 1: Straight Deletes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-156 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete 9 test files that test no production code (mocks-on-mocks, local reimplementations, hasattr checks, empty scaffolds). ~1,393 lines removed.
**Priority:** Immediate

---

## Tasks

### Task 1.1: Delete dead test files [Simple]
**Tests:** `pytest tests/ -n 12` after all deletes
**Expected:** Test count drops by number of deleted test methods. 145 pre-existing failures unchanged.

- [ ] Delete `tests/unit/ai/controllable_interface/test_interface_definition.py` (259 lines - pure hasattr checks on IControllable ABC)
- [ ] Delete `tests/unit/combat/test_combat_endurance_edge_cases.py` (27 lines - empty scaffolds with `pass`)
- [ ] Delete `tests/unit/combat/test_targeting_edge_cases.py` (23 lines - import/hasattr checks only)
- [ ] Delete `tests/unit/ai/formation_prediction/test_other_behaviors.py` (164 lines - weaker copies of test_behavior_units.py)
- [ ] Delete `tests/unit/research/research_controls/test_handle_event.py` (274 lines - zero production code, tests mocks)
- [ ] Delete `tests/unit/research/research_controls/test_event_formatting.py` (182 lines - zero production code, tests inline strings)
- [ ] Delete `tests/unit/research/research_controls/test_node_selection.py` (113 lines - zero production code, tests arithmetic)
- [ ] Delete `tests/unit/combat/test_lead.py` (143 lines - tests local `solve_lead()` reimplementation, not production)
- [ ] Delete `tests/unit/combat/test_ccd.py` (208 lines - tests local `check_collision()`, NOT `engine/collision_edge_cases/test_ccd.py`)

### Task 1.2: Check for orphaned directories [Simple]
**Tests:** N/A (directory check only)

- [ ] Check `tests/unit/research/research_controls/` - if no test files remain after deleting 3 files, remove `conftest.py`, `__init__.py`, and the directory
- [ ] Check `tests/unit/ai/formation_prediction/` - confirm other test files still exist (e.g., `test_formation_behavior.py`). Do NOT delete this directory.

### Task 1.3: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite
- [ ] Verify: no new failures beyond the 145 pre-existing ones
- [ ] Record new passed count (should be ~12,788 minus deleted test methods)

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
