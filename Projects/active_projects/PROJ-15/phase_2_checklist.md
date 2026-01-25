# Phase 2: Fleet Warp Method Aliases [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-15 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove deprecated energy-based naming in favor of resource-based naming

---

## Tasks

### Task 2.1: Remove Warp Aliases [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet.py -v`

- [ ] `game/strategy/data/fleet.py` - Delete lines 350-360: `has_energy_for_warp()` method
- [ ] `game/strategy/data/fleet.py` - Delete lines 392-403: `consume_warp_energy()` method
- [ ] Verify: Grep for remaining usages: `grep -r "has_energy_for_warp\|consume_warp_energy" game/ --include="*.py"`

**Notes:**

---

### Task 2.2: Delete Backward Compatibility Tests [Simple]
**File:** `tests/unit/strategy/test_fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet.py -v`

- [ ] `tests/unit/strategy/test_fleet.py` - Delete lines 871-930: Class `TestBackwardCompatibility`
  - This class explicitly tests the deprecated aliases we're removing
- [ ] Verify: Run `pytest tests/unit/strategy/test_fleet.py -v` - all tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No remaining warp energy references: `grep -r "energy_for_warp\|warp_energy" game/ tests/ --include="*.py" | grep -v __pycache__`
- [ ] Run: `pytest tests/unit/strategy/test_fleet.py -v`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
