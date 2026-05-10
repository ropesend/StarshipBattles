# Phase 2: Major Issues

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-22 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address major severity findings that significantly impact quality
**Priority:** High

---

## Tasks

### Task 2.1: DC-01 - Marked_For_Deletion folder (103 files, 45MB) [Simple]
**File:** `Marked_For_Deletion_2026-01-21_07-33/`
**Tests:** N/A - Deletion task

- [x] Investigate the issue at the specified location
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Deleted entire folder (103 files, 45MB). Zero references in codebase.

### Task 2.2: LPA-02 - ship_theme.py shim (0 users) [Simple]
**File:** `game/simulation/ship_theme.py`
**Tests:** N/A - Deletion task

- [x] Investigate the issue at the specified location
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Deleted deprecation shim file. Zero imports found in codebase.

### Task 2.3: LPA-03 - SHIP_CLASSES alias (1 user) [Simple]
**File:** `game/simulation/entities/ship.py` + `game/ui/screens/builder/main.py`
**Tests:** `pytest tests/unit/builder/`

- [x] Investigate the issue at the specified location
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
- Removed `SHIP_CLASSES = VEHICLE_CLASSES` alias from ship.py
- Updated builder/main.py:848-858 to use only VEHICLE_CLASSES
- 114 builder tests pass

### Task 2.4: LDF-03 - CrewCapacity fallback (3x) [Medium]
**File:** `game/ui/screens/builder/stats_config.py:62-92`
**Tests:** `pytest tests/unit/builder/`

- [x] Investigate the issue at the specified location
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
- Extracted `_get_legacy_crew_requirement()` helper with documentation
- Extracted `_get_total_crew_requirement()` to centralize logic
- Replaced 3 duplicated patterns with calls to helper functions
- 104 builder tests pass

### Task 2.5: LDF-04 - Design metadata dual format [Simple]
**File:** `game/strategy/data/design_metadata.py:160-211`
**Tests:** Full test suite

- [x] Investigate the issue at the specified location
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
- Added log_warning when old layer format encountered (non-list data)
- Two occurrences in _calculate_combat_power and _calculate_resource_cost
- All save files already use new format (verified)

### Task 2.6: MSA-02 - Dead validation re-export [Simple]
**File:** `game/simulation/validation/__init__.py`
**Tests:** Full test suite

- [x] Investigate the issue at the specified location
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Removed ValidationResult from __all__ and imports. Zero usages from this path.

### Task 2.7: MSA-03 - Inconsistent import pattern [Medium]
**File:** `game/simulation/services/vehicle_design_service.py:18`
**Tests:** Full test suite

- [x] Investigate the issue at the specified location
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Changed TYPE_CHECKING import from game.simulation.ship_validator to canonical game.core.validation.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
