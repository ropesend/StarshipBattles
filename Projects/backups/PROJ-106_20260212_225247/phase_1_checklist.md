# Phase 1: Simple Encapsulation Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-106 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix low-risk, isolated violations that require no new abstractions -- just proper encapsulation and removing direct private attribute access.

---

## Tasks

### Task 1.1: Replace pygame.math.Vector2 in SimulationDesignLoader [Simple]
**File:** `game/simulation/services/design_loader.py`
**Tests:** `pytest tests/unit/simulation/test_simulation_design_loader.py -v`
**Finding:** ADR-SIM-001 -- Simulation layer must not import pygame

- [x] Remove `import pygame` on line 69 (inside `load_ship_from_design_data()`)
- [x] Replace `pygame.math.Vector2(center_x, center_y)` with `Vector2(center_x, center_y)` on line 73
- [x] Add `from game.core.math import Vector2` to top-level imports (if not already present)
- [x] Grep entire file for any remaining `pygame` references
- [x] Run tests: `pytest tests/unit/simulation/test_simulation_design_loader.py -v`

---

### Task 1.2: Add Ship.registries Public Property [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/simulation/ -v -k ship`
**Finding:** ADR-SIM-005 -- `battle_engine.py:485` accesses private `source_ship._registries`

- [x] Add `@property` method `registries` to Ship class (after line 61) returning `self._registries`
- [x] Update `game/simulation/systems/battle_engine.py:485` to use `source_ship.registries` instead of `source_ship._registries`
- [x] Grep for external `._registries` access outside ship.py and its delegate files (ship_stats.py, ship_loader.py, etc.)
- [x] Update any other external callers found (battle_controller.py:830,837)
- [x] Add a simple test verifying `ship.registries` returns the injected GameRegistries
- [x] Run tests: `pytest tests/unit/simulation/ tests/unit/combat/ -v`

---

### Task 1.3: Add Component.mark_hp_cache_dirty() Public Method [Simple]
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/components/ -v`
**Finding:** ADR-SIM-006 -- External code directly modifies `_hp_ratio_dirty`

- [x] Add public method `mark_hp_cache_dirty(self)` to Component class that sets `self._hp_ratio_dirty = True`
- [x] Update `game/simulation/battle_state.py:301`: replace `new_comp._hp_ratio_dirty = True` with `new_comp.mark_hp_cache_dirty()`
- [x] Update `game/simulation/entities/ship_stats.py:428`: replace `comp._hp_ratio_dirty = True` with `comp.mark_hp_cache_dirty()`
- [x] Update `game/simulation/entities/ship_combat_engine.py:225`: replace `target._hp_ratio_dirty = True` with `target.mark_hp_cache_dirty()`
- [x] NOTE: `component_stats_calculator.py` and `component_health_manager.py` are INSIDE the component package -- they can access `_hp_ratio_dirty` directly
- [x] Run tests: `pytest tests/unit/components/ tests/unit/simulation/ -v`

---

### Task 1.4: Fix Private _resources Access in BattleUIService [Simple]
**File:** `game/ui/services/battle_ui_service.py`
**Tests:** `pytest tests/unit/ui/interfaces/test_battle_ui.py -v`
**Finding:** ADR-UI2-001 -- Accessing private `_resources` via `getattr(ship_resources, '_resources', {})`

- [x] In `_convert_ship()` (lines 131-141), replace the private `_resources` access block
- [x] Old pattern: `hasattr(ship_resources, '_resources')` + `getattr(ship_resources, '_resources', {})`
- [x] New pattern: `ship_resources.get_all_resources()` which returns `List[ResourceState]`
- [x] Updated test fixture in conftest.py to use mock `get_all_resources()` instead of private `_resources`
- [x] Run tests: `pytest tests/unit/ui/interfaces/test_battle_ui.py -v`

---

### Task 1.5: Verify ShipThemeManager.reset() Thread Safety [Simple]
**File:** `game/ui/assets/ship_theme_manager.py`
**Tests:** `pytest tests/unit/ui/ -v -k theme`
**Finding:** ADR-UI2-003 -- reset() should call clear() before nullifying instance

- [x] Read `reset()` at line 82-92. Current code already calls `cls._instance.clear()` on line 91 before `cls._instance = None`
- [x] Verify: this was already fixed. RESOLVED.
- [x] No code changes needed
- [x] Run tests to confirm: `pytest tests/unit/ui/ -v -k theme`

---

### Task 1.6: Move Lazy Imports to Top-Level in DesignLoaderAdapter [Simple]
**File:** `game/ui/services/design_loader_adapter.py`
**Tests:** `pytest tests/unit/ui/services/test_design_loader_adapter.py -v`
**Finding:** ADR-UI2-005 -- Lazy imports inside `__init__` obscure dependencies

- [x] Move `from game.simulation.services.design_loader import SimulationDesignLoader` from line 41 to top-level imports
- [x] Move `from game.core.registry import get_default_registries` from line 43 to top-level imports
- [x] Keep conditional logic in `__init__` (only create if not injected) but use the top-level names
- [x] Remove the TYPE_CHECKING import of SimulationDesignLoader (line 14-15) since it's now a real import
- [x] Run tests: `pytest tests/unit/ui/services/test_design_loader_adapter.py -v`

---

### Task 1.7: Verify ADR-UI1-009 (session._facade) [Simple]
**Finding:** ADR-UI1-009 -- `self.session._facade` private access in strategy_screen.py

- [x] Grep for `session._facade` across entire `game/` directory
- [x] Expected result: NO matches. `strategy_screen.py` creates its OWN `self._facade` (line 76), NOT `self.session._facade`
- [x] ADR-UI1-009 is a false positive -- strategy_screen creates its own _facade, not accessing session's private _facade
- [x] No code changes needed

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Full test suite passes: `pytest tests/ -n 12` (8164 tests)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
