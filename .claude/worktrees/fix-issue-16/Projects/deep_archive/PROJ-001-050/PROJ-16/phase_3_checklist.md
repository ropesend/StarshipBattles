# Phase 3: AI Re-export Removal

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-16 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove StrategyManager, get_strategy_names, reset_strategy_manager, TargetEvaluator re-exports from controller.py
**Risk:** Medium (test infrastructure affected)
**Files Affected:** ~40

---

## Tasks

### Task 3.1: Update Test Infrastructure [Medium]

**Canonical Locations:**
- `game/ai/strategy_manager.py` - StrategyManager, get_strategy_names, reset_strategy_manager, load_combat_strategies
- `game/ai/target_evaluator.py` - TargetEvaluator

**Re-export Location:** `game/ai/controller.py` (lines 52-61)
**Tests:** `pytest tests/unit/ai/ -v`

#### Critical Test Files (Update First):

- [ ] `conftest.py` (root) - imports reset_strategy_manager, StrategyManager
  - **Change:** `from game.ai.controller import StrategyManager, reset_strategy_manager`
  - **To:** `from game.ai.strategy_manager import StrategyManager, reset_strategy_manager`

- [ ] `tests/fixtures/ai.py` - imports StrategyManager
  - **Change:** `from game.ai.controller import StrategyManager`
  - **To:** `from game.ai.strategy_manager import StrategyManager`

- [ ] `tests/infrastructure/session_cache.py` - imports StrategyManager
  - **Change:** `from game.ai.controller import StrategyManager`
  - **To:** `from game.ai.strategy_manager import StrategyManager`

- [ ] `simulation_tests/conftest.py` - imports strategy functions
  - **Change:** `from game.ai.controller import ...`
  - **To:** `from game.ai.strategy_manager import ...`

**Notes:**

---

### Task 3.2: Update UI Layer Imports [Medium]

**Tests:** `pytest tests/unit/ui/ -v`

#### Files to Update:

- [ ] `game/ui/screens/setup_screen.py` - imports StrategyManager, get_strategy_names
  - **Change:** `from game.ai.controller import StrategyManager, get_strategy_names`
  - **To:** `from game.ai.strategy_manager import StrategyManager, get_strategy_names`

- [ ] `game/ui/screens/setup_renderer.py` - imports StrategyManager
  - **Change:** `from game.ai.controller import StrategyManager`
  - **To:** `from game.ai.strategy_manager import StrategyManager`

- [ ] `game/ui/panels/ship_stats_renderer.py` - imports StrategyManager
  - **Change:** `from game.ai.controller import StrategyManager`
  - **To:** `from game.ai.strategy_manager import StrategyManager`

- [ ] `game/ui/screens/workshop_data_loader.py` - imports StrategyManager
  - **Change:** `from game.ai.controller import StrategyManager`
  - **To:** `from game.ai.strategy_manager import StrategyManager`

- [ ] `game/ui/screens/workshop_event_router.py` - imports StrategyManager
  - **Change:** `from game.ai.controller import StrategyManager`
  - **To:** `from game.ai.strategy_manager import StrategyManager`

- [ ] `ui/builder/right_panel.py` - imports StrategyManager
  - **Change:** `from game.ai.controller import StrategyManager`
  - **To:** `from game.ai.strategy_manager import StrategyManager`

**Notes:**

---

### Task 3.3: Update Test File Imports [Medium]

**Tests:** `pytest tests/ --testmon`

#### AI Test Files:

- [ ] `tests/unit/ai/test_strategy_manager_singleton.py` - multiple imports
- [ ] `tests/unit/ai/test_strategy_system.py` - imports StrategyManager, TargetEvaluator
- [ ] `tests/unit/ai/test_movement_and_ai.py` - imports StrategyManager

#### Combat Test Files:

- [ ] `tests/unit/combat/test_battle_setup_logic.py` - imports StrategyManager
- [ ] `tests/unit/combat/test_fighter_launch.py` - imports StrategyManager
- [ ] `tests/unit/combat/test_multitarget.py` - imports StrategyManager

#### Builder Test Files:

- [ ] `tests/unit/builder/test_builder_ui_sync.py` - imports StrategyManager

#### UI Test Files:

- [ ] `tests/unit/ui/test_battle_scene_extended.py` - imports StrategyManager

#### Performance Test Files:

- [ ] `tests/unit/performance/strategy_tournament.py` - imports StrategyManager

#### Integration Test Files:

- [ ] `tests/integration/test_ai_strategy.py` - imports TargetEvaluator (may already use direct import)

**Notes:**

---

### Task 3.4: Remove Re-exports from controller.py [Simple]

**File:** `game/ai/controller.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Remove the re-export block (lines 52-61):
  ```python
  # Re-export from strategy_manager for backward compatibility
  from game.ai.strategy_manager import (
      StrategyManager,
      load_combat_strategies,
      get_strategy_names,
      reset_strategy_manager,
  )

  # Re-export TargetEvaluator for backward compatibility
  from game.ai.target_evaluator import TargetEvaluator
  ```

**Notes:**

---

### Task 3.5: Verify No Remaining Usages [Simple]

- [ ] Run verification commands:
  ```bash
  grep -r "from game.ai.controller import StrategyManager" --include="*.py"
  grep -r "from game.ai.controller import get_strategy_names" --include="*.py"
  grep -r "from game.ai.controller import reset_strategy_manager" --include="*.py"
  grep -r "from game.ai.controller import TargetEvaluator" --include="*.py"
  ```
  Expected: No results (only imports of AIController should remain)

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
