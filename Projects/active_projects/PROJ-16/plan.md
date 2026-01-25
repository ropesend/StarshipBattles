# PROJ-16: Legacy Cleanup Phase 3 - Consolidate Re-exports

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-16` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-16 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Create Package Facades | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Update Test Infrastructure | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Update Production Code | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Remove Old Re-exports | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Remove Wrapper Classes | In Progress | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-01-25
**Active Phase:** Phase 5 (Wrapper Classes)
**Last Action:** Phases 1-4 complete, re-exports consolidated
**Next Action:** Remove ModifierLogic wrapper class, simplify ProfilerProxy
**Blockers:** None

## Overview

Consolidate re-exports by creating proper package-level `__init__.py` facades, updating all callers to import from package level, then removing backward compatibility re-exports from individual modules. Also remove thin wrapper classes (ModifierLogic, ProfilerProxy) that only delegate.

## Goals
- Update all callers to import from canonical/package locations
- Remove backward compatibility re-exports from modules
- Consolidate shared constants to `game/core/constants.py`
- Remove thin adapter/wrapper classes that only delegate
- Establish proper Python package structure with `__init__.py` facades

## Scope
**In:**
- Component re-exports (LayerType, ComponentStatus, Modifier, ApplicationModifier)
- Ship loader re-exports (get_or_create_validator, load_vehicle_classes, initialize_ship_data)
- AI controller re-exports (StrategyManager, get_strategy_names, reset_strategy_manager)
- PLANET_RESOURCES constant re-export
- ModifierLogic wrapper removal
- ProfilerProxy simplification

**Out:**
- ShipControllableAdapter (essential design pattern, keep as-is)
- UI component changes beyond import updates
- Test logic changes (only import updates)

## Key Files
| Component | File Path |
|-----------|-----------|
| Component re-exports | `game/simulation/components/component.py:68-74` |
| Ship loader re-exports | `game/simulation/entities/ship.py:21-26` |
| AI controller re-exports | `game/ai/controller.py:52-60` |
| PLANET_RESOURCES re-export | `game/strategy/data/planet.py:8` |
| ModifierLogic wrapper | `ui/builder/modifier_logic.py` |
| ProfilerProxy | `game/core/profiling.py:133-144` |
| Root conftest | `conftest.py:55,68` |
| Test fixtures | `tests/fixtures/components.py`, `tests/fixtures/ships.py`, `tests/fixtures/ai.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [PHASE_3_CONSOLIDATE_REEXPORTS.md](../../legacy_cleanup/PHASE_3_CONSOLIDATE_REEXPORTS.md) - Original phase spec

---

## Phases

### Phase 1: Create Package Facades [Medium]
**Objective:** Create proper `__init__.py` files that expose the package API
**Status:** Not Started

This phase creates the target import structure. After this phase, callers can use package-level imports, but old imports still work.

#### Task 1.1: Create components package __init__.py [Simple]
**File:** `game/simulation/components/__init__.py`
**Tests:** `pytest --collect-only -q`
- [ ] Create/update `__init__.py` with exports:
  ```python
  """Component System - building blocks of ships."""
  from .component_constants import (
      ComponentStatus,
      LayerType,
      Modifier,
      ApplicationModifier,
  )
  from .component import (
      Component,
      create_component,
      load_components,
      load_modifiers,
      get_all_components,
      reset_component_caches,
  )
  __all__ = [
      'ComponentStatus', 'LayerType', 'Modifier', 'ApplicationModifier',
      'Component', 'create_component', 'load_components', 'load_modifiers',
      'get_all_components', 'reset_component_caches',
  ]
  ```
- [ ] Verify: `python -c "from game.simulation.components import Component, LayerType; print('OK')"`

#### Task 1.2: Create entities package __init__.py [Simple]
**File:** `game/simulation/entities/__init__.py` (NEW FILE)
**Tests:** `pytest --collect-only -q`
- [ ] Create new `__init__.py`:
  ```python
  """Entities - Ship and other game entities."""
  from .ship import Ship
  __all__ = ['Ship']
  ```
