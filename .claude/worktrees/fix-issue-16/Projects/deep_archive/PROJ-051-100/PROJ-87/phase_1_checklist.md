# Phase 1: ShipInstance Resource Extraction [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-87 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract ShipResourceManager to centralize 13 resource methods (~166 lines)

**File:** `game/strategy/data/ship_instance.py`
**New File:** `game/strategy/data/ship_resource_manager.py`
**Tests:** `pytest tests/unit/strategy/ -n 4`

---

## Tasks

### Task 1.1: Create ShipResourceManager class [Medium]
**File:** `game/strategy/data/ship_resource_manager.py` (NEW)
**Tests:** `pytest tests/unit/strategy/test_ship_resource_manager.py`
- [x] Create `ShipResourceManager` class with `__init__(self, ship_instance)` taking a reference to the owning ShipInstance
- [x] Move `get_current_fuel()` from ShipInstance (line ~256)
- [x] Move `consume_fuel()` from ShipInstance (line ~267)
- [x] Move `get_current_energy()` from ShipInstance (line ~308)
- [x] Move `consume_energy()` from ShipInstance (line ~319)
- [x] Move `get_current_resource()` from ShipInstance
- [x] Move `consume_resource()` from ShipInstance
- [x] Move `get_resource_capacity()` from ShipInstance (line ~342)
- [x] Move `resupply()` from ShipInstance
- [x] Verify resource_levels dict is owned by ShipInstance but accessed by manager

**Notes:** Created ship_resource_manager.py with all resource methods extracted

### Task 1.2: Extract cost calculation methods [Simple]
**File:** `game/strategy/data/ship_resource_manager.py`
- [x] Move `get_fuel_cost_per_hex()` from ShipInstance (line ~246)
- [x] Move `get_warp_energy_cost()` from ShipInstance
- [x] Move `get_warp_fuel_cost()` from ShipInstance
- [x] Move `get_all_resource_costs_per_hex()` from ShipInstance
- [x] Move `get_all_resource_costs_per_turn()` from ShipInstance
- [x] Move `get_warp_resource_costs()` from ShipInstance

**Notes:** All cost methods extracted and delegated

### Task 1.3: Wire ShipInstance to delegate to ShipResourceManager [Medium]
**File:** `game/strategy/data/ship_instance.py`
- [x] Add `self._resource_mgr = ShipResourceManager(self)` in `__init__`
- [x] Replace each extracted method with thin delegation wrapper
- [x] Ensure `to_dict()` / `from_dict()` serialization still works (resource_levels dict)
- [x] Ensure `from_ship()` factory method initializes resources correctly
- [x] Run `pytest tests/unit/strategy/ -n 4` — all pass

**Notes:** Used __post_init__ for dataclass initialization. All 1414 strategy tests pass.

### Task 1.4: Write dedicated tests for ShipResourceManager [Simple]
**File:** `tests/unit/strategy/test_ship_resource_manager.py` (NEW)
- [x] Test fuel consumption and tracking
- [x] Test energy consumption and tracking
- [x] Test generic resource operations
- [x] Test cost calculations
- [x] Test resupply
- [x] Run `pytest tests/unit/strategy/test_ship_resource_manager.py` — all pass

**Notes:** 26 tests written using TDD approach with mock ShipInstance

### Task 1.5: Phase 1 Verification [Simple]
- [x] Run `pytest tests/unit/strategy/ -n 4` — 1414 passed
- [x] Run `pytest tests/integration/strategy/ -n 4` — 346 passed
- [x] Verify ShipInstance line count reduced by ~166 lines (923→873, 50 lines)
- [x] Verify ShipResourceManager is standalone and testable (252 lines, 26 tests)
- [x] Update plan.md Current State

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

**Implementation Notes:**
- ShipInstance reduced from 923 to 873 lines (50 line reduction)
- ShipResourceManager is 252 lines with full test coverage (26 tests)
- Used facade pattern - ShipInstance methods delegate to _resource_mgr
- resource_levels dict stays on ShipInstance, manager accesses via reference
- All existing tests pass, no import chain breakage
