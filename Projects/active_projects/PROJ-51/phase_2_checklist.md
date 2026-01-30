# Phase 2: UI File Naming (UI-006)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-51 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
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
**Tests:** `pytest tests/unit/ui/test_battle_screen.py -v`

- [x] Rename class `BattleInterface` to `BattleUI` in `battle_screen.py`
- [x] Rename file: `battle_screen.py` -> `battle_ui.py`
- [x] Update import in `game/ui/screens/battle_scene.py`:
  - Change: `from game.ui.screens.battle_screen import BattleInterface`
  - To: `from game.ui.screens.battle_ui import BattleUI`
- [x] Update reference: `self.ui = BattleInterface(...)` -> `self.ui = BattleUI(...)`
- [x] Verify: `python -c "from game.ui.screens.battle_ui import BattleUI"`

**Notes:** Also updated game/ui/__init__.py exports

### Task 2.2: Rename StrategyInterface -> StrategyUI [Simple]
**File:** `game/ui/screens/strategy_screen.py` -> `game/ui/screens/strategy_ui.py`
**Tests:** `pytest tests/unit/ui/test_empire_asset_loading.py -v`

- [x] Rename class `StrategyInterface` to `StrategyUI` in `strategy_screen.py`
- [x] Rename file: `strategy_screen.py` -> `strategy_ui.py`
- [x] Update import in `game/ui/screens/strategy_scene.py`:
  - Change: `from game.ui.screens.strategy_screen import StrategyInterface`
  - To: `from game.ui.screens.strategy_ui import StrategyUI`
- [x] Update reference: `self.ui = StrategyInterface(...)` -> `self.ui = StrategyUI(...)`
- [x] Verify: `python -c "from game.ui.screens.strategy_ui import StrategyUI"`

**Notes:** Complete

### Task 2.3: Rename battle_scene.py -> battle_screen.py [Medium]
**File:** `game/ui/screens/battle_scene.py` -> `game/ui/screens/battle_screen.py`
**Tests:** `pytest tests/unit/ui/test_battle_screen.py tests/unit/ui/test_battle_screen_extended.py -v`

- [x] Rename file: `battle_scene.py` -> `battle_screen.py`
- [x] Update `game/app.py` import (~line 130):
  - Change: `from game.ui.screens.battle_scene import BattleScreen`
  - To: `from game.ui.screens.battle_screen import BattleScreen`
- [x] Update test imports:
  - `tests/unit/ui/test_battle_screen.py`
  - `tests/unit/ui/test_battle_screen_extended.py`
  - `tests/unit/combat/test_battle_setup_logic.py`
  - `tests/unit/combat/test_pdc.py`
  - `tests/unit/ai/test_movement_and_ai.py`
  - `scripts/verify_determinism_current.py`
- [x] Rename test files if appropriate:
  - `test_battle_scene.py` -> `test_battle_screen.py`
  - `test_battle_scene_extended.py` -> `test_battle_screen_extended.py`
- [x] Verify: `python -c "from game.ui.screens.battle_screen import BattleScreen"`

**Notes:** Also updated game/ui/__init__.py exports and tests/unit/ui/conftest.py pre-imports

### Task 2.4: Rename strategy_scene.py -> strategy_screen.py [Medium]
**File:** `game/ui/screens/strategy_scene.py` -> `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/unit/ui/test_empire_asset_loading.py tests/unit/ui/test_star_color_mapping.py -v`

- [x] Rename file: `strategy_scene.py` -> `strategy_screen.py`
- [x] Update `game/app.py` imports (multiple locations):
  - Change: `from game.ui.screens.strategy_scene import StrategyScreen`
  - To: `from game.ui.screens.strategy_screen import StrategyScreen`
- [x] Update test imports:
  - `tests/unit/ui/test_empire_asset_loading.py`
  - `tests/unit/ui/test_star_color_mapping.py`
  - `tests/integration/ui/test_strategy_buttons.py`
  - `tests/repro_issues/test_bug_16_raw_data_button.py`
  - `scripts/verify_star_scale.py`
- [x] Check for other imports: `grep -r "from game.ui.screens.strategy_scene" .`
- [x] Verify: `python -c "from game.ui.screens.strategy_screen import StrategyScreen"`

**Notes:** Also updated patch paths in test_star_color_mapping.py

### Task 2.5: Rename test_lab_scene.py -> test_lab_screen.py [Simple]
**File:** `game/ui/screens/test_lab_scene.py` -> `game/ui/screens/test_lab_screen.py`
**Tests:** `pytest tests/ -k "test_lab" -v`

- [x] Rename file: `test_lab_scene.py` -> `test_lab_screen.py`
- [x] Update `game/app.py` import (~line 133):
  - Change: `from game.ui.screens.test_lab_scene import TestLabScreen`
  - To: `from game.ui.screens.test_lab_screen import TestLabScreen`
- [x] Check for other imports: `grep -r "from game.ui.screens.test_lab_scene" .`
- [x] Verify: `python -c "from game.ui.screens.test_lab_screen import TestLabScreen"`

**Notes:** Complete

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/unit/ui/ -v` - all UI tests pass (715 passed, 7 pre-existing failures)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