- [ ] Verify: `python -c "from game.simulation.entities import Ship; print('OK')"`

#### Task 1.3: Create AI package __init__.py [Simple]
**File:** `game/ai/__init__.py`
**Tests:** `pytest --collect-only -q`
- [ ] Update empty `__init__.py` with exports:
  ```python
  """AI System - decision-making for autonomous entities."""
  from .controller import AIController
  from .strategy_manager import (
      StrategyManager,
      get_strategy_names,
      reset_strategy_manager,
  )
  from .target_evaluator import TargetEvaluator
  __all__ = [
      'AIController', 'StrategyManager', 'TargetEvaluator',
      'get_strategy_names', 'reset_strategy_manager',
  ]
  ```
- [ ] Verify: `python -c "from game.ai import AIController, StrategyManager; print('OK')"`

#### Task 1.4: Verify no circular imports [Simple]
**Tests:** Python import check
- [ ] Run: `python -c "import game.simulation.components; import game.simulation.entities; import game.ai; print('All packages import OK')"`
- [ ] Run: `pytest --collect-only -q` (verify test collection works)

---

### Phase 2: Update Test Infrastructure [High]
**Objective:** Update conftest files and fixtures BEFORE individual test files
**Status:** Not Started

CRITICAL: These files affect all tests. Update in exact order specified.

#### Task 2.1: Update root conftest.py [Medium]
**File:** `conftest.py`
**Tests:** `pytest --collect-only -q`
- [ ] Line 55: Change `from game.ai.controller import StrategyManager` to `from game.ai import StrategyManager`
- [ ] Line 68: Same change if duplicate import exists
- [ ] Any other imports from re-export locations
- [ ] Verify: `pytest --collect-only -q` (tests must collect without errors)

#### Task 2.2: Update tests/conftest.py [Medium]
**File:** `tests/conftest.py`
**Tests:** `pytest --collect-only -q`
- [ ] Update imports from `component.py` to use package: `from game.simulation.components import ...`
- [ ] Update imports from `ship.py` to use `ship_loader` for loader functions
- [ ] Verify: `pytest --collect-only -q`

#### Task 2.3: Update simulation_tests/conftest.py [Simple]
**File:** `simulation_tests/conftest.py`
**Tests:** `pytest simulation_tests/ --collect-only -q`
- [ ] Update any re-export imports to use package-level or canonical sources
- [ ] Verify: `pytest simulation_tests/ --collect-only -q`

#### Task 2.4: Update test fixtures [Medium]
**Files:** `tests/fixtures/components.py`, `tests/fixtures/ships.py`, `tests/fixtures/ai.py`, `tests/fixtures/common.py`
**Tests:** `pytest tests/unit/fixtures/ -v`
- [ ] `tests/fixtures/components.py`: Update `from game.simulation.components.component import` to `from game.simulation.components import`
- [ ] `tests/fixtures/ships.py`: Same updates for component imports
- [ ] `tests/fixtures/ai.py`: Update `from game.ai.controller import StrategyManager` to `from game.ai import StrategyManager`
- [ ] `tests/fixtures/common.py`: Update component/ship imports
- [ ] Verify: `pytest tests/unit/fixtures/ -v`

#### Task 2.5: Update tests/infrastructure [Simple]
**File:** `tests/infrastructure/session_cache.py`
**Tests:** `pytest --collect-only -q`
- [ ] Update any re-export imports
- [ ] Verify: `pytest --collect-only -q`

---

### Phase 3: Update Production Code [High]
**Objective:** Update all production code imports
**Status:** Not Started

