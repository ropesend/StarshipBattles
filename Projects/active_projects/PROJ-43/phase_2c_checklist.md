# Phase 2C: UI-Simulation Decoupling - Workshop & Battle Screens

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-43 2c`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress
**Objective:** Remove direct simulation imports from workshop and battle screens

---

## Prerequisites
- [x] Phase 2B complete

## Tasks

### Task 2C.1: Create Ship IO Adapter [Simple]
**File:** `game/ui/services/ship_io_adapter.py` (NEW)
**Tests:** `pytest tests/unit/ui/services/test_ship_io_adapter.py`

- [ ] Create `ShipIOAdapter` class wrapping ShipIO:
  - `set_ships_folder(folder_path)` - configure folder
  - `save_ship(ship) -> (bool, str)` - save ship design
  - `load_ship(width, height) -> (Ship, str)` - load ship design
- [ ] Inject actual ShipIO via constructor for testability
- [ ] Create unit tests with mock ShipIO

**Notes:**

---

### Task 2C.2: Create Design Loader Adapter [Simple]
**File:** `game/ui/services/design_loader_adapter.py` (NEW)
**Tests:** `pytest tests/unit/ui/services/test_design_loader_adapter.py`

- [ ] Create `DesignLoaderAdapter` class wrapping SimulationDesignLoader:
  - `load_ship_from_design_data(design_data, width, height) -> Ship`
- [ ] Inject actual loader via constructor for testability
- [ ] Create unit tests with mock loader

**Notes:**

---

### Task 2C.3: Update workshop_screen.py [Medium]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_workshop*.py tests/integration/test_workshop*.py`

**Current imports to remove:**
- Lines 18-19: `from game.simulation.components.component import get_all_components`
- Line 22: `from game.simulation.systems.persistence import ShipIO`
- Line 38: `from game.simulation.services.design_loader import SimulationDesignLoader`

**Changes:**
- [ ] Add imports for new adapters
- [ ] Remove simulation imports (lines 18-19, 22, 38)
- [ ] Update `__init__()` to accept adapters via context/constructor
- [ ] Replace `get_all_components()` (line 605) with viewmodel access
- [ ] Replace `ShipIO.default_ships_folder` assignments (lines 552, 560) with adapter
- [ ] Replace `ShipIO.save_ship()` (line 666) with adapter
- [ ] Replace `ShipIO.load_ship()` (lines 715, 869) with adapter
- [ ] Replace `SimulationDesignLoader()` instantiation (lines 759, 885) with adapter

**Notes:**

---

### Task 2C.4: Verify workshop_viewmodel.py [Simple]
**File:** `game/ui/screens/workshop_viewmodel.py`
**Tests:** `pytest tests/unit/ui/screens/test_workshop_viewmodel.py`

**Current state:**
- Line 16: `from game.simulation.services.vehicle_design_service import VehicleDesignService` (runtime)
- Lines 22-24: TYPE_CHECKING imports (already decoupled)

**Changes:**
- [ ] Verify VehicleDesignService import is acceptable (service pattern)
- [ ] Verify TYPE_CHECKING imports are properly guarded
- [ ] Document that this import is intentional (service layer)
- [ ] No changes needed if pattern is acceptable

**Notes:** VehicleDesignService is already an abstraction - may not need changes.

---

### Task 2C.5: Verify battle_scene.py [Simple]
**File:** `game/ui/screens/battle_scene.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle*.py`

**Current state:**
- Line 23: `from game.simulation.services.battle_service import BattleService` (runtime)
- Lines 26-27: TYPE_CHECKING imports (already decoupled)

**Changes:**
- [ ] Verify BattleService import is acceptable (abstraction layer)
- [ ] Verify no direct BattleEngine imports exist
- [ ] Document that BattleService is intentional facade
- [ ] No changes needed if pattern is acceptable

**Notes:** BattleService is already a proper abstraction layer.

---

### Task 2C.6: Integration Testing [Simple]
**Tests:** `pytest tests/integration/test_workshop*.py tests/integration/test_battle*.py`

- [ ] Run workshop integration tests
- [ ] Run battle integration tests
- [ ] Verify workshop ship save/load works
- [ ] Verify design library loading works
- [ ] Verify battle scene initialization works
- [ ] Run full test suite

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] workshop_screen.py has no direct simulation imports (uses adapters)
- [ ] workshop_viewmodel.py and battle_scene.py verified (service imports acceptable)
- [ ] All tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
