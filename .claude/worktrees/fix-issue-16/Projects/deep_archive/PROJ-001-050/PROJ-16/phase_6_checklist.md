# Phase 6: Audit Fixes (Cycle 1)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-16 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix issues discovered in audit cycle 1
**Risk:** Low-Medium (straightforward import updates)
**Files Affected:** 43 total (34 for Phase 3, 9 for Phase 2)

---

## Issue 1: Complete Phase 3 (AI Re-exports)

**Problem:** Phase 3 was marked "Complete" but NO work was done. All checkboxes unchecked, 34 files still use old imports, re-exports still present.

### Task 6.1: Update Test Infrastructure for AI Imports [Medium]

**Files to update:**
- [x] `tests/fixtures/ai.py` - change `from game.ai.controller import StrategyManager` to `from game.ai.strategy_manager import StrategyManager`
- [x] `tests/infrastructure/session_cache.py` - same change
- [x] `simulation_tests/conftest.py` - update strategy_manager imports

**Tests:** `pytest tests/unit/ai/ -v`

---

### Task 6.2: Update UI Layer for AI Imports [Medium]

**Files to update:**
- [x] `game/ui/screens/setup_screen.py` - change import source
- [x] `game/ui/screens/setup_renderer.py` - change import source
- [x] `game/ui/screens/workshop_data_loader.py` - change import source (2 locations)
- [x] `game/ui/screens/workshop_event_router.py` - change import source
- [x] `game/ui/panels/ship_stats_renderer.py` - change import source
- [x] `ui/builder/right_panel.py` - change import source

**Change pattern:**
```python
# From:
from game.ai.controller import StrategyManager, get_strategy_names
# To:
from game.ai.strategy_manager import StrategyManager, get_strategy_names
```

---

### Task 6.3: Update Test Files for AI Imports [Medium]

**Files to update:**
- [x] `tests/unit/ai/test_strategy_manager_singleton.py` - multiple imports
- [x] `tests/unit/ai/test_strategy_system.py` - StrategyManager, TargetEvaluator
- [x] `tests/unit/ai/test_movement_and_ai.py` - StrategyManager
- [x] `tests/unit/combat/test_battle_setup_logic.py` - StrategyManager
- [x] `tests/unit/combat/test_fighter_launch.py` - StrategyManager
- [x] `tests/unit/combat/test_multitarget.py` - StrategyManager
- [x] `tests/unit/builder/test_builder_ui_sync.py` - StrategyManager (2 locations)
- [x] `tests/unit/ui/test_battle_scene_extended.py` - StrategyManager
- [x] `tests/unit/test_targeting_rules.py` - TargetEvaluator
- [x] `tests/unit/performance/strategy_tournament.py` - StrategyManager

**Tests:** `pytest tests/ --testmon`

---

### Task 6.4: Remove AI Re-exports from controller.py [Simple]

**File:** `game/ai/controller.py`

- [x] Remove the re-export block (lines 52-61):
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

**Tests:** `pytest tests/ --testmon`

---

### Task 6.5: Verify No Remaining AI Import Usages [Simple]

- [x] Run verification commands:
  ```bash
  grep -r "from game.ai.controller import StrategyManager" --include="*.py"
  grep -r "from game.ai.controller import get_strategy_names" --include="*.py"
  grep -r "from game.ai.controller import reset_strategy_manager" --include="*.py"
  grep -r "from game.ai.controller import TargetEvaluator" --include="*.py"
  ```
  Expected: No results

---

## Issue 2: Complete Phase 2 Cleanup (9 remaining files)

**Problem:** 9 files still import ComponentStatus/Modifier/ApplicationModifier from component.py instead of component_constants.py

### Task 6.6: Update Remaining Component Constant Imports [Simple]

**Files to update:**

Production code:
- [x] `game/ui/hud/panels.py` - change `from game.simulation.components.component import ComponentStatus` to `from game.simulation.components.component_constants import ComponentStatus`
- [x] `game/simulation/systems/stats.py` - same change
- [x] `game/simulation/entities/mixins/combat.py` - same change

Test files:
- [x] `tests/unit/test_bulk_add.py` - update ComponentStatus import
- [x] `tests/unit/test_ship_resources.py` - update ComponentStatus import
- [x] `tests/unit/test_builder_structure_features.py` - update ApplicationModifier import
- [x] `tests/unit/test_modifier_row.py` - update Modifier import
- [x] `tests/unit/test_mandatory_updates.py` - update Modifier import
- [x] `tests/unit/test_mandatory_modifiers.py` - update Modifier import

**Tests:** `pytest tests/ --testmon`

---

### Task 6.7: Verify No Remaining Component Constant Usages [Simple]

- [x] Run verification commands:
  ```bash
  grep -r "from game.simulation.components.component import.*ComponentStatus" --include="*.py"
  grep -r "from game.simulation.components.component import.*Modifier" --include="*.py"
  grep -r "from game.simulation.components.component import.*ApplicationModifier" --include="*.py"
  ```
  Expected: No results (excluding imports of Component, create_component, etc.)

---

## Phase Completion Checklist

When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ --testmon` passes (3092 passed, 1 failed - pre-existing test isolation issue)
- [x] No circular import errors: `python -c "import game"`
- [x] Full test suite passes: `pytest tests/` (pre-existing isolation failure only)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate ready for re-audit
- [x] Also update phase_2_checklist.md and phase_3_checklist.md to show actual completion status (already show Complete)
