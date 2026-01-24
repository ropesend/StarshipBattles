# Phase 4: Refactor Fleet Mobility Service

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-07 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update Fleet Mobility Service to use calculated stats

---

## Tasks

### Task 4.1: Update calculate_ship_speed [Simple]
**File:** `game/strategy/services/fleet_mobility_service.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_mobility_service.py`

- [x] Refactor `calculate_ship_speed()` to use `ship_instance.get_calculated_stats()`

**Notes:** Simple one-line change from expected_stats to get_calculated_stats().

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
