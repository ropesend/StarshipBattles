# Phase 1: Create Package Facades

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-16 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create proper `__init__.py` files that expose the package API

This phase creates the target import structure. After this phase, callers can use package-level imports, but old imports still work.

---

## Tasks

### Task 1.1: Create components package __init__.py [Simple]
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

**Notes:**

---

### Task 1.2: Create entities package __init__.py [Simple]
**File:** `game/simulation/entities/__init__.py` (NEW FILE)
**Tests:** `pytest --collect-only -q`

- [ ] Create new `__init__.py`:
  ```python
  """Entities - Ship and other game entities."""
  from .ship import Ship
  __all__ = ['Ship']
  ```
- [ ] Verify: `python -c "from game.simulation.entities import Ship; print('OK')"`

**Notes:**

---

### Task 1.3: Create AI package __init__.py [Simple]
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

**Notes:**

---

### Task 1.4: Verify no circular imports [Simple]
**Tests:** Python import check

- [ ] Run: `python -c "import game.simulation.components; import game.simulation.entities; import game.ai; print('All packages import OK')"`
- [ ] Run: `pytest --collect-only -q` (verify test collection works)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest --collect-only -q` passes
- [ ] No circular imports
- [ ] Package-level imports work for all three packages
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
