# Phase 4: Remove Old Re-exports

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-16 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove the backward compatibility re-export blocks

---

## Tasks

### Task 4.1: Remove dead TargetEvaluator re-export [Simple]
**File:** `game/ai/controller.py:60`
**Tests:** `pytest tests/unit/ai/ -x`

- [ ] Remove line: `from game.ai.target_evaluator import TargetEvaluator`
- [ ] This is dead code (0 imports found)
- [ ] Verify: `pytest tests/unit/ai/ -x`

**Notes:**

---

### Task 4.2: Remove component.py re-exports [Medium]
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

**Notes:**

---

### Task 4.3: Remove ship.py re-exports [Medium]
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

**Notes:**

---

### Task 4.4: Remove controller.py re-exports [Medium]
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

**Notes:**

---

### Task 4.5: Remove planet.py re-export [Simple]
**File:** `game/strategy/data/planet.py:8`
**Tests:** `pytest tests/unit/strategy/ -x`

- [ ] Remove line: `from game.core.constants import PLANET_RESOURCES`
- [ ] Verify: `grep -r "from game.strategy.data.planet import PLANET_RESOURCES" --include="*.py"` returns nothing
- [ ] Verify: `pytest tests/unit/strategy/ -x`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All grep verification commands return empty
- [ ] `pytest tests/unit/ -x` passes
- [ ] `python -c "import game.simulation.entities.ship; import game.ai.controller; print('OK')"` passes (no circular imports)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
