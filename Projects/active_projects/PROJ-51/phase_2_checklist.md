# Phase 2: UI File Naming (UI-006)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-51 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Rename `*_scene.py` files to `*_screen.py` to match class names
**Priority:** High

---

## Overview

The class names are already correct (`BattleScreen`, `StrategyScreen`, `TestLabScreen`), but the file names use `*_scene.py`. Additionally, `battle_screen.py` and `strategy_screen.py` already exist with `*Interface` classes.

**Strategy:**
1. First rename `*Interface` classes to `*UI` and their files to `*_ui.py`
2. Then rename `*_scene.py` files to `*_screen.py`

---

## Tasks

### Task 2.1: Rename BattleInterface -> BattleUI [Simple]
**File:** `game/ui/screens/battle_screen.py` -> `game/ui/screens/battle_ui.py`
**Tests:** `pytest tests/unit/ui/test_battle_scene.py -v`

- [ ] Rename class `BattleInterface` to `BattleUI` in `battle_screen.py`
- [ ] Rename file: `battle_screen.py` -> `battle_ui.py`
- [ ] Update import in `game/ui/screens/battle_scene.py`:
  - Change: `from game.ui.screens.battle_screen import BattleInterface`
  - To: `from game.ui.screens.battle_ui import BattleUI`
- [ ] Update reference: `self.ui = BattleInterface(...)` -> `self.ui = BattleUI(...)`
- [ ] Verify: `python -c "from game.ui.screens.battle_ui import BattleUI"`

**Notes:** [Filled during implementation]

### Task 2.2: Rename StrategyInterface -> StrategyUI [Simple]
**File:** `game/ui/screens/strategy_screen.py` -> `game/ui/screens/strategy_ui.py`
**Tests:** `pytest tests/unit/ui/test_empire_asset_loading.py -v`

- [ ] Rename class `StrategyInterface` to `StrategyUI` in `strategy_screen.py`
- [ ] Rename file: `strategy_screen.py` -> `strategy_ui.py`
- [ ] Update import in `game/ui/screens/strategy_scene.py`:
  - Change: `from game.ui.screens.strategy_screen import StrategyInterface`
  - To: `from game.ui.screens.strategy_ui import StrategyUI`
- [ ] Update reference: `self.ui = StrategyInterface(...)` -> `self.ui = StrategyUI(...)`
- [ ] Verify: `python -c "from game.ui.screens.strategy_ui import StrategyUI"`

**Notes:** [Filled during implementation]

### Task 2.3: Rename battle_scene.py -> battle_screen.py [Medium]
**File:** `game/ui/screens/battle_scene.py` -> `game/ui/screens/battle_screen.py`
**Tests:** `pytest tests/unit/ui/test_battle_scene.py tests/unit/ui/test_battle_scene_extended.py -v`

- [ ] Rename file: `battle_scene.py` -> `battle_screen.py`
- [ ] Update `game/app.py` import (~line 130):
  - Change: `from game.ui.screens.battle_scene import BattleScreen`
  - To: `from game.ui.screens.battle_screen import BattleScreen`
- [ ] Update test imports:
  - `tests/unit/ui/test_battle_scene.py`
  - `tests/unit/ui/test_battle_scene_extended.py`
  - `tests/unit/combat/test_battle_setup_logic.py`
  - `tests/unit/combat/test_pdc.py`
  - `tests/unit/ai/test_movement_and_ai.py`
  - `tests/unit/performance/verify_determinism_current.py`
- [ ] Rename test files if appropriate:
  - `test_battle_scene.py` -> `test_battle_screen.py`
  - `test_battle_scene_extended.py` -> `test_battle_screen_extended.py`
- [ ] Verify: `python -c "from game.ui.screens.battle_screen import BattleScreen"`

**Notes:** [Filled during implementation]

### Task 2.4: Rename strategy_scene.py -> strategy_screen.py [Medium]
**File:** `game/ui/screens/strategy_scene.py` -> `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/unit/ui/test_empire_asset_loading.py tests/unit/ui/test_star_color_mapping.py -v`

- [ ] Rename file: `strategy_scene.py` -> `strategy_screen.py`
- [ ] Update `game/app.py` imports (multiple locations):
  - Change: `from game.ui.screens.strategy_scene import StrategyScreen`
  - To: `from game.ui.screens.strategy_screen import StrategyScreen`
- [ ] Update test imports:
  - `tests/unit/ui/test_empire_asset_loading.py`
  - `tests/unit/ui/test_star_color_mapping.py`
- [ ] Check for other imports: `grep -r "from game.ui.screens.strategy_scene" .`
- [ ] Verify: `python -c "from game.ui.screens.strategy_screen import StrategyScreen"`

**Notes:** [Filled during implementation]

### Task 2.5: Rename test_lab_scene.py -> test_lab_screen.py [Simple]
**File:** `game/ui/screens/test_lab_scene.py` -> `game/ui/screens/test_lab_screen.py`
**Tests:** `pytest tests/ -k "test_lab" -v`

- [ ] Rename file: `test_lab_scene.py` -> `test_lab_screen.py`
- [ ] Update `game/app.py` import (~line 133):
  - Change: `from game.ui.screens.test_lab_scene import TestLabScreen`
  - To: `from game.ui.screens.test_lab_screen import TestLabScreen`
- [ ] Check for other imports: `grep -r "from game.ui.screens.test_lab_scene" .`
- [ ] Verify: `python -c "from game.ui.screens.test_lab_screen import TestLabScreen"`

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/unit/ui/ -v` - all UI tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
