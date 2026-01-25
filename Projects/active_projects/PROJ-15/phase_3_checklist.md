# Phase 3: ShipBuilderService Shim [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-15 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove VehicleDesignService alias and update callers

---

## Tasks

### Task 3.1: Update workshop_viewmodel.py [Medium]
**File:** `game/ui/screens/workshop_viewmodel.py`
**Tests:** `pytest tests/unit/builder/test_builder_viewmodel.py -v`

- [ ] Line 14: Change import:
  ```python
  # FROM:
  from game.simulation.services import ShipBuilderService, ShipBuilderResult
  # TO:
  from game.simulation.services.vehicle_design_service import VehicleDesignService, DesignResult
  ```
- [ ] Update all `ShipBuilderService` references to `VehicleDesignService`
- [ ] Update all `ShipBuilderResult` type annotations to `DesignResult`
- [ ] Verify: File compiles without errors

**Notes:**

---

### Task 3.2: Update services __init__.py [Simple]
**File:** `game/simulation/services/__init__.py`
**Tests:** `pytest tests/unit/services/ -v`

- [ ] Update import:
  ```python
  # FROM:
  from .ship_builder_service import ShipBuilderService, ShipBuilderResult
  # TO:
  from .vehicle_design_service import VehicleDesignService, DesignResult
  ```
- [ ] Update `__all__` to export `VehicleDesignService`, `DesignResult` instead of old names

**Notes:**

---

### Task 3.3: Update test file [Simple]
**File:** `tests/unit/services/test_ship_builder_service.py`
**Tests:** `pytest tests/unit/services/test_ship_builder_service.py -v`

- [ ] Line 9: Change import:
  ```python
  # FROM:
  from game.simulation.services.ship_builder_service import ShipBuilderService, ShipBuilderResult
  # TO:
  from game.simulation.services.vehicle_design_service import VehicleDesignService, DesignResult
  ```
- [ ] Update test class to use new names (or keep aliases for test readability)
- [ ] Verify: Tests pass with new imports

**Notes:**

---

### Task 3.4: Delete Shim File [Simple]
**File:** `game/simulation/services/ship_builder_service.py`
**Tests:** `pytest tests/unit/services/ tests/unit/builder/ -v`

- [ ] Delete file: `game/simulation/services/ship_builder_service.py`
- [ ] Verify: No import errors when running `python -c "from game.simulation.services import VehicleDesignService"`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No remaining ShipBuilderService references: `grep -r "ShipBuilderService\|ShipBuilderResult" game/ --include="*.py" | grep -v __pycache__`
- [ ] ship_builder_service.py is deleted
- [ ] Run: `pytest tests/unit/services/ tests/unit/builder/ -v`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
