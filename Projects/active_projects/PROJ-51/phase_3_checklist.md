# Phase 3: InputHandler Rename (NCA-007)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-51 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
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

- [ ] Create new file `game/ui/screens/battle_input_handler.py`
- [ ] Copy content from `game/core/input_handler.py`
- [ ] Rename class: `InputHandler` -> `BattleInputHandler`
- [ ] Update docstring to clarify battle-specific purpose:
  ```python
  class BattleInputHandler:
      """
      Handles keyboard input for Battle mode.

      Provides static methods for routing keyboard events during battle simulation.
      Manages speed control, pause, and overlay toggles.
      """
  ```
- [ ] Verify: `python -c "from game.ui.screens.battle_input_handler import BattleInputHandler"`

**Notes:** [Filled during implementation]

### Task 3.2: Update app.py Import [Simple]
**File:** `game/app.py`
**Tests:** `python -c "from game.app import Game"`

- [ ] Update import in `game/app.py`:
  - Change: `from game.core.input_handler import InputHandler`
  - To: `from game.ui.screens.battle_input_handler import BattleInputHandler`
- [ ] Update call site in `_handle_keydown()`:
  - Change: `InputHandler.handle_keydown(self, event)`
  - To: `BattleInputHandler.handle_keydown(self, event)`
- [ ] Verify: `python -c "from game.app import Game"`

**Notes:** [Filled during implementation]

### Task 3.3: Update core/__init__.py [Simple]
**File:** `game/core/__init__.py`
**Tests:** `python -c "import game.core"`

- [ ] Check if `game/core/__init__.py` exports `InputHandler`
- [ ] If yes, remove the export (or update to re-export from new location if needed)
- [ ] Verify: `python -c "import game.core"`

**Notes:** [Filled during implementation]

### Task 3.4: Delete Old File [Simple]
**File:** `game/core/input_handler.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Verify no remaining imports: `grep -r "from game.core.input_handler" .`
- [ ] Delete file: `game/core/input_handler.py`
- [ ] Verify: `pytest tests/unit/core/ -v`

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
