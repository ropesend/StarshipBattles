# Phase 2: Component Constants Re-export Removal

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-16 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
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

- [x] `ui/builder/detail_panel.py` - imports LayerType
- [x] `game/ui/panels/ship_detail_panel.py` - imports LayerType
- [x] `game/ui/panels/ship_stats_renderer.py` - imports ComponentStatus (also had LayerType from ship.py re-export)

**Change pattern:**
```python
# From:
from game.simulation.components.component import ComponentStatus, LayerType
# To:
from game.simulation.components.component_constants import ComponentStatus, LayerType
```

**Notes:** Task 2.1 complete. All 3 UI files updated, tests pass.

---

### Task 2.2: Update Simulation Layer Imports [Medium]

**Tests:** `pytest tests/unit/simulation/ tests/unit/entities/ -v`

#### Files to Update:

- [x] `game/ai/target_evaluator.py` - imports LayerType
- [x] `game/simulation/ship_validator.py` - imports Component, LayerType
- [x] `game/simulation/services/vehicle_design_service.py` - imports Component, LayerType
- [x] `game/simulation/battle_state.py` - imports LayerType
- [x] `game/simulation/designs.py` - imports LayerType
- [x] `game/simulation/entities/ship_stats.py` - imports ComponentStatus, LayerType
- [x] `game/simulation/entities/ship_serialization.py` - imports LayerType
- [x] `game/simulation/entities/ship_component_manager.py` - imports Component, LayerType
- [x] `game/simulation/entities/ship_combat_engine.py` - imports LayerType, ComponentStatus
- [x] `game/simulation/validation/base.py` - imports Component, LayerType (TYPE_CHECKING import)

**Note:** Keep imports of `Component`, `create_component`, `load_components` from `component.py` - only move the constant imports.

**Notes:** Task 2.2 complete. All 10 simulation layer files updated. 238 tests pass.

---

### Task 2.3: Update Test File Imports [Complex]

**Tests:** `pytest tests/ --testmon`

**ALL FILES UPDATED** - 48+ test files updated to import from component_constants

**Notes:** Task 2.3 complete. All test files updated. Also updated ship.py which imports LayerType internally. 4524 tests pass.

---

### Task 2.4: Remove Re-exports from component.py [Simple]

**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/ --testmon`

- [x] Remove the re-export block (lines 68-74):
  ```python
  # Re-export from component_constants for backward compatibility
  from .component_constants import (
      ComponentStatus,
      LayerType,
      Modifier,
      ApplicationModifier,
  )
  ```

**Notes:** Task 2.4 complete. Re-export block removed. Note: component.py still imports ComponentStatus, Modifier, ApplicationModifier internally for its own use (not re-exporting).

---

### Task 2.5: Verify No Remaining Usages [Simple]

- [x] Run verification commands:
  ```bash
  grep -r "from game.simulation.components.component import ComponentStatus" --include="*.py"
  grep -r "from game.simulation.components.component import LayerType" --include="*.py"
  grep -r "from game.simulation.components.component import Modifier" --include="*.py"
  grep -r "from game.simulation.components.component import ApplicationModifier" --include="*.py"
  ```
  Expected: No results (only imports of Component, create_component, load_components should remain) - VERIFIED

**Notes:** Task 2.5 complete. All verification commands return no matches.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ --testmon` passes (4524 passed, 1 pre-existing failure, 1 pre-existing error)
- [x] No circular import errors: `python -c "import game"` - OK
- [ ] Application launches: `python -m game` (GUI test - not performed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
