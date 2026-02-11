# Phase 1: Simple Encapsulation Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-106 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix low-risk, isolated violations that require no new abstractions -- just proper encapsulation and removing direct private attribute access.

---

## Tasks

### Task 1.1: Replace pygame.math.Vector2 in SimulationDesignLoader [Simple]
**File:** `game/simulation/services/design_loader.py`
**Tests:** `pytest tests/unit/simulation/test_simulation_design_loader.py -v`
**Finding:** ADR-SIM-001 -- Simulation layer must not import pygame

- [ ] Remove `import pygame` on line 69 (inside `load_ship_from_design_data()`)
- [ ] Replace `pygame.math.Vector2(center_x, center_y)` with `Vector2(center_x, center_y)` on line 73
- [ ] Add `from game.core.math import Vector2` to top-level imports (if not already present)
- [ ] Grep entire file for any remaining `pygame` references
- [ ] Run tests: `pytest tests/unit/simulation/test_simulation_design_loader.py -v`

---

### Task 1.2: Add Ship.registries Public Property [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/simulation/ -v -k ship`
**Finding:** ADR-SIM-005 -- `battle_engine.py:485` accesses private `source_ship._registries`

- [ ] Add `@property` method `registries` to Ship class (after line 61) returning `self._registries`
- [ ] Update `game/simulation/systems/battle_engine.py:485` to use `source_ship.registries` instead of `source_ship._registries`
- [ ] Grep for external `._registries` access outside ship.py and its delegate files (ship_stats.py, ship_loader.py, etc.)
- [ ] Update any other external callers found
- [ ] Add a simple test verifying `ship.registries` returns the injected GameRegistries
- [ ] Run tests: `pytest tests/unit/simulation/ tests/unit/combat/ -v`

---

### Task 1.3: Add Component.mark_hp_cache_dirty() Public Method [Simple]
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/components/ -v`
**Finding:** ADR-SIM-006 -- External code directly modifies `_hp_ratio_dirty`

- [ ] Add public method `mark_hp_cache_dirty(self)` to Component class (near line 113) that sets `self._hp_ratio_dirty = True`
- [ ] Update `game/simulation/battle_state.py:301`: replace `new_comp._hp_ratio_dirty = True` with `new_comp.mark_hp_cache_dirty()`
- [ ] Update `game/simulation/entities/ship_stats.py:428`: replace `comp._hp_ratio_dirty = True` with `comp.mark_hp_cache_dirty()`
- [ ] Update `game/simulation/entities/ship_combat_engine.py:225`: replace `target._hp_ratio_dirty = True` with `target.mark_hp_cache_dirty()`
- [ ] Update `game/simulation/components/component_stats_calculator.py:111`: replace `component._hp_ratio_dirty = True` with `component.mark_hp_cache_dirty()`
- [ ] Update `game/simulation/components/component_health_manager.py:56`: replace `component._hp_ratio_dirty = True` with `component.mark_hp_cache_dirty()`
- [ ] Update `game/simulation/components/component_health_manager.py:74`: replace `component._hp_ratio_dirty = True` with `component.mark_hp_cache_dirty()`
- [ ] NOTE: `component_health_manager.py:86` READS `_hp_ratio_dirty` internally -- this is within the component module, acceptable
- [ ] Run tests: `pytest tests/unit/components/ tests/unit/simulation/ -v`

---

### Task 1.4: Fix Private _resources Access in BattleUIService [Simple]
**File:** `game/ui/services/battle_ui_service.py`
**Tests:** `pytest tests/unit/ui/interfaces/test_battle_ui.py -v`
**Finding:** ADR-UI2-001 -- Accessing private `_resources` via `getattr(ship_resources, '_resources', {})`

- [ ] In `_convert_ship()` (lines 131-141), replace the private `_resources` access block
- [ ] Old pattern: `hasattr(ship_resources, '_resources')` + `getattr(ship_resources, '_resources', {})`
- [ ] New pattern: `ship_resources.get_all_resources()` which returns `List[ResourceState]` (already exists at `resource_manager.py:200`)
- [ ] Each ResourceState has `.name`, `.current_value`, `.max_value` -- matches existing DTO mapping
- [ ] Example replacement:
  ```python
  if ship_resources:
      for res in ship_resources.get_all_resources():
          resources.append(ResourceDTO(
              name=res.name,
              current_value=res.current_value,
              max_value=res.max_value
          ))
  ```
- [ ] Run tests: `pytest tests/unit/ui/interfaces/test_battle_ui.py -v`

---

### Task 1.5: Verify ShipThemeManager.reset() Thread Safety [Simple]
**File:** `game/ui/assets/ship_theme_manager.py`
**Tests:** `pytest tests/unit/ui/ -v -k theme`
**Finding:** ADR-UI2-003 -- reset() should call clear() before nullifying instance

- [ ] Read `reset()` at line 82-92. Current code already calls `cls._instance.clear()` on line 91 before `cls._instance = None`
- [ ] Verify: this was already fixed. Mark as RESOLVED in decisions.md
- [ ] No code changes needed
- [ ] Run tests to confirm: `pytest tests/unit/ui/ -v -k theme`

---

### Task 1.6: Move Lazy Imports to Top-Level in DesignLoaderAdapter [Simple]
**File:** `game/ui/services/design_loader_adapter.py`
**Tests:** `pytest tests/unit/ui/services/test_design_loader_adapter.py -v`
**Finding:** ADR-UI2-005 -- Lazy imports inside `__init__` obscure dependencies

- [ ] Move `from game.simulation.services.design_loader import SimulationDesignLoader` from line 41 to top-level imports
- [ ] Move `from game.core.registry import get_default_registries` from line 43 to top-level imports
- [ ] Keep conditional logic in `__init__` (only create if not injected) but use the top-level names
- [ ] Remove the TYPE_CHECKING import of SimulationDesignLoader (line 14-15) since it's now a real import
- [ ] Run tests: `pytest tests/unit/ui/services/test_design_loader_adapter.py -v`

---

### Task 1.7: Verify ADR-UI1-009 (session._facade) [Simple]
**Finding:** ADR-UI1-009 -- `self.session._facade` private access in strategy_screen.py

- [ ] Grep for `session._facade` across entire `game/` directory
- [ ] Expected result: NO matches. `strategy_screen.py` creates its OWN `self._facade` (line 76), NOT `self.session._facade`
- [ ] Record in decisions.md: "ADR-UI1-009 is a false positive -- strategy_screen creates its own _facade, not accessing session's private _facade"
- [ ] No code changes needed

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full test suite passes: `pytest tests/ -n 12` (8164+ tests)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
