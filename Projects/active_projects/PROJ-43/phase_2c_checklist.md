# Phase 2C: UI-Simulation Decoupling - Workshop & Battle Screens

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-43 2c`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove direct simulation imports from workshop and battle screens

---

## Prerequisites
- [x] Phase 2B complete

## Tasks

### Task 2C.1: Create Ship IO Adapter [Simple]
**File:** `game/ui/services/ship_io_adapter.py` (NEW)
**Tests:** `pytest tests/unit/ui/services/test_ship_io_adapter.py`

- [x] Create `ShipIOAdapter` class wrapping ShipIO:
  - `set_ships_folder(folder_path)` - configure folder
  - `save_ship(ship) -> (bool, str)` - save ship design
  - `load_ship(width, height) -> (Ship, str)` - load ship design
- [x] Inject actual ShipIO via constructor for testability
- [x] Create unit tests with mock ShipIO

**Notes:** Created ShipIOAdapter with 8 unit tests (all passing). Added `get_ships_folder()` method for completeness. Added to `game/ui/services/__init__.py` exports.

---

### Task 2C.2: Create Design Loader Adapter [Simple]
**File:** `game/ui/services/design_loader_adapter.py` (NEW)
**Tests:** `pytest tests/unit/ui/services/test_design_loader_adapter.py`

- [x] Create `DesignLoaderAdapter` class wrapping SimulationDesignLoader:
  - `load_ship_from_design_data(design_data, width, height) -> Ship`
- [x] Inject actual loader via constructor for testability
- [x] Create unit tests with mock loader

**Notes:** Created DesignLoaderAdapter with 6 unit tests (all passing). Also added `load_ship_from_file()` method. Added to `game/ui/services/__init__.py` exports.

---

### Task 2C.3: Update workshop_screen.py [Medium]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_workshop*.py tests/integration/test_workshop*.py`

**Current imports to remove:**
- Lines 18-19: `from game.simulation.components.component import get_all_components`
- Line 22: `from game.simulation.systems.persistence import ShipIO`
- Line 38: `from game.simulation.services.design_loader import SimulationDesignLoader`

**Changes:**
- [x] Add imports for new adapters
- [x] Remove simulation imports (lines 18-19, 22, 38)
- [x] Update `__init__()` to accept adapters via context/constructor
- [x] Replace `get_all_components()` (line 605) with viewmodel access
- [x] Replace `ShipIO.default_ships_folder` assignments (lines 552, 560) with adapter
- [x] Replace `ShipIO.save_ship()` (line 666) with adapter
- [x] Replace `ShipIO.load_ship()` (lines 715, 869) with adapter
- [x] Replace `SimulationDesignLoader()` instantiation (lines 759, 885) with adapter

**Notes:** Removed all 3 simulation imports. Added ShipIOAdapter and DesignLoaderAdapter instances created in `__init__()`. Replaced all usages with adapter calls. Workshop tests pass (37 tests).

---

### Task 2C.4: Verify workshop_viewmodel.py [Simple]
**File:** `game/ui/screens/workshop_viewmodel.py`
**Tests:** `pytest tests/unit/ui/screens/test_workshop_viewmodel.py`

**Current state:**
- Line 16: `from game.simulation.services.vehicle_design_service import VehicleDesignService` (runtime)
- Lines 22-24: TYPE_CHECKING imports (already decoupled)

**Changes:**
- [x] Verify VehicleDesignService import is acceptable (service pattern)
- [x] Verify TYPE_CHECKING imports are properly guarded
- [x] Document that this import is intentional (service layer)
- [x] No changes needed if pattern is acceptable

**Notes:** VERIFIED - VehicleDesignService is a proper service abstraction layer ("Provides an abstraction layer between UI and Ship domain objects"). It accepts dependency injection via registries parameter (PROJ-38). TYPE_CHECKING imports (Ship, LayerType, Component, DesignResult) are properly guarded. No changes needed.

---

### Task 2C.5: Verify battle_scene.py [Simple]
**File:** `game/ui/screens/battle_scene.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle*.py`

**Current state:**
- Line 23: `from game.simulation.services.battle_service import BattleService` (runtime)
- Lines 26-27: TYPE_CHECKING imports (already decoupled)

**Changes:**
- [x] Verify BattleService import is acceptable (abstraction layer)
- [x] Verify no direct BattleEngine imports exist
- [x] Document that BattleService is intentional facade
- [x] No changes needed if pattern is acceptable

**Notes:** VERIFIED - BattleService is a proper abstraction ("Provides an abstraction between the UI and BattleEngine"). No direct BattleEngine imports exist. TYPE_CHECKING imports (BattleController, BattleConfig, Ship) are properly guarded. No changes needed.

---

### Task 2C.6: Integration Testing [Simple]
**Tests:** `pytest tests/integration/test_workshop*.py tests/integration/test_battle*.py`

- [x] Run workshop integration tests
- [x] Run battle integration tests
- [x] Verify workshop ship save/load works
- [x] Verify design library loading works
- [x] Verify battle scene initialization works
- [x] Run full test suite

**Notes:** Full test suite: 5249 passed, 3 skipped (up from 5235 due to 14 new adapter tests). Fixed 5 failing tests in test_builder_io_integration.py and test_builder_improvements.py that were patching removed ShipIO import.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] workshop_screen.py has no direct simulation imports (uses adapters)
- [x] workshop_viewmodel.py and battle_scene.py verified (service imports acceptable)
- [x] All tests pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
