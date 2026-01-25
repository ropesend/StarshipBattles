# Phase 3: Update Production Code

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-16 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update all production code imports

---

## Tasks

### Task 3.1: Update component imports in simulation layer [Medium]
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

**Notes:**

---

### Task 3.2: Update AI layer imports [Simple]
**Files:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/ -x`

- [ ] Update LayerType import to use `from game.simulation.components import LayerType`
- [ ] Verify: `pytest tests/unit/ai/ -x`

**Notes:**

---

### Task 3.3: Update UI layer imports [Medium]
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

**Notes:**

---

### Task 3.4: Update app.py imports [Simple]
**File:** `game/app.py`
**Tests:** `pytest tests/unit/ -x`

- [ ] Update `load_components`, `load_modifiers` imports
- [ ] Verify: `pytest tests/unit/ -x`

**Notes:**

---

### Task 3.5: Update PLANET_RESOURCES imports [Simple]
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

**Notes:**

---

### Task 3.6: Update Tools directory [Simple]
**Files:** `Tools/verify_resources.py`, `Tools/quick_test_modifiers.py`, etc.
**Tests:** Run tools manually

- [ ] Update imports in any Tools that import from re-export locations
- [ ] Verify: `python Tools/verify_resources.py` (if applicable)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/entities/ -x` passes
- [ ] `pytest tests/unit/simulation/ -x` passes
- [ ] `pytest tests/unit/ai/ -x` passes
- [ ] `pytest tests/unit/ui/ -x` passes
- [ ] `pytest tests/unit/strategy/ -x` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
