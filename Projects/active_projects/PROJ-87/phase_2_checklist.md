# Phase 2: ShipInstance Cargo & Display Extraction [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-87 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract cargo operations and display formatting from ShipInstance

**File:** `game/strategy/data/ship_instance.py`
**New Files:** `game/strategy/data/ship_cargo_manager.py`, `game/strategy/data/ship_display_formatter.py`
**Tests:** `pytest tests/unit/strategy/ -n 4`

---

## Tasks

### Task 2.1: Create ShipCargoManager [Simple]
**File:** `game/strategy/data/ship_cargo_manager.py` (NEW)
**Tests:** `pytest tests/unit/strategy/test_ship_cargo_manager.py`
- [ ] Create `ShipCargoManager` class with `__init__(self, ship_instance)`
- [ ] Move `load_cargo()` from ShipInstance
- [ ] Move `unload_cargo()` from ShipInstance
- [ ] Move `get_cargo_space_available()` from ShipInstance
- [ ] Move `get_cargo_capacity()` from ShipInstance
- [ ] Move `get_current_cargo()` from ShipInstance
- [ ] Wire ShipInstance: `self._cargo_mgr = ShipCargoManager(self)` + delegation wrappers

**Notes:**

### Task 2.2: Extract ShipDisplayFormatter [Simple]
**File:** `game/strategy/data/ship_display_formatter.py` (NEW)
**Tests:** `pytest tests/unit/strategy/test_ship_display_formatter.py`
- [ ] Create `ShipDisplayFormatter` class (stateless, takes ShipInstance as parameter)
- [ ] Move `get_status_text()` from ShipInstance
- [ ] Move `get_hp_display()` from ShipInstance
- [ ] Move `get_resource_display()` from ShipInstance
- [ ] Move `get_resource_percentage()` from ShipInstance
- [ ] Move `get_display_id()` from ShipInstance
- [ ] Wire ShipInstance: `self._display = ShipDisplayFormatter(self)` + delegation wrappers
- [ ] Find all callers of these methods and verify they still work via delegation

**Notes:** These methods are UI concerns in the data layer. Extracting makes the boundary explicit.

### Task 2.3: Write tests and verify [Simple]
- [ ] Write tests for ShipCargoManager (load, unload, capacity checks)
- [ ] Write tests for ShipDisplayFormatter (status text, HP display, resource display)
- [ ] Run `pytest tests/unit/strategy/ -n 4` — all pass
- [ ] Run `pytest tests/integration/strategy/ -n 4` — all pass
- [ ] Verify ShipInstance line count reduced by ~80 additional lines
- [ ] Update plan.md Current State

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
