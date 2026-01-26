# Phase 3: ShipBuilderService Shim [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-15 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove VehicleDesignService alias and update callers

---

## Tasks

### Task 3.1: Update workshop_viewmodel.py [Medium]
**File:** `game/ui/screens/workshop_viewmodel.py`
**Tests:** `pytest tests/unit/builder/test_builder_viewmodel.py -v`

- [x] Line 14: Change import from ShipBuilderService to VehicleDesignService
- [x] Update all `ShipBuilderService` references to `VehicleDesignService`
- [x] Update all `ShipBuilderResult` type annotations to `DesignResult`
- [x] Verify: File compiles without errors

**Notes:** 4 changes made: import, constructor, and 2 type annotations

---

### Task 3.2: Update services __init__.py [Simple]
**File:** `game/simulation/services/__init__.py`
**Tests:** `pytest tests/unit/services/ -v`

- [x] Update import from ship_builder_service to vehicle_design_service
- [x] Update `__all__` to export `VehicleDesignService`, `DesignResult` instead of old names

**Notes:**

---

### Task 3.3: Handle test file [Simple]
**File:** `tests/unit/services/test_ship_builder_service.py`

- [x] DELETED - This file was a duplicate of test_vehicle_design_service.py (both 292 lines)
- [x] test_vehicle_design_service.py already tests the canonical API with the new names

**Notes:** Instead of updating, deleted the redundant test file since identical tests exist in test_vehicle_design_service.py

---

### Task 3.4: Delete Shim File [Simple]
**File:** `game/simulation/services/ship_builder_service.py`
**Tests:** `pytest tests/unit/services/ tests/unit/builder/ -v`

- [x] Delete file: `game/simulation/services/ship_builder_service.py`
- [x] Verify: No import errors when running `python -c "from game.simulation.services import VehicleDesignService"`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] No remaining ShipBuilderService references (only docstring comments mentioning rename history)
- [x] ship_builder_service.py is deleted
- [x] Run: `pytest tests/unit/services/ tests/unit/builder/ -v` - 187 tests pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
