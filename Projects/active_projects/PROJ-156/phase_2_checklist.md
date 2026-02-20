# Phase 2: Partial Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-156 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Mostly Complete (4 of 6 tasks done by PROJ-157, Task 2.5 remains)
**Objective:** Remove empty stubs, trivial constant checks, and duplicate classes from within existing files. ~220 lines removed.
**Priority:** High

---

## Tasks

### Task 2.1: Remove empty stubs from test_bulk_add.py [Simple]
**File:** `tests/unit/builder/test_bulk_add.py`
**Tests:** `pytest tests/unit/builder/test_bulk_add.py -v`

- [x] Remove `test_bulk_add_with_limit` method (lines 32-58, has setup but body is `pass`)
- [x] Remove `test_bulk_performance_mock` method (lines 60-63, entirely `pass`)
- [x] Keep `test_bulk_add_success` (lines 9-30, real test)
- [x] Verify: file still runs, `test_bulk_add_success` passes

**Notes:** Done by PROJ-157.

### Task 2.2: Remove empty class from test_ship_loading.py [Simple]
**File:** `tests/unit/builder/test_ship_loading.py`
**Tests:** `pytest tests/unit/builder/test_ship_loading.py -v`

- [x] Remove `class TestShipExpectedStats: pass` (lines 77-79)
- [x] Keep `TestModifierStacking` and `TestAllShipDesigns` classes
- [x] Verify: file still runs, remaining tests pass

**Notes:** Done by PROJ-157.

### Task 2.3: Remove migration check class from test_allowed_layers_removal.py [Simple]
**File:** `tests/unit/systems/test_allowed_layers_removal.py`
**Tests:** `pytest tests/unit/systems/test_allowed_layers_removal.py -v`

- [x] Remove `TestAllowedLayersRemoval` class (lines 19-70, 5 tests checking attribute was removed - one-time migration)
- [x] Keep `TestBuilderDropValidation` class (lines 73-136, ongoing validator tests)
- [x] Keep any fixtures used by TestBuilderDropValidation
- [x] Verify: `TestBuilderDropValidation` tests still pass

**Notes:** Done by PROJ-157. PROJ-157 left a comment documenting the removal.

### Task 2.4: Remove duplicate classes from test_validation.py [Simple]
**File:** `tests/unit/research/tech_tree/test_validation.py`
**Tests:** `pytest tests/unit/research/tech_tree/test_validation.py -v`

- [x] Remove `TestDetectCycles` class (lines 130-286) - duplicated by `test_cycle_detection.py` which has 5 specialized classes
- [x] Remove `TestDepthCalculation` class (lines 371-407) - duplicated by `test_queries.py::TestTechTreeDepthCalculation`
- [x] Keep `TestValidateRequirements` (lines 17-128)
- [x] Keep `TestValidate` (lines 288-368)
- [x] Keep `TestEdgeCases` (lines 410-454)
- [x] Verify: remaining 3 classes pass

**Notes:** Done by PROJ-157. PROJ-157 left a comment documenting the removal.

### Task 2.5: Remove TestLayoutConstants from 2 files [Simple] ⚠️ NOT DONE
**File 1:** `tests/unit/research/research_scene/test_initialization.py`
**File 2:** `tests/unit/ui/panels/test_empire_treasury_panel.py`
**Tests:** `pytest tests/unit/research/research_scene/test_initialization.py tests/unit/ui/panels/test_empire_treasury_panel.py -v`

- [ ] Remove `TestLayoutConstants` class from `test_initialization.py` (lines 264-286, 4 tests asserting constants `> 0`)
- [ ] Remove `TestLayoutConstants` class from `test_empire_treasury_panel.py` (lines 322-342, 4 tests asserting range bounds)
- [ ] Verify: remaining tests in both files pass

**Notes:** NOT completed by PROJ-157. Both `TestLayoutConstants` classes still exist with their original trivial checks (`> 0`, range bounds). These are the original stubs, not replacements.

### Task 2.6: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite
- [ ] Verify: no new failures beyond pre-existing ones
- [ ] Record new passed count

**Notes:** Run after Task 2.5 is completed.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
