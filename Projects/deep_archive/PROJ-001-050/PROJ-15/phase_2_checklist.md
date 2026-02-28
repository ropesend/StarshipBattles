# Phase 2: Fleet Warp Method Aliases [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-15 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove deprecated energy-based naming in favor of resource-based naming

---

## Tasks

### Task 2.1: Remove Warp Aliases [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet.py -v`

- [x] `game/strategy/data/fleet.py` - Delete lines 350-360: `has_energy_for_warp()` method
- [x] `game/strategy/data/fleet.py` - Delete lines 392-403: `consume_warp_energy()` method
- [x] Verify: Grep for remaining usages: `grep -r "has_energy_for_warp\|consume_warp_energy" game/ --include="*.py"` - none found

**Notes:** Both alias methods removed. They were simple wrappers around the canonical methods.

---

### Task 2.2: Delete Backward Compatibility Tests [Simple]
**File:** `tests/unit/strategy/test_fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet.py -v`

- [x] `tests/unit/strategy/test_fleet.py` - Remove tests that used removed aliases:
  - `test_backward_compat_has_energy_for_warp_wrapper`
  - `test_backward_compat_consume_warp_energy_wrapper`
  - `test_backward_compat_legacy_warp_methods_still_work`
- [x] Kept `test_backward_compat_consume_fleet_fuel_wrapper` (tests a different method, not an alias)
- [x] Verify: Run `pytest tests/unit/strategy/test_fleet.py -v` - all 73 tests pass

**Notes:** Retained TestBackwardCompatibility class with remaining fuel test. The `warp_energy_cost` property references in other files are legitimate data fields, not the deprecated method aliases.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] No remaining warp alias method references: `grep -r "has_energy_for_warp\|consume_warp_energy" game/ tests/ --include="*.py"` - none found
- [x] Run: `pytest tests/unit/strategy/test_fleet.py -v` - 73 tests pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