#### Task 3.1: Update component imports in simulation layer [Medium]
**Files:** Multiple files in `game/simulation/`
**Tests:** `pytest tests/unit/entities/ tests/unit/simulation/ -x`
- [ ] `game/simulation/entities/ship.py` - update LayerType, ComponentStatus imports
- [ ] `game/simulation/entities/ship_component_manager.py` - update Component, LayerType imports
- [ ] `game/simulation/entities/ship_combat_engine.py` - update LayerType, ComponentStatus imports
- [ ] `game/simulation/entities/ship_serialization.py` - update LayerType, create_component imports
- [ ] `game/simulation/entities/ship_stats.py` - update ComponentStatus, LayerType imports
- [ ] `game/simulation/services/vehicle_design_service.py` - update Component, LayerType imports
- [ ] `game/simulation/ship_validator.py` - update Component, LayerType imports
- [ ] `game/simulation/validation/base.py` - update lazy imports
- [ ] `game/simulation/designs.py` - update create_component, LayerType imports
- [ ] `game/simulation/battle_state.py` - update LayerType imports
- [ ] Verify: `pytest tests/unit/entities/ tests/unit/simulation/ -x`

#### Task 3.2: Update AI layer imports [Simple]
**Files:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/ -x`
- [ ] Update LayerType import to use `from game.simulation.components import LayerType`
- [ ] Verify: `pytest tests/unit/ai/ -x`

#### Task 3.3: Update UI layer imports [Medium]
**Files:** Multiple files in `game/ui/`
**Tests:** `pytest tests/unit/ui/ -x`
- [ ] `game/ui/panels/ship_detail_panel.py` - update LayerType import
- [ ] `game/ui/panels/ship_stats_renderer.py` - update ComponentStatus, StrategyManager imports
- [ ] `game/ui/panels/component_modifier_grid_panel.py` - update lazy Component import
- [ ] `game/ui/panels/modifier_impact_grid.py` - update lazy Component import
- [ ] `game/ui/screens/builder_screen.py` - update get_all_components import
- [ ] `game/ui/screens/workshop_screen.py` - update Component, LayerType, create_component imports
- [ ] `game/ui/screens/workshop_viewmodel.py` - update Component, get_all_components imports
- [ ] `game/ui/screens/workshop_data_loader.py` - update lazy imports for components and StrategyManager
- [ ] `game/ui/screens/workshop_event_router.py` - update StrategyManager import
- [ ] `game/ui/screens/battle_scene.py` - update AIController import
- [ ] `game/ui/screens/setup_screen.py` - update StrategyManager import
- [ ] `game/ui/screens/setup_renderer.py` - update StrategyManager import
- [ ] Verify: `pytest tests/unit/ui/ -x`

#### Task 3.4: Update app.py imports [Simple]
**File:** `game/app.py`
**Tests:** `pytest tests/unit/ -x`
- [ ] Update `load_components`, `load_modifiers` imports
- [ ] Verify: `pytest tests/unit/ -x`

#### Task 3.5: Update PLANET_RESOURCES imports [Simple]
**Files:** 7 files importing from `planet.py`
**Tests:** `pytest tests/unit/strategy/ -x`
- [ ] `game/strategy/data/planet_gen.py` - change to `from game.core.constants import PLANET_RESOURCES`
- [ ] `game/ui/screens/planet_list_window.py` - same change
- [ ] `tests/unit/components/test_resource_costs.py` - same change
- [ ] `tests/unit/validation/test_component_definitions.py` - same change
- [ ] `ui/builder/detail_panel.py` - same change
- [ ] `ui/builder/stats_config.py` - same change
- [ ] `ui/builder/structure_list_items.py` - same change
- [ ] Verify: `pytest tests/unit/strategy/ -x`

#### Task 3.6: Update Tools directory [Simple]
**Files:** `Tools/verify_resources.py`, `Tools/quick_test_modifiers.py`, etc.
**Tests:** Run tools manually
- [ ] Update imports in any Tools that import from re-export locations
- [ ] Verify: `python Tools/verify_resources.py` (if applicable)

---

### Phase 4: Remove Old Re-exports [Medium]
**Objective:** Remove the backward compatibility re-export blocks
**Status:** Not Started

#### Task 4.1: Remove dead TargetEvaluator re-export [Simple]
**File:** `game/ai/controller.py:60`
**Tests:** `pytest tests/unit/ai/ -x`
- [ ] Remove line: `from game.ai.target_evaluator import TargetEvaluator`
- [ ] This is dead code (0 imports found)
- [ ] Verify: `pytest tests/unit/ai/ -x`

#### Task 4.2: Remove component.py re-exports [Medium]
**File:** `game/simulation/components/component.py:68-74`
**Tests:** `pytest tests/unit/ -x`
- [ ] Remove the re-export block:
  ```python
  # Re-export from component_constants for backward compatibility
  from .component_constants import (
      ComponentStatus,
      LayerType,
      Modifier,
      ApplicationModifier,
  )
  ```
- [ ] Verify: `grep -r "from game.simulation.components.component import ComponentStatus" --include="*.py"` returns nothing
- [ ] Verify: `grep -r "from game.simulation.components.component import LayerType" --include="*.py"` returns nothing
- [ ] Verify: `pytest tests/unit/ -x`

#### Task 4.3: Remove ship.py re-exports [Medium]
**File:** `game/simulation/entities/ship.py:21-26`
**Tests:** `pytest tests/unit/ -x`
- [ ] Remove the re-export block:
  ```python
  # Re-export from ship_loader for backward compatibility
  from .ship_loader import (
      get_or_create_validator,
      load_vehicle_classes,
      initialize_ship_data,
  )
  ```
- [ ] Verify: `grep -r "from game.simulation.entities.ship import get_or_create_validator" --include="*.py"` returns nothing
- [ ] Verify: `pytest tests/unit/ -x`

#### Task 4.4: Remove controller.py re-exports [Medium]
**File:** `game/ai/controller.py:52-57`
**Tests:** `pytest tests/unit/ -x`
- [ ] Remove the re-export block:
  ```python
  # Re-export from strategy_manager for backward compatibility
  from game.ai.strategy_manager import (
      StrategyManager,
      get_strategy_names,
      reset_strategy_manager,
  )
  ```
- [ ] Verify: `grep -r "from game.ai.controller import StrategyManager" --include="*.py"` returns nothing
- [ ] Verify: `pytest tests/unit/ -x`

#### Task 4.5: Remove planet.py re-export [Simple]
**File:** `game/strategy/data/planet.py:8`
**Tests:** `pytest tests/unit/strategy/ -x`
- [ ] Remove line: `from game.core.constants import PLANET_RESOURCES`
- [ ] Verify: `grep -r "from game.strategy.data.planet import PLANET_RESOURCES" --include="*.py"` returns nothing
- [ ] Verify: `pytest tests/unit/strategy/ -x`

---

### Phase 5: Remove Wrapper Classes [Medium]
**Objective:** Remove ModifierLogic wrapper and simplify ProfilerProxy
**Status:** Not Started

#### Task 5.1: Move calculate_snap_value to ModifierControlRow [Medium]
**Files:** `ui/builder/modifier_logic.py`, `ui/builder/modifier_row.py`
**Tests:** `pytest tests/unit/ui/ tests/unit/entities/test_modifier*.py -x`
- [ ] Read `ui/builder/modifier_logic.py` to get `calculate_snap_value()` implementation
- [ ] Add `calculate_snap_value()` as static method in `ModifierControlRow` class in `modifier_row.py`
- [ ] Update calls in `modifier_row.py:299,301` to use `ModifierControlRow.calculate_snap_value(...)`
- [ ] Verify: `pytest tests/unit/ui/ tests/unit/entities/test_modifier*.py -x`

#### Task 5.2: Update ModifierLogic callers to use ModifierService [Medium]
**Files:** `ui/builder/modifier_row.py`, `ui/builder/detail_panel.py`, `game/ui/panels/builder_widgets.py`
**Tests:** `pytest tests/unit/ui/ tests/unit/builder/ -x`
- [ ] In each file, change import from `from ui.builder.modifier_logic import ModifierLogic` to `from game.simulation.services import ModifierService`
- [ ] Replace all `ModifierLogic.method()` calls with `ModifierService.method()`
- [ ] Methods are 1:1 compatible: `is_modifier_allowed`, `get_mandatory_modifiers`, `is_modifier_mandatory`, `get_initial_value`, `ensure_mandatory_modifiers`, `get_local_min_max`
- [ ] Verify: `pytest tests/unit/ui/ tests/unit/builder/ -x`

#### Task 5.3: Update test files using ModifierLogic [Simple]
**Files:** Test files that import ModifierLogic
**Tests:** `pytest tests/unit/entities/test_modifier*.py tests/unit/ui/test_detail*.py -x`
- [ ] `tests/unit/ui/test_detail_panel_rendering.py` - update patch target
- [ ] `tests/unit/entities/test_modifier_defaults_robustness.py` - update import
- [ ] `tests/unit/entities/test_mandatory_updates.py` - update import
- [ ] `Tools/quick_test_modifiers.py` - update import
- [ ] Verify: `pytest tests/unit/entities/test_modifier*.py tests/unit/ui/test_detail*.py -x`

#### Task 5.4: Delete ModifierLogic and update __init__.py [Simple]
**Files:** `ui/builder/modifier_logic.py`, `ui/builder/__init__.py`
**Tests:** `pytest tests/unit/ -x`
- [ ] Delete file: `ui/builder/modifier_logic.py`
- [ ] Update `ui/builder/__init__.py` - remove `from .modifier_logic import ModifierLogic` line
- [ ] Verify: `pytest tests/unit/ -x`

#### Task 5.5: Simplify ProfilerProxy [Simple]
**File:** `game/core/profiling.py:133-144`
**Tests:** `pytest tests/unit/core/test_profiling.py tests/unit/performance/test_profiler*.py -x`
- [ ] Replace `_ProfilerProxy` class and `PROFILER = _ProfilerProxy()` with:
  ```python
  # Simple module-level instance (Profiler.instance() is thread-safe)
  PROFILER = Profiler.instance()
  ```
- [ ] Delete `_ProfilerProxy` class definition (lines 133-143)
- [ ] Verify: `pytest tests/unit/core/test_profiling.py tests/unit/performance/test_profiler*.py -x`

---

## Verification Checklist

### After Each Phase
- [ ] `pytest --collect-only -q` - Tests collect without import errors
- [ ] `pytest tests/unit/ -x --tb=short` - Unit tests pass
- [ ] `python -c "import game.simulation.entities.ship; import game.ai.controller; print('OK')"` - No circular imports

### Final Verification
- [ ] All phase checklists complete
- [ ] `pytest tests/ -v` - Full test suite passes
- [ ] `pytest simulation_tests/ -v` - Simulation tests pass
- [ ] No remaining old import patterns:
  - [ ] `grep -r "from game.simulation.components.component import ComponentStatus" --include="*.py"` - empty
  - [ ] `grep -r "from game.simulation.components.component import LayerType" --include="*.py"` - empty
  - [ ] `grep -r "from game.ai.controller import StrategyManager" --include="*.py"` - empty
  - [ ] `grep -r "from game.simulation.entities.ship import get_or_create_validator" --include="*.py"` - empty
- [ ] `ui/builder/modifier_logic.py` deleted
- [ ] `_ProfilerProxy` class removed from profiling.py
- [ ] Application launches and runs correctly
- [ ] User verified

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks complete
- [ ] All Phase 2 tasks complete
- [ ] All Phase 3 tasks complete
- [ ] All Phase 4 tasks complete
- [ ] All Phase 5 tasks complete
- [ ] All tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified
