# Phase 2: ShipInstance Cargo & Display Extraction [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-87 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract cargo operations and display formatting from ShipInstance

**File:** `game/strategy/data/ship_instance.py`
**New Files:** `game/strategy/data/ship_cargo_manager.py`, `game/strategy/data/ship_display_formatter.py`
**Tests:** `pytest tests/unit/strategy/ -n 4`

---

## Tasks

### Task 2.1: Create ShipCargoManager [Simple]
**File:** `game/strategy/data/ship_cargo_manager.py` (NEW)
**Tests:** `pytest tests/unit/strategy/test_ship_cargo_manager.py`
- [x] Create `ShipCargoManager` class with `__init__(self, ship_instance)`
- [x] Move `load_cargo()` from ShipInstance
- [x] Move `unload_cargo()` from ShipInstance
- [x] Move `get_cargo_space_available()` from ShipInstance
- [x] Move `get_cargo_capacity()` from ShipInstance
- [x] Move `get_current_cargo()` from ShipInstance
- [x] Wire ShipInstance: `self._cargo_mgr = ShipCargoManager(self)` + delegation wrappers

**Notes:** Created 112-line ShipCargoManager, 15 tests passing

### Task 2.2: Extract ShipDisplayFormatter [Simple]
**File:** `game/strategy/data/ship_display_formatter.py` (NEW)
**Tests:** `pytest tests/unit/strategy/test_ship_display_formatter.py`
- [x] Create `ShipDisplayFormatter` class (stateless, takes ShipInstance as parameter)
- [x] Move `get_status_text()` from ShipInstance
- [x] Move `get_hp_display()` from ShipInstance
- [x] Move `get_resource_display()` from ShipInstance
- [x] Move `get_resource_percentage()` from ShipInstance
- [x] Move `get_display_id()` from ShipInstance
- [x] Wire ShipInstance: `self._display = ShipDisplayFormatter(self)` + delegation wrappers
- [x] Find all callers of these methods and verify they still work via delegation

**Notes:** Created 109-line ShipDisplayFormatter, 16 tests passing

### Task 2.3: Write tests and verify [Simple]
- [x] Write tests for ShipCargoManager (load, unload, capacity checks)
- [x] Write tests for ShipDisplayFormatter (status text, HP display, resource display)
- [x] Run `pytest tests/unit/strategy/ -n 4` — all pass (159 tests)
- [x] Run `pytest tests/integration/strategy/ -n 4` — all pass
- [x] Verify ShipInstance line count reduced by ~80 additional lines (874→749, 125 lines saved)
- [x] Update plan.md Current State

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
