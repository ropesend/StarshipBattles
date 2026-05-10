# Phase 5: Maintenance System

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-75 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Deduct 5% of build cost per turn, scuttle on failure

---

## Tasks

### Task 5.1: Write TDD tests for MaintenanceEngine [Medium]
**File:** `tests/unit/strategy/engine/test_maintenance_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_maintenance_engine.py -v`

- [x] Create test file with TestMaintenanceEngine class
- [x] Test: maintenance cost = 5% of total build cost
- [x] Test: successful payment deducts from empire pool
- [x] Test: facility scuttled when payment fails
- [x] Test: ship scuttled when payment fails
- [x] Test: multiple facilities - all checked in one pass
- [x] Test: scuttle cascade prevented (one-pass processing)
- [x] Test: non-operational facilities have no maintenance
- [x] Test: scuttle events returned for notification

**Notes:** 17 unit tests covering cost calculation, facility maintenance, ship maintenance, scuttling, cascade prevention, and edge cases.

---

### Task 5.2: Create MaintenanceEngine class [Medium]
**File:** `game/strategy/engine/maintenance_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_maintenance_engine.py -v`

- [x] Create `MaintenanceEngine` class with MAINTENANCE_RATE = 0.05
- [x] Implement `_process_empire(empire) -> List[ScuttleEvent]`
- [x] Implement `_calculate_maintenance_cost(design_data) -> Dict[str, float]`
- [x] Implement facility and ship maintenance checking
- [x] Implement scuttling logic (remove from lists)

**Notes:** Handles both layer formats (dict with "components" key and direct list format). Registries parameter removed as unnecessary for maintenance calculation.

---

### Task 5.3: Implement scuttling logic [Medium]
**File:** `game/strategy/engine/maintenance_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_maintenance_engine.py -v`

- [x] Scuttling integrated into `_process_colony_facilities` and `_process_fleet_ships` (batch removal after iteration)
- [x] ScuttleEvent returned for each scuttled entity
- [x] `_cleanup_empty_fleets(empire, fleets_with_scuttles)` removes only fleets emptied by scuttling

**Notes:** Cleanup only removes fleets that had ships scuttled (not pre-existing empty fleets), preventing unintended fleet deletion.

---

### Task 5.4: Integrate MaintenanceEngine into TurnEngine [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/integration/strategy/turn_engine/test_maintenance.py -v`

- [x] Write integration test in `tests/integration/strategy/turn_engine/test_maintenance.py` (NEW)
- [x] Add `_maintenance_engine` property with lazy initialization
- [x] Call after harvesting, before per-turn consumption (Phase 0b in process_turn)
- [x] Added IMaintenanceEngine interface to engines.py
- [x] Added MockMaintenanceEngine to mock_engines.py
- [x] Updated test_engine_interfaces.py with 4 new interface tests + 1 concrete impl test + 1 __all__ check

**Notes:** 6 integration tests verifying DI, call ordering, real maintenance deduction, and scuttling through TurnEngine.

---

### Task 5.5: Add ship maintenance [Medium]
**File:** `game/strategy/engine/maintenance_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_maintenance_engine.py -v`

- [x] Iterate empire.fleets -> ships
- [x] Calculate ship maintenance from design_data
- [x] Deduct from empire pool or scuttle ship
- [x] Handle fleet becoming empty after scuttles

**Notes:** Ship maintenance integrated into MaintenanceEngine alongside facility maintenance. Empty fleet cleanup only targets fleets with scuttled ships.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6
