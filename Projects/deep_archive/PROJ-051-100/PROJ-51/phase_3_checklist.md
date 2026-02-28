# Phase 3: InputHandler Rename (NCA-007)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-51 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Rename `InputHandler` to `BattleInputHandler` for consistency with `StrategyInputHandler`
**Priority:** High

---

## Overview

The generic `InputHandler` in `game/core/input_handler.py` is actually battle-specific (contains `_handle_battle_keydown()`). It should be renamed to `BattleInputHandler` and moved to `game/ui/screens/` to match the `StrategyInputHandler` pattern.

---

## Tasks

### Task 3.1: Create BattleInputHandler [Simple]
**File:** `game/core/input_handler.py` -> `game/ui/screens/battle_input_handler.py`
**Tests:** `pytest tests/ -k "input" -v`

- [x] Create new file `game/ui/screens/battle_input_handler.py`
- [x] Copy content from `game/core/input_handler.py`
- [x] Rename class: `InputHandler` -> `BattleInputHandler`
- [x] Update docstring to clarify battle-specific purpose:
  ```python
  class BattleInputHandler:
      """
      Handles keyboard input for Battle mode.

      Provides static methods for routing keyboard events during battle simulation.
      Manages speed control, pause, and overlay toggles.
      """
  ```
- [x] Verify: `python -c "from game.ui.screens.battle_input_handler import BattleInputHandler"`

**Notes:** Created new file with updated docstring. Import verified working.

### Task 3.2: Update app.py Import [Simple]
**File:** `game/app.py`
**Tests:** `python -c "from game.app import Game"`

- [x] Update import in `game/app.py`:
  - Change: `from game.core.input_handler import InputHandler`
  - To: `from game.ui.screens.battle_input_handler import BattleInputHandler`
- [x] Update call site in `_handle_keydown()`:
  - Change: `InputHandler.handle_keydown(self, event)`
  - To: `BattleInputHandler.handle_keydown(self, event)`
- [x] Verify: `python -c "from game.app import Game"`

**Notes:** Updated import and call site. Import verified working.

### Task 3.3: Update core/__init__.py [Simple]
**File:** `game/core/__init__.py`
**Tests:** `python -c "import game.core"`

- [x] Check if `game/core/__init__.py` exports `InputHandler`
- [x] If yes, remove the export (or update to re-export from new location if needed)
- [x] Verify: `python -c "import game.core"`

**Notes:** `game/core/__init__.py` does NOT export InputHandler - no changes needed.

### Task 3.4: Delete Old File [Simple]
**File:** `game/core/input_handler.py`
**Tests:** `pytest tests/ --testmon`

- [x] Verify no remaining imports: `grep -r "from game.core.input_handler" .`
- [x] Delete file: `game/core/input_handler.py`
- [x] Verify: `pytest tests/unit/core/ -v`

**Notes:**
- Updated `tests/unit/ui/test_overlay.py` to import from new location
- Also fixed `tests/unit/systems/test_main_integration.py` import of `battle_scene` -> `battle_screen` (Phase 2 residual)
- Old file deleted. 524 core/UI tests passing.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ --testmon` - all affected tests pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
