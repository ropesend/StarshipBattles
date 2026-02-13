# Phase 4: Centralize SimulationDesignLoader Access

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-106 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Route all UI-layer SimulationDesignLoader usage through the existing `DesignLoaderAdapter`. Currently 4 UI files bypass the adapter and import SimulationDesignLoader directly.

---

## Context

`game/ui/services/design_loader_adapter.py` already exists as the proper UI-layer facade for SimulationDesignLoader (created in PROJ-43). However, several UI files still import SimulationDesignLoader directly:

1. **strategy_screen.py** -- 3 separate methods create `SimulationDesignLoader(registries=get_default_registries())` locally (lines 425/438, 543/556, 587/600)
2. **build_queue_screen.py** -- TYPE_CHECKING import of SimulationDesignLoader (line 39), accepts as constructor param (line 53)
3. **build_queue_controller.py** -- TYPE_CHECKING import of SimulationDesignLoader (line 26), accepts as constructor param (line 57)

The TYPE_CHECKING imports in build_queue_screen.py and build_queue_controller.py are for type hints on DI parameters. These are acceptable since they don't create runtime coupling, but we can improve them by accepting a protocol/ABC instead.

### Design Decision
- **strategy_screen.py**: Refactor to create DesignLoaderAdapter once and reuse, eliminating 3 separate SimulationDesignLoader instantiations
- **build_queue_screen/controller**: Keep DI pattern but switch type hint to use the adapter type or a protocol

---

## Tasks

### Task 4.1: Refactor strategy_screen.py Build Queue Creation [Medium]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/unit/ui/ tests/integration/ui/ -v -k strategy`

strategy_screen.py creates `SimulationDesignLoader(registries=get_default_registries())` in three places:
- `_open_planet_build_queue()` (lines 425, 438)
- `_open_entity_build_queue()` (lines 543, 556)
- `_open_fleet_build_queue()` (lines 587, 600)

- [x] Add `from game.ui.services.design_loader_adapter import DesignLoaderAdapter` to imports
- [x] Create a helper method `_create_design_loader(self)` that returns `DesignLoaderAdapter()` -- NOT NEEDED: Direct inline use is cleaner
- [x] In `_open_planet_build_queue()`: Remove local `from game.simulation.services.design_loader import SimulationDesignLoader` and `from game.core.registry import get_default_registries`
- [x] Replace `design_loader = SimulationDesignLoader(registries=get_default_registries())` with `design_loader = DesignLoaderAdapter()`
- [x] Repeat for `_open_entity_build_queue()` (lines 543-556)
- [x] Repeat for `_open_fleet_build_queue()` (lines 587-600)
- [x] NOTE: BuildQueueScreen/Controller accept design_loader as a parameter. DesignLoaderAdapter wraps SimulationDesignLoader, so we need to ensure the downstream code uses the adapter's API (load_ship_from_design_data, load_ship_from_file) which matches

**Important compatibility check:**
- [x] Verify BuildQueueController uses `design_loader.load_ship_from_design_data()` or similar -- if it calls SimulationDesignLoader-specific methods, the adapter must expose them
- [x] If BuildQueueController calls methods not on DesignLoaderAdapter, add them to the adapter -- N/A, only uses load_ship_from_design_data
- [x] Run tests: `pytest tests/unit/ui/ tests/integration/ui/ -v -k "strategy or build_queue"`

---

### Task 4.2: Update build_queue_screen.py Type Hints [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/ -v`

- [x] Line 39: Replace `from game.simulation.services.design_loader import SimulationDesignLoader` (TYPE_CHECKING) with `from game.ui.services.design_loader_adapter import DesignLoaderAdapter`
- [x] Line 53: Change type hint from `'SimulationDesignLoader'` to `'DesignLoaderAdapter'`
- [x] Line 69: Update docstring to reference DesignLoaderAdapter
- [x] Run tests: `pytest tests/integration/ui/build_queue_screen/ -v`

---

### Task 4.3: Update build_queue_controller.py Type Hints [Simple]
**File:** `game/ui/panels/build_queue_controller.py`
**Tests:** `pytest tests/unit/ui/ -v -k build_queue`

- [x] Line 26: Replace `from game.simulation.services.design_loader import SimulationDesignLoader` (TYPE_CHECKING) with `from game.ui.services.design_loader_adapter import DesignLoaderAdapter`
- [x] Line 57: Change type hint from `'SimulationDesignLoader'` to `'DesignLoaderAdapter'`
- [x] Line 71: Update docstring to reference DesignLoaderAdapter
- [x] Verify all methods on design_loader called by BuildQueueController exist on DesignLoaderAdapter
- [x] Run tests: `pytest tests/unit/ui/ -v -k build_queue`

---

### Task 4.4: Verify No Direct SimulationDesignLoader Imports in UI [Simple]

- [x] Grep for `from game.simulation.services.design_loader` in `game/ui/` directory
- [x] Only acceptable: `game/ui/services/design_loader_adapter.py` (the adapter itself)
- [x] No other UI files should import SimulationDesignLoader directly
- [x] Run full test suite: `pytest tests/ -n 12` (8182 tests passing)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Zero direct SimulationDesignLoader imports in UI (except the adapter)
- [x] DesignLoaderAdapter is the single entry point for design loading in UI
- [x] Full test suite passes: `pytest tests/ -n 12` (8182 tests)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
