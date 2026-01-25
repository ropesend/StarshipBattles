# Phase 2: Component Constants Re-export Removal

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-16 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove ComponentStatus, LayerType, Modifier, ApplicationModifier re-exports from component.py
**Risk:** Low
**Files Affected:** ~65

---

## Tasks

### Task 2.1: Update UI Layer Imports [Medium]

**Canonical Location:** `game/simulation/components/component_constants.py`
**Re-export Location:** `game/simulation/components/component.py` (lines 68-74)
**Tests:** `pytest tests/unit/ui/ -v`

#### Files to Update:

- [ ] `ui/builder/detail_panel.py` - imports LayerType
- [ ] `game/ui/panels/ship_detail_panel.py` - imports LayerType
- [ ] `game/ui/panels/ship_stats_renderer.py` - imports ComponentStatus

**Change pattern:**
```python
# From:
from game.simulation.components.component import ComponentStatus, LayerType
# To:
from game.simulation.components.component_constants import ComponentStatus, LayerType
```

**Notes:**

---

### Task 2.2: Update Simulation Layer Imports [Medium]

**Tests:** `pytest tests/unit/simulation/ tests/unit/entities/ -v`

#### Files to Update:

- [ ] `game/ai/target_evaluator.py` - imports LayerType
- [ ] `game/simulation/ship_validator.py` - imports Component, LayerType
- [ ] `game/simulation/services/vehicle_design_service.py` - imports Component, LayerType
- [ ] `game/simulation/battle_state.py` - imports LayerType
- [ ] `game/simulation/designs.py` - imports LayerType
- [ ] `game/simulation/entities/ship_stats.py` - imports ComponentStatus, LayerType
- [ ] `game/simulation/entities/ship_serialization.py` - imports LayerType
- [ ] `game/simulation/entities/ship_component_manager.py` - imports Component, LayerType
- [ ] `game/simulation/entities/ship_combat_engine.py` - imports LayerType, ComponentStatus
- [ ] `game/simulation/validation/base.py` - imports Component, LayerType

**Note:** Keep imports of `Component`, `create_component`, `load_components` from `component.py` - only move the constant imports.

**Notes:**

---

### Task 2.3: Update Test File Imports [Complex]

**Tests:** `pytest tests/ --testmon`

#### Critical Test Fixtures (Update First):

- [ ] `tests/fixtures/components.py` - imports create_component, Component, LayerType
- [ ] `tests/conftest.py` - check for ComponentStatus/LayerType imports

#### Test Files to Update (~49 files):

Combat Tests:
- [ ] `tests/unit/combat/test_multitarget.py`
- [ ] `tests/unit/combat/test_fighter_launch.py`
- [ ] `tests/unit/combat/test_damage_weighted.py`
- [ ] `tests/unit/combat/test_combat_endurance.py`

Builder Tests:
- [ ] `tests/unit/builder/test_requirement_abilities.py`
- [ ] `tests/unit/builder/test_bulk_add.py`
- [ ] `tests/unit/builder/test_builder_validation.py`
- [ ] `tests/unit/builder/test_builder_structure_features.py`

Entity Tests:
- [ ] `tests/unit/entities/test_ship_stats.py`
- [ ] `tests/unit/entities/test_ship_helpers.py`
- [ ] `tests/unit/entities/test_hull_layer.py`
- [ ] `tests/unit/entities/test_stacking_integration.py`
- [ ] `tests/unit/entities/test_stacking_rules.py`
- [ ] `tests/unit/entities/test_ship_caching.py`
- [ ] `tests/unit/entities/test_mandatory_updates.py`
- [ ] `tests/unit/entities/test_mandatory_modifiers.py`
- [ ] `tests/unit/entities/test_modifier_row.py`
- [ ] `tests/unit/entities/test_ship_resources.py`

System Tests:
- [ ] `tests/unit/systems/test_layer_restrictions_refactor.py`
- [ ] `tests/unit/systems/test_dynamic_layers.py`

Simulation Tests:
- [ ] `tests/unit/simulation/test_ship_component_manager.py`
- [ ] `tests/unit/simulation/test_ship_combat_engine.py`

AI/Service Tests:
- [ ] `tests/unit/ai/test_target_evaluator.py`
- [ ] `tests/unit/ai/test_movement_and_ai.py`
- [ ] `tests/unit/services/test_vehicle_design_service.py`
- [ ] `tests/unit/services/test_ship_builder_service.py`

Regression/Repro Tests:
- [ ] `tests/unit/regressions/test_bug_regressions_2026_01.py`
- [ ] `tests/repro_issues/test_bug_01_crew_delay.py`
- [ ] `tests/repro_issues/test_bug_05_logistics.py`
- [ ] `tests/repro_issues/test_bug_07_crash.py`
- [ ] `tests/repro_issues/test_bug_09_endurance.py`
- [ ] `tests/repro_issues/test_bug_10_repro.py`
- [ ] `tests/repro_issues/test_bug_11_hull_update.py`
- [ ] `tests/repro_issues/test_bug_13_clear_removes_hull.py`

Performance/Fixtures:
- [ ] `tests/unit/performance/generate_test_data.py`
- [ ] `tests/unit/performance/repro_shield.py`
- [ ] `tests/unit/performance/repro_energy_stats.py`
- [ ] `tests/unit/fixtures/test_component_fixtures.py`
- [ ] `tests/unit/fixtures/test_ship_fixtures.py`
- [ ] `tests/fixtures/ships.py`

Test Framework:
- [ ] `test_framework/scenario.py`
- [ ] `test_framework/scenarios/gun_accuracy_test.py`

**Notes:**

---

### Task 2.4: Remove Re-exports from component.py [Simple]

**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Remove the re-export block (lines 68-74):
  ```python
  # Re-export from component_constants for backward compatibility
  from .component_constants import (
      ComponentStatus,
      LayerType,
      Modifier,
      ApplicationModifier,
  )
  ```

**Notes:**

---

### Task 2.5: Verify No Remaining Usages [Simple]

- [ ] Run verification commands:
  ```bash
  grep -r "from game.simulation.components.component import ComponentStatus" --include="*.py"
  grep -r "from game.simulation.components.component import LayerType" --include="*.py"
  grep -r "from game.simulation.components.component import Modifier" --include="*.py"
  grep -r "from game.simulation.components.component import ApplicationModifier" --include="*.py"
  ```
  Expected: No results (only imports of Component, create_component, load_components should remain)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` passes
- [ ] No circular import errors: `python -c "import game"`
- [ ] Application launches: `python -m game`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
